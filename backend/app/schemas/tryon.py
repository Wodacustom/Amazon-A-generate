from pydantic import BaseModel, ConfigDict

from app.schemas.aliases import to_camel


class CreateTryonJobRequest(BaseModel):
    product_asset_ids: list[str]
    model_asset_ids: list[str]
    product_image_urls: list[str] = []
    model_image_urls: list[str] = []
    prompt: str = ""
    output_count: int = 1
    ratio: str = "4_5"
    image_model: str | None = None
    mode: str = "fast"
    async_processing: bool = False

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class TryonJobResponse(BaseModel):
    id: str
    status: str
    progress: int
    total_items: int
    completed_items: int
    failed_items: int
    cancelled_items: int
    created_at: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class TryonJobItemResponse(BaseModel):
    id: str
    job_id: str
    product_asset_id: str
    model_asset_id: str
    status: str
    progress: int
    output_image_url: str | None = None
    error_message: str | None = None
    prompt: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class TryonJobItemList(BaseModel):
    items: list[TryonJobItemResponse]
