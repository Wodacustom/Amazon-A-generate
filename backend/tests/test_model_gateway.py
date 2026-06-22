"""模型服务测试。"""

import asyncio

import pytest

from app.core.config import settings
from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models import ModelClientFactory, ModelService
from app.services.models.adapters import NewAPIAdapter, OpenAIAdapter, QwenAdapter, VLLMAdapter
from app.services.models.types import GeneratedImage, ImageFileInput, ImageGenerationInput


def test_mock_model_service_returns_stable_embedding_dimension():
    """验证 mock embedding 维度和配置一致。"""
    service = ModelService()

    first = asyncio.run(service.embed_query("portable grinder"))
    second = asyncio.run(service.embed_query("portable grinder"))

    assert first == second
    assert len(first) == settings.embedding_dimensions == 1536


def test_mock_model_service_parses_chat_json():
    """验证 mock LLM 路径可返回 JSON 对象。"""
    service = ModelService()

    payload = asyncio.run(service.chat_json([{"role": "user", "content": "hello"}]))

    assert payload["summary"] == "Mock model response."
    assert payload["prompt_digest"]


def test_openai_compatible_llm_requires_base_url():
    """真实模型档案缺 base_url 时应给出明确错误。"""
    factory = ModelClientFactory()
    profile = _profile("openai")
    profile = ModelProfileConfig(
        **{
            **profile.__dict__,
            "base_url": None,
        }
    )

    with pytest.raises(ModelConfigurationError, match="base_url"):
        asyncio.run(factory.create(profile).chat_text([{"role": "user", "content": "hello"}]))


def test_model_client_factory_routes_openai_compatible_adapters():
    """验证工厂能创建常见 OpenAI-compatible 厂商 adapter。"""
    factory = ModelClientFactory()

    assert isinstance(factory.create(_profile("qwen")), QwenAdapter)
    assert isinstance(factory.create(_profile("vllm")), VLLMAdapter)
    assert isinstance(factory.create(_profile("newapi")), NewAPIAdapter)


def test_mock_model_service_generates_image():
    """验证空库 fallback 能打通 mock 生图。"""
    service = ModelService()

    output = asyncio.run(service.generate_image(ImageGenerationInput(prompt="product hero")))

    assert output.operation == "generations"
    assert output.images[0].content_type == "image/png"
    assert output.images[0].data


def test_openai_image_generation_uses_generations(monkeypatch):
    """无参考图时应调用 images/generations。"""
    adapter = OpenAIAdapter(_profile("openai", model_type="image"))
    seen = {}

    async def post_image_request(operation, request):
        seen["operation"] = operation

        class Response:
            def json(self):
                return {"data": [{"b64_json": "ignored"}]}

        return Response()

    async def collect_images(payload):
        return [GeneratedImage(data=b"image", content_type="image/png")]

    monkeypatch.setattr(adapter, "_post_image_request", post_image_request)
    monkeypatch.setattr(adapter, "_collect_images", collect_images)

    output = asyncio.run(adapter.generate_image(ImageGenerationInput(prompt="hero")))

    assert seen["operation"] == "generations"
    assert output.operation == "generations"


def test_openai_image_edit_uses_edits(monkeypatch):
    """有参考图时应调用 images/edits。"""
    adapter = OpenAIAdapter(_profile("openai", model_type="image"))
    seen = {}

    async def post_image_request(operation, request):
        seen["operation"] = operation

        class Response:
            def json(self):
                return {"data": [{"b64_json": "ignored"}]}

        return Response()

    async def collect_images(payload):
        return [GeneratedImage(data=b"image", content_type="image/png")]

    monkeypatch.setattr(adapter, "_post_image_request", post_image_request)
    monkeypatch.setattr(adapter, "_collect_images", collect_images)

    output = asyncio.run(
        adapter.generate_image(
            ImageGenerationInput(
                prompt="edit",
                image=ImageFileInput(filename="image.png", data=b"image", content_type="image/png"),
            )
        )
    )

    assert seen["operation"] == "edits"
    assert output.operation == "edits"


def _profile(provider: str, *, model_type: str = "chat") -> ModelProfileConfig:
    return ModelProfileConfig(
        name=f"{provider}_profile",
        model_type=model_type,
        provider=provider,
        model="demo",
        base_url="http://127.0.0.1/v1",
        api_key="secret",
        timeout_seconds=60,
        temperature=0.2,
        dimensions=None,
        config={},
    )
