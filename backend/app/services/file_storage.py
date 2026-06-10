from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings


STORAGE_DIRS = {
    "uploads": "uploads",
    "generated": "generated",
    "garment-library": "garment-library",
}


def storage_dir(bucket: str) -> Path:
    directory = STORAGE_DIRS.get(bucket)
    if not directory:
        raise ValueError(f"Unknown storage bucket: {bucket}")
    return Path(settings.local_storage_dir) / directory


def safe_filename(filename: str) -> str:
    if not filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return Path(filename).name


async def save_upload_file(file: UploadFile, bucket: str, default_name: str) -> dict:
    file_id = str(uuid4())
    original_name = safe_filename(file.filename or default_name)
    stored_filename = f"{file_id}{Path(original_name).suffix}"

    directory = storage_dir(bucket)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / stored_filename).write_bytes(await file.read())

    return {
        "id": file_id,
        "filename": original_name,
        "contentType": file.content_type,
        "storageKey": stored_filename,
    }


def storage_path(bucket: str, filename: str) -> Path:
    return storage_dir(bucket) / safe_filename(filename)


def delete_storage_file(bucket: str, filename: str | None) -> None:
    if not filename:
        return
    path = storage_path(bucket, filename)
    if path.exists():
        path.unlink()
