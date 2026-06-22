"""模型配置管理接口模型。"""

from pydantic import BaseModel, ConfigDict, Field


class ModelProfileCreate(BaseModel):
    """创建模型档案。"""

    name: str
    model_type: str
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: float = 60.0
    temperature: float | None = None
    dimensions: int | None = None
    config: dict = Field(default_factory=dict)
    enabled: bool = True


class ModelProfileUpdate(BaseModel):
    """更新模型档案。"""

    model_type: str | None = None
    provider: str | None = None
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: float | None = None
    temperature: float | None = None
    dimensions: int | None = None
    config: dict | None = None
    enabled: bool | None = None


class ModelProfileRead(BaseModel):
    """模型档案响应。"""

    id: int
    name: str
    model_type: str
    provider: str
    model: str
    base_url: str | None
    api_key_configured: bool
    masked_api_key: str | None = None
    timeout_seconds: float
    temperature: float | None
    dimensions: int | None
    config: dict
    enabled: bool

    model_config = ConfigDict(from_attributes=True)


class ModelRouteUpsert(BaseModel):
    """创建或更新模型路由。"""

    role: str
    primary_profile_id: int
    fallback_profile_id: int | None = None
    enabled: bool = True


class ModelRouteRead(BaseModel):
    """模型路由响应。"""

    id: int
    role: str
    primary_profile_id: int
    fallback_profile_id: int | None
    enabled: bool

    model_config = ConfigDict(from_attributes=True)


class ModelTemplateUpsert(BaseModel):
    """创建或更新请求模板。"""

    role: str
    name: str
    version: str = "v1"
    system_prompt: str
    user_template: str
    response_contract: str
    enabled: bool = True


class ModelTemplateRead(BaseModel):
    """请求模板响应。"""

    id: int
    role: str
    name: str
    version: str
    system_prompt: str
    user_template: str
    response_contract: str
    enabled: bool

    model_config = ConfigDict(from_attributes=True)
