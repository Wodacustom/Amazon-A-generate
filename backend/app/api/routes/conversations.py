from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.services.in_memory import store

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation(payload: dict) -> dict:
    session_id = str(uuid4())
    session = {"id": session_id, "status": "active", "messages": [], "imageVersions": [], "context": payload, "createdAt": datetime.now(UTC).isoformat()}
    store.sessions[session_id] = session
    return session


@router.get("/{session_id}")
def get_conversation(session_id: str) -> dict:
    session = store.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return session


@router.post("/{session_id}/messages")
def add_message(session_id: str, payload: dict) -> dict:
    session = store.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    message = {"id": str(uuid4()), **payload, "createdAt": datetime.now(UTC).isoformat()}
    session.setdefault("messages", []).append(message)
    return message


@router.get("/{session_id}/image-versions")
def list_image_versions(session_id: str) -> dict:
    session = store.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"items": session.get("imageVersions", [])}


@router.post("/{session_id}/rollback")
def rollback_image_version(session_id: str, payload: dict) -> dict:
    if session_id not in store.sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"sessionId": session_id, "currentImageVersionId": payload.get("imageVersionId")}
