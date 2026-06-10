from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.file_storage import delete_storage_file, save_upload_file, storage_path
from app.services.in_memory import store

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile) -> dict:
    saved = await save_upload_file(file, "uploads", "upload.bin")
    record = {
        "id": saved["id"],
        "filename": saved["filename"],
        "contentType": saved["contentType"],
        "url": f"/api/files/uploads/{saved['storageKey']}",
        "storageKey": saved["storageKey"],
    }
    store.files[saved["id"]] = record
    return record


@router.get("/uploads/{filename}")
def get_uploaded_file(filename: str) -> FileResponse:
    path = storage_path("uploads", filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path)


@router.get("/{file_id}")
def get_file(file_id: str) -> FileResponse:
    record = store.files.get(file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    storage_key = record.get("storageKey")
    if not storage_key:
        raise HTTPException(status_code=400, detail="Invalid storage key")

    path = storage_path("uploads", storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type=record.get("contentType"), filename=record.get("filename"))


@router.delete("/{file_id}")
def delete_file(file_id: str) -> dict[str, bool]:
    record = store.files.pop(file_id, None)
    if record:
        delete_storage_file("uploads", record.get("storageKey"))
    return {"ok": True}


@router.get("/generated/{filename}")
def get_generated_file(filename: str) -> FileResponse:
    path = storage_path("generated", filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Generated file not found")
    return FileResponse(path)


@router.get("/garment-library/{filename}")
def get_garment_library_file(filename: str) -> FileResponse:
    path = storage_path("garment-library", filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Garment library file not found")
    return FileResponse(path)
