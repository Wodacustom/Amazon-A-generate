"""文件接口响应模型。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileAssetRead(BaseModel):
    """文件元数据响应。"""

    id: UUID
    object_key: str
    bucket: str
    original_filename: str | None
    content_type: str | None
    size_bytes: int
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
