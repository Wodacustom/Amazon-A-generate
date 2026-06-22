"""模型调用通用类型。"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.services.model_config import ModelProfileConfig

Message = dict[str, str]


@dataclass(frozen=True)
class ImageFileInput:
    """传给图片模型的二进制图片输入。"""

    filename: str
    data: bytes
    content_type: str | None = None


@dataclass(frozen=True)
class ImageGenerationInput:
    """图片生成/编辑的统一请求。"""

    prompt: str
    size: str = "1024x1024"
    n: int = 1
    image: ImageFileInput | None = None
    mask: ImageFileInput | None = None
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneratedImage:
    """模型供应商返回并已整理成字节的单张图片。"""

    data: bytes
    content_type: str


@dataclass(frozen=True)
class ImageGenerationOutput:
    """图片模型调用结果。"""

    images: list[GeneratedImage]
    operation: str
    usage: dict[str, Any] = field(default_factory=dict)
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class ModelClient(Protocol):
    """统一模型客户端接口。"""

    profile: ModelProfileConfig

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        """执行聊天模型请求。"""

    async def embed_query(self, text: str) -> list[float]:
        """执行单条 embedding 请求。"""

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """执行批量 embedding 请求。"""

    async def generate_image(self, request: ImageGenerationInput) -> ImageGenerationOutput:
        """执行图片生成或图片编辑请求。"""
