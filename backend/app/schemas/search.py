from pydantic import BaseModel, Field


class SearchResponseItem(BaseModel):
    id: str
    source_type: str
    source_id: str
    content: str
    metadata: dict
    score: float | None = None


class SearchResponse(BaseModel):
    items: list[SearchResponseItem]


class SearchQuery(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
