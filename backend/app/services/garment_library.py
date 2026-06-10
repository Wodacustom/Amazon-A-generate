from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.services.file_storage import delete_storage_file, save_upload_file, storage_dir


def garment_library_dir() -> Path:
    return storage_dir("garment-library")


def garment_library_index_path() -> Path:
    return Path(settings.local_storage_dir) / "garment_library.json"


def list_garment_items() -> list[dict]:
    index_path = garment_library_index_path()
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    items = data if isinstance(data, list) else data.get("items", [])
    return [item for item in items if isinstance(item, dict)]


async def create_garment_item(file: UploadFile, name: str | None = None, tags: str | None = None) -> dict:
    saved = await save_upload_file(file, "garment-library", "garment.png")
    item = {
        "id": saved["id"],
        "name": (name or Path(saved["filename"]).stem).strip() or saved["filename"],
        "filename": saved["filename"],
        "contentType": saved["contentType"],
        "url": f"/api/files/garment-library/{saved['storageKey']}",
        "storageKey": saved["storageKey"],
        "tags": _parse_tags(tags),
        "createdAt": datetime.now(UTC).isoformat(),
    }
    items = [item, *list_garment_items()]
    _write_items(items)
    return item


def delete_garment_item(item_id: str) -> bool:
    items = list_garment_items()
    target = next((item for item in items if item.get("id") == item_id), None)
    if not target:
        return False

    delete_storage_file("garment-library", target.get("storageKey"))
    _write_items([item for item in items if item.get("id") != item_id])
    return True


def _write_items(items: list[dict]) -> None:
    index_path = garment_library_index_path()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    return [tag.strip() for tag in tags.replace("，", ",").split(",") if tag.strip()]
