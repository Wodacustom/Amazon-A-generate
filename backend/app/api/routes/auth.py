from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    AdminAdjustCreditsRequest,
    AdminCreateCreditCodesRequest,
    AdminCreateUserRequest,
    AuthTokenResponse,
    CreditAccountResponse,
    CreditRedemptionCodeList,
    LoginRequest,
    RedeemCreditCodeRequest,
    RegisterRequest,
    UserListResponse,
    UserProfileResponse,
)
from app.services.auth_accounts import (
    adjust_user_credits,
    authenticate_user,
    code_to_response,
    create_public_user_account,
    create_redemption_codes,
    create_user_without_session,
    get_credit_account,
    get_user_by_token,
    list_redemption_codes,
    list_users,
    redeem_credit_code,
    require_admin,
    user_to_profile,
)

router = APIRouter()


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)) -> dict:
    user, auth_session = await create_public_user_account(session, payload.email, payload.password, payload.display_name)
    return {"accessToken": auth_session.access_token, "tokenType": auth_session.token_type, "user": user_to_profile(user)}


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> dict:
    user, auth_session = await authenticate_user(session, payload.email, payload.password)
    return {"accessToken": auth_session.access_token, "tokenType": auth_session.token_type, "user": user_to_profile(user)}


@router.get("/me", response_model=UserProfileResponse)
async def me(authorization: str | None = Header(default=None), session: AsyncSession = Depends(get_db)) -> dict:
    user = await _current_user(authorization, session)
    return user_to_profile(user)


@router.get("/credits", response_model=CreditAccountResponse)
async def credits(authorization: str | None = Header(default=None), session: AsyncSession = Depends(get_db)) -> dict:
    user = await _current_user(authorization, session)
    return await _credit_account_response(session, user.id)


@router.post("/credits/redeem", response_model=CreditAccountResponse)
async def redeem_credits(
    payload: RedeemCreditCodeRequest,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    user = await _current_user(authorization, session)
    await redeem_credit_code(session, user, payload.code)
    return await _credit_account_response(session, user.id)


@router.get("/admin/users", response_model=UserListResponse)
async def admin_users(authorization: str | None = Header(default=None), session: AsyncSession = Depends(get_db)) -> dict:
    await _admin_user(authorization, session)
    return {"items": [user_to_profile(user) for user in await list_users(session)]}


@router.post("/admin/users", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    payload: AdminCreateUserRequest,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await _admin_user(authorization, session)
    user = await create_user_without_session(
        session,
        payload.email,
        payload.password,
        payload.display_name,
        role=payload.role,
        plan=payload.plan,
        initial_credits=payload.credits,
    )
    await session.commit()
    await session.refresh(user)
    return user_to_profile(user)


@router.post("/admin/credits/adjust", response_model=CreditAccountResponse)
async def admin_adjust_credits(
    payload: AdminAdjustCreditsRequest,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await _admin_user(authorization, session)
    await adjust_user_credits(session, UUID(payload.user_id), payload.amount, payload.reason)
    return await _credit_account_response(session, UUID(payload.user_id))


@router.get("/admin/credit-codes", response_model=CreditRedemptionCodeList)
async def admin_credit_codes(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await _admin_user(authorization, session)
    return {"items": [code_to_response(code) for code in await list_redemption_codes(session)]}


@router.post("/admin/credit-codes", response_model=CreditRedemptionCodeList, status_code=status.HTTP_201_CREATED)
async def admin_create_credit_codes(
    payload: AdminCreateCreditCodesRequest,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    admin = await _admin_user(authorization, session)
    expires_at = datetime.fromisoformat(payload.expires_at) if payload.expires_at else None
    codes = await create_redemption_codes(session, admin.id, payload.amount, payload.count, payload.note, expires_at)
    return {"items": [code_to_response(code) for code in codes]}


async def _current_user(authorization: str | None, session: AsyncSession):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return await get_user_by_token(session, authorization.split(" ", 1)[1])


async def _admin_user(authorization: str | None, session: AsyncSession):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return await require_admin(session, authorization.split(" ", 1)[1])


async def _credit_account_response(session: AsyncSession, user_id: UUID) -> dict:
    account, transactions = await get_credit_account(session, user_id)
    return {
        "balance": account.balance,
        "lifetimeEarned": account.lifetime_earned,
        "lifetimeSpent": account.lifetime_spent,
        "transactions": [
            {
                "id": str(item.id),
                "amount": item.amount,
                "balanceAfter": item.balance_after,
                "transactionType": item.transaction_type,
                "reason": item.reason,
                "relatedEntityType": item.related_entity_type,
                "relatedEntityId": item.related_entity_id,
                "createdAt": item.created_at.isoformat(),
            }
            for item in transactions
        ],
    }
