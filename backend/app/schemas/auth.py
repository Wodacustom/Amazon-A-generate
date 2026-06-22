"""认证接口模型。"""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str | None = None
    email: str | None = None
    password: str


class UserRead(BaseModel):
    """用户信息。"""

    id: int
    username: str
    role: str
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AuthTokenResponse(BaseModel):
    """登录响应。"""

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    user: UserRead

    model_config = ConfigDict(populate_by_name=True)
