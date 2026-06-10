from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.agents.mock_generation import MockGenerationAgent
from app.schemas.generation import (
    CreateGenerationTaskRequest,
    CreateResultVersionRequest,
    GenerationResultResponse,
    GenerationTaskResponse,
    ResultVersionListResponse,
    ResultVersionResponse,
)
from app.services.in_memory import store

router = APIRouter()
agent = MockGenerationAgent()


@router.post("/tasks", response_model=GenerationTaskResponse, status_code=status.HTTP_201_CREATED)
def create_generation_task(payload: CreateGenerationTaskRequest) -> dict:
    task, result, session = agent.run(payload)
    store.tasks[task["id"]] = task
    store.results[task["id"]] = result
    _create_result_version(result, "初始生成")
    store.sessions[session["id"]] = session
    return task


@router.get("/tasks/{task_id}", response_model=GenerationTaskResponse)
def get_generation_task(task_id: str) -> dict:
    task = store.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Generation task not found")
    return task


@router.post("/tasks/{task_id}/cancel", response_model=GenerationTaskResponse)
def cancel_generation_task(task_id: str) -> dict:
    task = store.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Generation task not found")
    if task["status"] not in {"completed", "failed"}:
        task.update({"status": "cancelled", "currentStep": "任务已取消"})
    return task


@router.post("/tasks/{task_id}/retry", response_model=GenerationTaskResponse)
def retry_generation_task(task_id: str) -> dict:
    task = store.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Generation task not found")
    task.update({"status": "queued", "progress": 10, "currentStep": "任务排队中"})
    return task


@router.get("/results/{task_id}", response_model=GenerationResultResponse)
def get_generation_result(task_id: str) -> dict:
    result = store.results.get(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Generation result not found")
    return result


@router.put("/results/{result_id}", response_model=GenerationResultResponse)
def update_generation_result(result_id: str, patch: dict) -> dict:
    version_label = patch.pop("versionLabel", None) or patch.pop("version_label", None)
    for result in store.results.values():
        if result["id"] == result_id:
            result.update(patch)
            _create_result_version(result, version_label or "编辑保存")
            return result
    raise HTTPException(status_code=404, detail="Generation result not found")


@router.get("/results/{result_id}/versions", response_model=ResultVersionListResponse)
def list_result_versions(result_id: str) -> dict:
    _find_result_by_id(result_id)
    return {"items": store.result_versions.get(result_id, [])}


@router.post("/results/{result_id}/versions", response_model=ResultVersionResponse, status_code=status.HTTP_201_CREATED)
def create_result_version(result_id: str, payload: CreateResultVersionRequest) -> dict:
    result = _find_result_by_id(result_id)
    return _create_result_version(result, payload.label or "手动保存")


@router.post("/results/{result_id}/versions/{version_id}/restore", response_model=GenerationResultResponse)
def restore_result_version(result_id: str, version_id: str) -> dict:
    result = _find_result_by_id(result_id)
    versions = store.result_versions.get(result_id, [])
    version = next((item for item in versions if item["id"] == version_id), None)
    if not version:
        raise HTTPException(status_code=404, detail="Result version not found")

    result.update(
        {
            "modules": deepcopy(version["modules"]),
            "previewUrl": version.get("previewUrl"),
            "exportUrls": deepcopy(version.get("exportUrls", {})),
            "qualityScore": version["qualityScore"],
            "metadata": deepcopy(version.get("metadata", {})),
        }
    )
    _create_result_version(result, f"恢复版本 {version['version']}")
    return result


def _find_result_by_id(result_id: str) -> dict:
    result = next((item for item in store.results.values() if item["id"] == result_id), None)
    if not result:
        raise HTTPException(status_code=404, detail="Generation result not found")
    return result


def _create_result_version(result: dict, label: str) -> dict:
    versions = store.result_versions.setdefault(result["id"], [])
    version = {
        "id": str(uuid4()),
        "resultId": result["id"],
        "version": len(versions) + 1,
        "label": label,
        "createdAt": datetime.now(UTC).isoformat(),
        "modules": deepcopy(result["modules"]),
        "previewUrl": result.get("previewUrl"),
        "exportUrls": deepcopy(result.get("exportUrls", {})),
        "qualityScore": result["qualityScore"],
        "metadata": deepcopy(result.get("metadata", {})),
    }
    versions.append(version)
    return version
