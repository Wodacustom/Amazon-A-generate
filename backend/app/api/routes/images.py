"""图片生成接口。"""

import json
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.file import FileAsset
from app.schemas.image_generation import GeneratedImageRead, ImageGenerationRead
from app.services.models import ModelService
from app.services.models.types import ImageFileInput, ImageGenerationInput
from app.services.storage import get_storage

router = APIRouter()

PRESIGNED_EXPIRES_IN = 7200
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@router.post("/generate", response_model=ImageGenerationRead)
async def generate_image(
    prompt: str = Form(...),
    image: UploadFile | None = File(None),
    mask: UploadFile | None = File(None),
    role: str = Form("image_generation"),
    model_profile_id: int | None = Form(None),
    size: str = Form("1024x1024"),
    n: int = Form(1),
    options_json: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
) -> ImageGenerationRead:
    """生成或编辑图片，并把结果保存到对象存储后返回预签名链接。"""
    if mask is not None and image is None:
        raise HTTPException(status_code=400, detail="mask requires image.")
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required.")
    if n < 1 or n > 10:
        raise HTTPException(status_code=400, detail="n must be between 1 and 10.")

    options = _parse_options(options_json)
    request = ImageGenerationInput(
        prompt=prompt,
        size=size,
        n=n,
        image=await _read_upload(image) if image else None,
        mask=await _read_upload(mask) if mask else None,
        options=options,
    )
    service = ModelService()
    try:
        output = await service.generate_image(
            request,
            db=db,
            role=role,
            model_profile_id=model_profile_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    storage = get_storage()
    items: list[GeneratedImageRead] = []
    metadata = {**service.image_metadata(), **output.raw_metadata}
    # 结果落库只记录本地文件元数据；provider 原始 URL/base64 不返回给前端。
    for index, generated in enumerate(output.images):
        content_type = generated.content_type or "image/png"
        stored = await storage.put_bytes(
            generated.data,
            f"generated-{index}{_extension_for_content_type(content_type)}",
            content_type,
            prefix="generated",
        )
        asset = FileAsset(
            object_key=stored.object_key,
            bucket=stored.bucket,
            original_filename=f"generated-{index}{_extension_for_content_type(content_type)}",
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
            url=stored.url,
        )
        db.add(asset)
        await db.flush()
        items.append(
            GeneratedImageRead(
                file_id=asset.id,
                image_url=await storage.presign_get_url(stored.object_key, expires_in=PRESIGNED_EXPIRES_IN),
                expires_in=PRESIGNED_EXPIRES_IN,
                provider=str(metadata.get("model_provider") or output.raw_metadata.get("provider") or ""),
                model=str(metadata.get("model_name") or output.raw_metadata.get("model") or ""),
                operation=output.operation,
            )
        )
    await db.commit()
    return ImageGenerationRead(items=items, usage=output.usage, metadata=metadata)


async def _read_upload(upload: UploadFile) -> ImageFileInput:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail=f"{upload.filename or 'file'} is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"{upload.filename or 'file'} exceeds 50MB.")
    return ImageFileInput(filename=upload.filename or "image.png", data=data, content_type=upload.content_type)


def _parse_options(options_json: str | None) -> dict[str, Any]:
    if not options_json:
        return {}
    try:
        options = json.loads(options_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="options_json must be valid JSON.") from exc
    if not isinstance(options, dict):
        raise HTTPException(status_code=400, detail="options_json must be a JSON object.")
    return options


def _extension_for_content_type(content_type: str) -> str:
    if content_type == "image/jpeg":
        return ".jpg"
    if content_type == "image/webp":
        return ".webp"
    return ".png"
