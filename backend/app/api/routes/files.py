"""文件上传和下载接口。"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.file import FileAsset
from app.schemas.file import FileAssetRead
from app.services.storage import get_storage

router = APIRouter()
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@router.post("", response_model=FileAssetRead, status_code=201)
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> FileAsset:
    """上传文件到 RustFS，并把对象元数据写入 PostgreSQL。"""
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File size exceeds 50MB.")
    stored = await get_storage().put_bytes(data, file.filename, file.content_type)
    asset = FileAsset(
        object_key=stored.object_key,
        bucket=stored.bucket,
        original_filename=file.filename,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        url=stored.url,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/{file_id}", response_model=FileAssetRead)
async def get_file(file_id: UUID, db: AsyncSession = Depends(get_db)) -> FileAsset:
    """按文件 ID 查询元数据。"""
    asset = await db.get(FileAsset, file_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="File not found.")
    return asset


@router.get("/{object_key:path}/content")
async def download_file(object_key: str, db: AsyncSession = Depends(get_db)) -> Response:
    """按对象 key 从 RustFS 读取文件内容。"""
    result = await db.execute(select(FileAsset).where(FileAsset.object_key == object_key))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="File not found.")
    data, content_type = await get_storage().get_bytes(object_key)
    return Response(content=data, media_type=content_type or asset.content_type or "application/octet-stream")
