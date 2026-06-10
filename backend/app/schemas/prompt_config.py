from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.aliases import to_camel


class PromptConfig(BaseModel):
    visual_style: list[str] = Field(default_factory=list)
    color: list[str] = Field(default_factory=list)
    composition: list[str] = Field(default_factory=list)
    copy_tone: list[str] = Field(default_factory=list)
    content: list[str] = Field(default_factory=list)
    platform: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class StyleMemorySelection(BaseModel):
    mode: Literal["none", "user", "company", "brand"] = "none"
    memory_id: str | None = None
    update_after_generation: bool = False

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
