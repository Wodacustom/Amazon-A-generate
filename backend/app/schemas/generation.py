from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.aliases import to_camel
from app.schemas.mockup import MockupGenerationPlan
from app.schemas.product import ProductInfo
from app.schemas.prompt_config import PromptConfig, StyleMemorySelection


class CreateGenerationTaskRequest(BaseModel):
    product_id: str | None = None
    images: list[str]
    platform: str
    country: str
    language: str
    quality_level: str
    image_ratio: str | None = None
    image_model: str | None = None
    design_style: str | None = None
    product_info: ProductInfo
    modules: list[str]
    prompt_config: PromptConfig = Field(default_factory=PromptConfig)
    style_memory: StyleMemorySelection = Field(default_factory=StyleMemorySelection)
    mockup_plan: MockupGenerationPlan | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class GenerationTaskResponse(BaseModel):
    id: str
    product_name: str
    status: str
    progress: int
    current_step: str
    created_at: str
    error_message: str | None = None
    conversation_session_id: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class GeneratedModule(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str | None = None
    description: str | None = None
    image_url: str | None = None
    visual_prompt: str | None = None
    layout: str
    sort_order: int

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class GenerationResultResponse(BaseModel):
    id: str
    task_id: str
    product_id: str
    modules: list[GeneratedModule]
    preview_url: str | None = None
    export_urls: dict[str, str] = Field(default_factory=dict)
    quality_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreateResultVersionRequest(BaseModel):
    label: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ResultVersionResponse(BaseModel):
    id: str
    result_id: str
    version: int
    label: str
    created_at: str
    modules: list[GeneratedModule]
    preview_url: str | None = None
    export_urls: dict[str, str] = Field(default_factory=dict)
    quality_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ResultVersionListResponse(BaseModel):
    items: list[ResultVersionResponse]

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
