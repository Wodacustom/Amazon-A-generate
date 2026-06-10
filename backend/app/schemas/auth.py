from pydantic import BaseModel, ConfigDict, Field

from app.schemas.aliases import to_camel


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6)
    display_name: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class UserProfileResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    role: str = "user"
    plan: str
    credits: int
    status: str
    avatar_url: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreditTransactionResponse(BaseModel):
    id: str
    amount: int
    balance_after: int
    transaction_type: str
    reason: str
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    created_at: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreditAccountResponse(BaseModel):
    balance: int
    lifetime_earned: int
    lifetime_spent: int
    transactions: list[CreditTransactionResponse] = []

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class AdminCreateUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6)
    display_name: str | None = None
    plan: str = "free"
    credits: int = Field(default=0, ge=0)
    role: str = "user"

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class AdminAdjustCreditsRequest(BaseModel):
    user_id: str
    amount: int
    reason: str = "admin_adjustment"

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreditRedemptionCodeResponse(BaseModel):
    id: str
    code: str
    amount: int
    status: str
    note: str | None = None
    created_by_user_id: str | None = None
    redeemed_by_user_id: str | None = None
    redeemed_at: str | None = None
    expires_at: str | None = None
    created_at: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class CreditRedemptionCodeList(BaseModel):
    items: list[CreditRedemptionCodeResponse]

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class AdminCreateCreditCodesRequest(BaseModel):
    amount: int = Field(gt=0)
    count: int = Field(default=1, ge=1, le=200)
    note: str | None = None
    expires_at: str | None = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class RedeemCreditCodeRequest(BaseModel):
    code: str = Field(min_length=4, max_length=64)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class UserListResponse(BaseModel):
    items: list[UserProfileResponse]

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
