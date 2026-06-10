from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.services.file_storage import storage_dir


class GeminiImageGenerationClient:
    def generate_module_image(
        self,
        prompt: str,
        module_type: str,
        image_ratio: str | None,
        product_image_urls: list[str],
        mockup_image_url: str | None = None,
        image_model: str | None = None,
    ) -> str | None:
        if not settings.gemini_api_key or not prompt:
            return None

        image_bytes, mime_type = self._generate_image(
            prompt,
            module_type,
            image_ratio,
            product_image_urls,
            mockup_image_url,
            image_model,
        )
        extension = self._extension_from_mime(mime_type)
        output_dir = storage_dir("generated")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4()}.{extension}"
        (output_dir / filename).write_bytes(image_bytes)
        return f"/api/files/generated/{filename}"

    def _generate_image(
        self,
        prompt: str,
        module_type: str,
        image_ratio: str | None,
        product_image_urls: list[str],
        mockup_image_url: str | None,
        image_model: str | None,
    ) -> tuple[bytes, str]:
        model = self._resolve_model(image_model).strip().removeprefix("models/")
        url = f"{settings.gemini_base_url.rstrip('/')}/models/{model}:generateContent"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": self._build_parts(prompt, module_type, image_ratio, product_image_urls, mockup_image_url),
                }
            ],
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key.get_secret_value(),
        }

        with httpx.Client(timeout=settings.gemini_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            inline_data = part.get("inlineData") or part.get("inline_data")
            if inline_data and inline_data.get("data"):
                mime_type = inline_data.get("mimeType") or inline_data.get("mime_type") or "image/png"
                return base64.b64decode(inline_data["data"]), mime_type
        raise ValueError("Gemini image response did not include image data")

    def _build_parts(
        self,
        prompt: str,
        module_type: str,
        image_ratio: str | None,
        product_image_urls: list[str],
        mockup_image_url: str | None = None,
    ) -> list[dict]:
        parts = [{"text": self._build_prompt(prompt, module_type, image_ratio, product_image_urls, mockup_image_url)}]
        for image_url in product_image_urls[:3]:
            image_part = self._image_part_from_url(image_url)
            if image_part:
                parts.append(image_part)
        if mockup_image_url:
            mockup_part = self._image_part_from_url(mockup_image_url)
            if mockup_part:
                parts.append(mockup_part)
        return parts

    def _image_part_from_url(self, image_url: str) -> dict | None:
        path = self._local_image_path(image_url)
        if not path or not path.exists() or not path.is_file():
            return None
        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        if not mime_type.startswith("image/"):
            return None
        return {
            "inlineData": {
                "mimeType": mime_type,
                "data": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
        }

    def _local_image_path(self, image_url: str) -> Path | None:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        prefixes = {
            "/api/files/uploads/": storage_dir("uploads"),
            "/api/files/generated/": storage_dir("generated"),
            "/api/files/garment-library/": storage_dir("garment-library"),
        }
        for prefix, directory in prefixes.items():
            if path.startswith(prefix):
                filename = path.removeprefix(prefix)
                if "/" in filename or "\\" in filename or not filename:
                    return None
                return directory / filename
        return None

    def _build_prompt(
        self,
        prompt: str,
        module_type: str,
        image_ratio: str | None,
        product_image_urls: list[str],
        mockup_image_url: str | None = None,
    ) -> str:
        references = "\n".join(f"- {url}" for url in product_image_urls[:3]) or "- no reference image provided"
        mockup_reference = mockup_image_url or "no mockup image provided"
        return (
            "Create a clean ecommerce Amazon A+ module image.\n"
            f"Module type: {module_type}\n"
            f"Target aspect ratio: {self._aspect_ratio(image_ratio)}\n"
            f"Target canvas size: {self._target_size(image_ratio)}\n"
            f"Visual prompt: {prompt}\n"
            "Requirements: realistic commercial product photography, product as the clear focus, no distorted logo, "
            "text-safe composition, no unreadable text, no exaggerated claims.\n"
            "Use attached product reference images as the product identity reference. Preserve the user's product shape, "
            "logo, label text, packaging details, colors, and proportions.\n"
            "If a mockup reference image is attached, use it as the scene/template reference and replace the product shown "
            "in that mockup with the user's product while matching perspective, lighting, contact shadow, reflections, and depth of field.\n"
            f"Product reference URLs:\n{references}\n"
            f"Mockup reference URL: {mockup_reference}"
        )

    def _aspect_ratio(self, image_ratio: str | None) -> str:
        mapping = {
            "1_1": "1:1",
            "2_3": "2:3",
            "3_4": "3:4",
            "4_5": "4:5",
            "9_16": "9:16",
            "16_9": "16:9",
            "platform_default": "16:9",
        }
        parsed = self._parse_ratio(image_ratio)
        return parsed or mapping.get(image_ratio or "", "16:9")

    def _target_size(self, image_ratio: str | None) -> str:
        mapping = {
            "1_1": "1600x1600 px",
            "2_3": "1600x2400 px",
            "3_4": "1600x2133 px",
            "4_5": "1600x2000 px",
            "9_16": "1440x2560 px",
            "16_9": "1600x900 px",
            "platform_default": "1600x900 px",
        }
        parsed = self._parse_ratio(image_ratio)
        if parsed:
            width, height = [int(part) for part in parsed.split(":")]
            if width <= height:
                target_width = 1600
                target_height = round(target_width * height / width)
            else:
                target_width = 1600
                target_height = round(target_width * height / width)
            return f"{target_width}x{target_height} px"
        return mapping.get(image_ratio or "", "1600x900 px")

    def _parse_ratio(self, image_ratio: str | None) -> str | None:
        if not image_ratio:
            return None
        parts = image_ratio.split("_")
        if len(parts) == 3 and parts[0] == "model" and parts[1].isdigit() and parts[2].isdigit():
            return f"{int(parts[1])}:{int(parts[2])}"
        return None

    def _extension_from_mime(self, mime_type: str) -> str:
        if mime_type == "image/jpeg":
            return "jpg"
        if mime_type == "image/webp":
            return "webp"
        return "png"

    def _resolve_model(self, image_model: str | None) -> str:
        model_key = image_model or settings.default_image_model
        mapping = {
            "nanobanana_pro": settings.gemini_image_model,
            "gemini_3_pro_image": settings.gemini_image_model,
        }
        return mapping.get(model_key, settings.gemini_image_model)
