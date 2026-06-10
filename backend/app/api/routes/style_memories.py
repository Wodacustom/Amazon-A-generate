from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.services.in_memory import store

router = APIRouter()


@router.get("")
def list_style_memories() -> dict[str, list[dict]]:
    return {"items": list(store.style_memories.values())}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_style_memory(payload: dict) -> dict:
    memory_id = str(uuid4())
    record = {**payload, "id": memory_id, "isActive": payload.get("isActive", True), "createdAt": datetime.now(UTC).isoformat()}
    store.style_memories[memory_id] = record
    return record


@router.put("/{memory_id}")
def update_style_memory(memory_id: str, payload: dict) -> dict:
    record = store.style_memories.get(memory_id)
    if not record:
        raise HTTPException(status_code=404, detail="Style memory not found")
    record.update(payload)
    return record


@router.delete("/{memory_id}")
def delete_style_memory(memory_id: str) -> dict[str, bool]:
    store.style_memories.pop(memory_id, None)
    return {"ok": True}


@router.post("/{memory_id}/apply")
def apply_style_memory(memory_id: str) -> dict:
    if memory_id not in store.style_memories:
        raise HTTPException(status_code=404, detail="Style memory not found")
    return {"memoryId": memory_id, "applied": True}


@router.post("/{memory_id}/update-from-result")
def update_style_memory_from_result(memory_id: str, payload: dict) -> dict:
    record = store.style_memories.get(memory_id)
    if not record:
        raise HTTPException(status_code=404, detail="Style memory not found")
    record["lastResultId"] = payload.get("resultId")
    record["updatedAt"] = datetime.now(UTC).isoformat()
    return record
