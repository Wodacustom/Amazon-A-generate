"""OpenAI-compatible 厂商适配器。"""

import base64
from collections.abc import Sequence
from typing import Any

import httpx

from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models.types import GeneratedImage, ImageGenerationInput, ImageGenerationOutput, Message


class OpenAIAdapter:
    """OpenAI-compatible 模型客户端。"""

    provider_name = "openai"

    def __init__(self, profile: ModelProfileConfig) -> None:
        self.profile = profile

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        if not self.profile.base_url:
            raise ModelConfigurationError(f"{self.profile.name} requires base_url.")
        if not self.profile.api_key:
            raise ModelConfigurationError(f"{self.profile.name} requires api_key.")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ModelConfigurationError("langchain-openai is required for OpenAI-compatible chat.") from exc
        model = ChatOpenAI(
            model=self.profile.model,
            api_key=self.profile.api_key,
            base_url=self.profile.base_url,
            timeout=self.profile.timeout_seconds,
            temperature=self.profile.temperature if temperature is None else temperature,
        )
        response = await model.ainvoke([(message["role"], message["content"]) for message in messages])
        return str(response.content)

    async def embed_query(self, text: str) -> list[float]:
        return list(await self._embedding_model().aembed_query(text))

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [list(vector) for vector in await self._embedding_model().aembed_documents(list(texts))]

    async def generate_image(self, request: ImageGenerationInput) -> ImageGenerationOutput:
        """按 OpenAI 图片协议生成或编辑图片。"""
        if not self.profile.base_url:
            raise ModelConfigurationError(f"{self.profile.name} requires base_url.")
        if not self.profile.api_key:
            raise ModelConfigurationError(f"{self.profile.name} requires api_key.")
        operation = "edits" if request.image else "generations"
        response = await self._post_image_request(operation, request)
        payload = response.json()
        images = await self._collect_images(payload)
        return ImageGenerationOutput(
            images=images,
            operation=operation,
            usage=payload.get("usage") or {},
            raw_metadata={"created": payload.get("created"), "provider": self.provider_name, "model": self.profile.model},
        )

    def _embedding_model(self) -> Any:
        if not self.profile.base_url:
            raise ModelConfigurationError(f"{self.profile.name} requires base_url.")
        if not self.profile.api_key:
            raise ModelConfigurationError(f"{self.profile.name} requires api_key.")
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError as exc:
            raise ModelConfigurationError("langchain-openai is required for OpenAI-compatible embedding.") from exc
        return OpenAIEmbeddings(
            model=self.profile.model,
            api_key=self.profile.api_key,
            base_url=self.profile.base_url,
            dimensions=self.profile.dimensions,
        )

    async def _post_image_request(self, operation: str, request: ImageGenerationInput) -> httpx.Response:
        url = f"{self.profile.base_url.rstrip('/')}/images/{operation}"
        headers = {"Authorization": f"Bearer {self.profile.api_key}"}
        timeout = httpx.Timeout(self.profile.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if operation == "generations":
                response = await client.post(
                    url,
                    headers=headers,
                    json=self._generation_payload(request),
                )
            else:
                response = await client.post(
                    url,
                    headers=headers,
                    data=self._edit_data(request),
                    files=self._edit_files(request),
                )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ModelConfigurationError(
                f"{self.profile.name} image request failed: {response.status_code} {response.text[:500]}"
            ) from exc
        return response

    def _generation_payload(self, request: ImageGenerationInput) -> dict[str, Any]:
        payload = {
            "model": self.profile.model,
            "prompt": request.prompt,
            "n": request.n,
            "size": request.size,
        }
        payload.update(request.options)
        return {key: value for key, value in payload.items() if value is not None}

    def _edit_data(self, request: ImageGenerationInput) -> dict[str, str]:
        payload = self._generation_payload(request)
        payload.pop("image", None)
        payload.pop("mask", None)
        return {key: str(value) for key, value in payload.items() if value is not None}

    def _edit_files(self, request: ImageGenerationInput) -> dict[str, tuple[str, bytes, str]]:
        if request.image is None:
            raise ModelConfigurationError("image is required for image edits.")
        files = {
            "image": (
                request.image.filename,
                request.image.data,
                request.image.content_type or "application/octet-stream",
            )
        }
        if request.mask is not None:
            files["mask"] = (
                request.mask.filename,
                request.mask.data,
                request.mask.content_type or "application/octet-stream",
            )
        return files

    async def _collect_images(self, payload: dict[str, Any]) -> list[GeneratedImage]:
        items = payload.get("data") or []
        if not isinstance(items, list) or not items:
            raise ModelConfigurationError(f"{self.profile.name} returned no image data.")
        images = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("b64_json"):
                images.append(GeneratedImage(data=base64.b64decode(item["b64_json"]), content_type="image/png"))
            elif item.get("url"):
                images.append(await self._download_provider_image(item["url"]))
        if not images:
            raise ModelConfigurationError(f"{self.profile.name} returned unsupported image payload.")
        return images

    async def _download_provider_image(self, url: str) -> GeneratedImage:
        async with httpx.AsyncClient(timeout=httpx.Timeout(self.profile.timeout_seconds)) as client:
            response = await client.get(url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ModelConfigurationError(
                f"{self.profile.name} provider image download failed: {response.status_code}"
            ) from exc
        content_type = response.headers.get("content-type") or "image/png"
        return GeneratedImage(data=response.content, content_type=content_type.split(";")[0])


class QwenAdapter(OpenAIAdapter):
    """通义千问 OpenAI-compatible 适配器。"""

    provider_name = "qwen"


class VLLMAdapter(OpenAIAdapter):
    """vLLM OpenAI-compatible 适配器。"""

    provider_name = "vllm"


class NewAPIAdapter(OpenAIAdapter):
    """NewAPI OpenAI-compatible 适配器。"""

    provider_name = "newapi"
