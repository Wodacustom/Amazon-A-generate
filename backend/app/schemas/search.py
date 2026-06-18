"""语义搜索接口模型。"""

from pydantic import BaseModel, Field


class SearchResponseItem(BaseModel):
    """单条搜索结果。"""

    id: str
    source_type: str
    source_id: str
    content: str
    metadata: dict
    score: float | None = None


class SearchResponse(BaseModel):
    """搜索结果列表响应。"""

    items: list[SearchResponseItem]


class SearchQuery(BaseModel):
    """搜索参数校验模型。"""

    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
