from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    platform: str = "amazon"
    country: str = "US"
    language: str = "zh-CN"
    selling_points: list[str] = Field(default_factory=list)
    specs: dict = Field(default_factory=dict)
    description: str | None = None
    file_ids: list[str] = Field(default_factory=list)


class ProductRead(ProductCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
