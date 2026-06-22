"""模型配置管理接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.model_config import ModelConfigAuditLog, ModelProfile, ModelRequestTemplate, ModelRoute
from app.schemas.model_config import (
    ModelProfileCreate,
    ModelProfileRead,
    ModelProfileUpdate,
    ModelRouteRead,
    ModelRouteUpsert,
    ModelTemplateRead,
    ModelTemplateUpsert,
)
from app.services.security import decrypt_secret, encrypt_secret, mask_secret

router = APIRouter()
logger = get_logger(__name__)


@router.get("/profiles", response_model=dict)
async def list_profiles(db: AsyncSession = Depends(get_db)) -> dict:
    """列出模型档案。"""
    result = await db.execute(select(ModelProfile).where(ModelProfile.deleted == 0).order_by(ModelProfile.id))
    return {"items": [_profile_read(profile) for profile in result.scalars()]}


@router.post("/profiles", response_model=ModelProfileRead, status_code=201)
async def create_profile(
    payload: ModelProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ModelProfileRead:
    """创建模型档案。"""
    # API key 只在写入时接收，入库前加密；响应由 _profile_read 统一脱敏。
    profile = ModelProfile(
        name=payload.name,
        model_type=payload.model_type,
        provider=payload.provider,
        model=payload.model,
        base_url=payload.base_url,
        encrypted_api_key=encrypt_secret(payload.api_key) if payload.api_key else None,
        timeout_seconds=payload.timeout_seconds,
        temperature=payload.temperature,
        dimensions=payload.dimensions,
        config=payload.config,
        enabled=payload.enabled,
    )
    db.add(profile)
    await db.flush()
    await _audit(db, "create_profile", "model_profile", str(profile.id), {"name": profile.name})
    await db.commit()
    await db.refresh(profile)
    logger.info(
        "model_config.profile.created",
        extra={
            "event": "model_config.profile.created",
            "profile_id": profile.id,
            "profile_name": profile.name,
            "model_type": profile.model_type,
            "provider": profile.provider,
            "api_key_configured": bool(profile.encrypted_api_key),
        },
    )
    return _profile_read(profile)


@router.patch("/profiles/{profile_id}", response_model=ModelProfileRead)
async def update_profile(
    profile_id: int,
    payload: ModelProfileUpdate,
    db: AsyncSession = Depends(get_db),
) -> ModelProfileRead:
    """更新模型档案。"""
    profile = await db.get(ModelProfile, profile_id)
    if profile is None or profile.deleted:
        raise HTTPException(status_code=404, detail="Model profile not found.")
    updates = payload.model_dump(exclude_unset=True)
    api_key = updates.pop("api_key", None)
    for key, value in updates.items():
        setattr(profile, key, value)
    if api_key:
        # 空 api_key 表示不改密钥；传入新值才覆盖加密字段。
        profile.encrypted_api_key = encrypt_secret(api_key)
    await _audit(db, "update_profile", "model_profile", str(profile.id), {"name": profile.name})
    await db.commit()
    await db.refresh(profile)
    logger.info(
        "model_config.profile.updated",
        extra={
            "event": "model_config.profile.updated",
            "profile_id": profile.id,
            "profile_name": profile.name,
            "model_type": profile.model_type,
            "provider": profile.provider,
            "updated_fields": list(updates.keys()) + (["api_key"] if api_key else []),
        },
    )
    return _profile_read(profile)


@router.delete("/profiles/{profile_id}", response_model=dict)
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """逻辑删除模型档案。"""
    profile = await db.get(ModelProfile, profile_id)
    if profile is None or profile.deleted:
        raise HTTPException(status_code=404, detail="Model profile not found.")
    # 只标记 deleted，保留历史配置和审计链路；同时禁用，避免被路由继续调用。
    profile.deleted = 1
    profile.enabled = False
    await _audit(db, "delete_profile", "model_profile", str(profile.id), {"name": profile.name})
    await db.commit()
    logger.info(
        "model_config.profile.deleted",
        extra={"event": "model_config.profile.deleted", "profile_id": profile.id, "profile_name": profile.name},
    )
    return {"ok": True}


@router.get("/routes", response_model=dict)
async def list_routes(db: AsyncSession = Depends(get_db)) -> dict:
    """列出模型路由。"""
    result = await db.execute(select(ModelRoute).where(ModelRoute.deleted == 0).order_by(ModelRoute.id))
    return {"items": list(result.scalars())}


@router.post("/routes", response_model=ModelRouteRead, status_code=201)
async def upsert_route(
    payload: ModelRouteUpsert,
    db: AsyncSession = Depends(get_db),
) -> ModelRoute:
    """创建或更新模型路由。"""
    result = await db.execute(select(ModelRoute).where(ModelRoute.role == payload.role, ModelRoute.deleted == 0))
    route = result.scalar_one_or_none()
    if route is None:
        route = ModelRoute(role=payload.role, primary_profile_id=payload.primary_profile_id)
        db.add(route)
    route.primary_profile_id = payload.primary_profile_id
    route.fallback_profile_id = payload.fallback_profile_id
    route.enabled = payload.enabled
    await _audit(db, "upsert_route", "model_route", payload.role, payload.model_dump())
    await db.commit()
    await db.refresh(route)
    logger.info(
        "model_config.route.upserted",
        extra={
            "event": "model_config.route.upserted",
            "role": route.role,
            "primary_profile_id": route.primary_profile_id,
            "fallback_profile_id": route.fallback_profile_id,
            "enabled": route.enabled,
        },
    )
    return route


@router.get("/templates", response_model=dict)
async def list_templates(db: AsyncSession = Depends(get_db)) -> dict:
    """列出模型请求模板。"""
    result = await db.execute(
        select(ModelRequestTemplate).where(ModelRequestTemplate.deleted == 0).order_by(ModelRequestTemplate.id)
    )
    return {"items": list(result.scalars())}


@router.post("/templates", response_model=ModelTemplateRead, status_code=201)
async def upsert_template(
    payload: ModelTemplateUpsert,
    db: AsyncSession = Depends(get_db),
) -> ModelRequestTemplate:
    """创建或更新模型请求模板。"""
    result = await db.execute(
        select(ModelRequestTemplate).where(
            ModelRequestTemplate.role == payload.role,
            ModelRequestTemplate.name == payload.name,
            ModelRequestTemplate.deleted == 0,
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        template = ModelRequestTemplate(role=payload.role, name=payload.name)
        db.add(template)
    for key, value in payload.model_dump().items():
        setattr(template, key, value)
    await _audit(db, "upsert_template", "model_request_template", payload.role, {"name": payload.name})
    await db.commit()
    await db.refresh(template)
    logger.info(
        "model_config.template.upserted",
        extra={
            "event": "model_config.template.upserted",
            "role": template.role,
            "template_name": template.name,
            "version": template.version,
            "enabled": template.enabled,
        },
    )
    return template


def _profile_read(profile: ModelProfile) -> ModelProfileRead:
    """构建脱敏后的 profile 响应。"""
    secret = decrypt_secret(profile.encrypted_api_key) if profile.encrypted_api_key else None
    return ModelProfileRead(
        id=profile.id,
        name=profile.name,
        model_type=profile.model_type,
        provider=profile.provider,
        model=profile.model,
        base_url=profile.base_url,
        api_key_configured=bool(secret),
        masked_api_key=mask_secret(secret),
        timeout_seconds=profile.timeout_seconds,
        temperature=profile.temperature,
        dimensions=profile.dimensions,
        config=profile.config,
        enabled=profile.enabled,
    )


async def _audit(db: AsyncSession, action: str, target_type: str, target_id: str, detail: dict) -> None:
    """记录模型配置变更审计日志。"""
    db.add(
        ModelConfigAuditLog(
            actor_user_id=None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
    )
