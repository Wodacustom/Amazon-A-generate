from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthSession, CreditAccount, CreditRedemptionCode, CreditTransaction, User


INITIAL_FREE_CREDITS = 100


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)


async def create_user_account(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
    *,
    role: str = "user",
    plan: str = "free",
    initial_credits: int = INITIAL_FREE_CREDITS,
) -> tuple[User, AuthSession]:
    user = await create_user_without_session(
        session,
        email,
        password,
        display_name,
        role=role,
        plan=plan,
        initial_credits=initial_credits,
    )
    auth_session = create_auth_session(user)
    session.add(auth_session)
    await session.commit()
    await session.refresh(user)
    return user, auth_session


async def create_public_user_account(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
) -> tuple[User, AuthSession]:
    user_count = await session.scalar(select(func.count()).select_from(User))
    role = "admin" if not user_count else "user"
    return await create_user_account(
        session,
        email,
        password,
        display_name,
        role=role,
        plan="admin" if role == "admin" else "free",
        initial_credits=INITIAL_FREE_CREDITS,
    )


async def create_user_without_session(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
    *,
    role: str = "user",
    plan: str = "free",
    initial_credits: int = 0,
) -> User:
    normalized_email = normalize_email(email)
    existing = await session.scalar(select(User).where(User.email == normalized_email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        display_name=display_name or normalized_email.split("@", 1)[0],
        role=role,
        plan=plan,
        credits=initial_credits,
    )
    session.add(user)
    await session.flush()

    credit_account = CreditAccount(
        user_id=user.id,
        balance=initial_credits,
        lifetime_earned=initial_credits,
        lifetime_spent=0,
    )
    session.add(credit_account)
    await session.flush()

    if initial_credits:
        session.add(
            CreditTransaction(
                account_id=credit_account.id,
                user_id=user.id,
                amount=initial_credits,
                balance_after=initial_credits,
                transaction_type="grant",
                reason="initial_credits",
            )
        )
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> tuple[User, AuthSession]:
    user = await session.scalar(select(User).where(User.email == normalize_email(email)))
    if not user or user.status != "active" or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user.last_login_at = datetime.now(UTC)
    auth_session = create_auth_session(user)
    session.add(auth_session)
    await session.commit()
    await session.refresh(user)
    return user, auth_session


async def get_user_by_token(session: AsyncSession, access_token: str) -> User:
    auth_session = await session.scalar(
        select(AuthSession).where(AuthSession.access_token == access_token, AuthSession.status == "active")
    )
    if not auth_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    user = await session.get(User, auth_session.user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return user


async def require_admin(session: AsyncSession, access_token: str) -> User:
    user = await get_user_by_token(session, access_token)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")
    return user


async def get_credit_account(session: AsyncSession, user_id: UUID) -> tuple[CreditAccount, list[CreditTransaction]]:
    account = await ensure_credit_account(session, user_id)
    transactions = (
        (
            await session.execute(
                select(CreditTransaction)
                .where(CreditTransaction.account_id == account.id)
                .order_by(CreditTransaction.created_at.desc())
                .limit(50)
            )
        )
        .scalars()
        .all()
    )
    return account, list(transactions)


async def ensure_credit_account(session: AsyncSession, user_id: UUID) -> CreditAccount:
    account = await session.scalar(select(CreditAccount).where(CreditAccount.user_id == user_id))
    if account:
        return account
    account = CreditAccount(user_id=user_id, balance=0, lifetime_earned=0, lifetime_spent=0)
    session.add(account)
    await session.flush()
    return account


async def list_users(session: AsyncSession) -> list[User]:
    return list((await session.execute(select(User).order_by(User.created_at.desc()))).scalars().all())


async def adjust_user_credits(
    session: AsyncSession,
    user_id: UUID,
    amount: int,
    reason: str,
    *,
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
) -> tuple[User, CreditAccount, CreditTransaction]:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    account = await ensure_credit_account(session, user.id)
    next_balance = account.balance + amount
    if next_balance < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credits")

    account.balance = next_balance
    if amount >= 0:
        account.lifetime_earned += amount
    else:
        account.lifetime_spent += abs(amount)
    user.credits = account.balance

    transaction = CreditTransaction(
        account_id=account.id,
        user_id=user.id,
        amount=amount,
        balance_after=account.balance,
        transaction_type="grant" if amount >= 0 else "deduct",
        reason=reason,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(user)
    await session.refresh(account)
    await session.refresh(transaction)
    return user, account, transaction


async def create_redemption_codes(
    session: AsyncSession,
    admin_user_id: UUID,
    amount: int,
    count: int,
    note: str | None = None,
    expires_at: datetime | None = None,
) -> list[CreditRedemptionCode]:
    codes: list[CreditRedemptionCode] = []
    for _ in range(count):
        code = CreditRedemptionCode(
            code=generate_redemption_code(),
            amount=amount,
            status="unused",
            note=note,
            created_by_user_id=admin_user_id,
            expires_at=expires_at,
        )
        session.add(code)
        codes.append(code)
    await session.commit()
    for code in codes:
        await session.refresh(code)
    return codes


async def list_redemption_codes(session: AsyncSession) -> list[CreditRedemptionCode]:
    return list(
        (
            await session.execute(
                select(CreditRedemptionCode).order_by(CreditRedemptionCode.created_at.desc()).limit(200)
            )
        )
        .scalars()
        .all()
    )


async def redeem_credit_code(session: AsyncSession, user: User, code_value: str) -> tuple[CreditAccount, CreditTransaction]:
    code = await session.scalar(select(CreditRedemptionCode).where(CreditRedemptionCode.code == code_value.strip()))
    if not code or code.status != "unused":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or used redemption code")
    if code.expires_at and code.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Redemption code expired")

    code.status = "redeemed"
    code.redeemed_by_user_id = user.id
    code.redeemed_at = datetime.now(UTC)
    _user, account, transaction = await adjust_user_credits(
        session,
        user.id,
        code.amount,
        "redeem_code",
        related_entity_type="credit_redemption_code",
        related_entity_id=str(code.id),
    )
    return account, transaction


def create_auth_session(user: User) -> AuthSession:
    return AuthSession(user_id=user.id, access_token=secrets.token_urlsafe(32), token_type="bearer")


def generate_redemption_code() -> str:
    token = secrets.token_urlsafe(18).replace("-", "").replace("_", "").upper()
    return f"AP{token[:18]}"


def user_to_profile(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "displayName": user.display_name,
        "role": user.role,
        "plan": user.plan,
        "credits": user.credits,
        "status": user.status,
        "avatarUrl": user.avatar_url,
    }


def code_to_response(code: CreditRedemptionCode) -> dict:
    return {
        "id": str(code.id),
        "code": code.code,
        "amount": code.amount,
        "status": code.status,
        "note": code.note,
        "createdByUserId": str(code.created_by_user_id) if code.created_by_user_id else None,
        "redeemedByUserId": str(code.redeemed_by_user_id) if code.redeemed_by_user_id else None,
        "redeemedAt": code.redeemed_at.isoformat() if code.redeemed_at else None,
        "expiresAt": code.expires_at.isoformat() if code.expires_at else None,
        "createdAt": code.created_at.isoformat() if code.created_at else None,
    }
