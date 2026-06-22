"""本地 mock 模型适配器。"""

import hashlib
import json
import math
from base64 import b64decode
from collections.abc import Sequence

from app.core.config import settings
from app.services.model_config import ModelProfileConfig
from app.services.models.types import GeneratedImage, ImageGenerationInput, ImageGenerationOutput, Message


MOCK_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class MockAdapter:
    """本地 mock 模型客户端。"""

    def __init__(self, profile: ModelProfileConfig) -> None:
        self.profile = profile

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        prompt = "\n".join(message.get("content", "") for message in messages)
        if "content_modules" in prompt:
            return json.dumps(
                {
                    "content_modules": [
                        {
                            "type": "hero",
                            "title": "Mock Product Built for Everyday Confidence",
                            "subtitle": "A clean Amazon A+ hero draft.",
                            "body": "Highlight the product clearly with concise, compliant copy.",
                        },
                        {"type": "benefits", "title": "Key Benefits", "items": ["Reliable quality"]},
                        {"type": "details", "title": "Product Details", "items": {}},
                    ]
                }
            )
        if "image_prompts" in prompt:
            return json.dumps(
                {
                    "image_prompts": [
                        {
                            "module_type": "hero",
                            "prompt": "Amazon A+ module image, clean commercial product photography.",
                        }
                    ]
                }
            )
        return json.dumps(
            {
                "summary": "Mock model response.",
                "prompt_digest": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12],
            }
        )

    async def embed_query(self, text: str) -> list[float]:
        return self._mock_embedding(text)

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._mock_embedding(text) for text in texts]

    async def generate_image(self, request: ImageGenerationInput) -> ImageGenerationOutput:
        """返回一张固定 PNG，供本地无真实模型时测试完整链路。"""
        operation = "edits" if request.image else "generations"
        count = max(1, min(request.n, 10))
        return ImageGenerationOutput(
            images=[GeneratedImage(data=b64decode(MOCK_PNG), content_type="image/png") for _ in range(count)],
            operation=operation,
            usage={"mock": True},
            raw_metadata={"provider": "mock", "model": self.profile.model},
        )

    def _mock_embedding(self, text: str) -> list[float]:
        dimensions = self.profile.dimensions or settings.embedding_dimensions
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(dimensions):
            byte = digest[index % len(digest)]
            values.append((byte / 127.5) - 1.0)
        length = math.sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / length, 6) for value in values]
