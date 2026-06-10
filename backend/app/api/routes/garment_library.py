from fastapi import APIRouter, Form, HTTPException, UploadFile, status

from app.schemas.garment_library import GarmentLibraryItem, GarmentLibraryList
from app.services.file_storage import safe_filename
from app.services.garment_library import create_garment_item, delete_garment_item, list_garment_items

router = APIRouter()


@router.get("/items", response_model=GarmentLibraryList)
def list_items() -> dict[str, list[dict]]:
    return {"items": list_garment_items()}


@router.post("/items", response_model=GarmentLibraryItem, status_code=status.HTTP_201_CREATED)
async def upload_item(
    file: UploadFile,
    name: str | None = Form(default=None),
    tags: str | None = Form(default=None),
) -> dict:
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files can be added to garment library")
    safe_filename(file.filename or "garment.png")
    return await create_garment_item(file, name, tags)


@router.delete("/items/{item_id}")
def delete_item(item_id: str) -> dict[str, bool]:
    return {"ok": delete_garment_item(item_id)}
