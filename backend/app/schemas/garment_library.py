from pydantic import BaseModel, ConfigDict

from app.schemas.aliases import to_camel


class GarmentLibraryItem(BaseModel):
    id: str
    name: str
    filename: str
    content_type: str | None = None
    url: str
    storage_key: str
    tags: list[str] = []
    created_at: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class GarmentLibraryList(BaseModel):
    items: list[GarmentLibraryItem]

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
