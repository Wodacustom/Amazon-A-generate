"""图片生成接口响应模型。"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class GeneratedImageRead(BaseModel):
    """单张生成图片响应。"""

    file_id: UUID
    image_url: str
    expires_in: int
    provider: str
    model: str
    operation: str


class ImageGenerationRead(BaseModel):
    """图片生成响应。"""

    items: list[GeneratedImageRead]
    usage: dict[str, Any]
    metadata: dict[str, Any]
