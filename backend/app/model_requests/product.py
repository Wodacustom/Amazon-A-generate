"""产品 A+ 生成相关模型请求契约。"""

import json
from typing import Any

from pydantic import BaseModel, Field


class APlusContentRequest(BaseModel):
    """A+ 内容生成上下文。"""

    product: dict[str, Any]
    analysis: dict[str, Any]
    retrieved_context: list[dict[str, Any]] = Field(default_factory=list)
    required_module_types: list[str] = Field(default_factory=lambda: ["hero", "benefits", "details"])

    def variables(self) -> dict[str, str]:
        return {"payload": json.dumps(self.model_dump(), ensure_ascii=False)}


class APlusContentResponse(BaseModel):
    """A+ 内容生成响应。"""

    content_modules: list[dict[str, Any]]


class ImagePromptRequest(BaseModel):
    """图片提示词生成上下文。"""

    product: dict[str, Any]
    content_modules: list[dict[str, Any]]

    def variables(self) -> dict[str, str]:
        return {"payload": json.dumps(self.model_dump(), ensure_ascii=False)}


class ImagePromptResponse(BaseModel):
    """图片提示词生成响应。"""

    image_prompts: list[dict[str, Any]]
