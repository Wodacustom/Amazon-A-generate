"""智能体接口的请求和响应模型。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentRunCreate(BaseModel):
    """创建智能体运行的请求体。"""

    product_id: UUID | None = None
    product_input: dict = Field(default_factory=dict)


class AgentResultRead(BaseModel):
    """智能体结果响应。"""

    id: UUID
    run_id: UUID
    product_id: UUID | None
    content_modules: list[dict]
    image_prompts: list[dict]
    model_metadata: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunRead(BaseModel):
    """智能体运行状态响应。"""

    id: UUID
    product_id: UUID | None
    status: str
    progress: int
    current_step: str | None
    input_snapshot: dict
    error_message: str | None
    result: AgentResultRead | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
