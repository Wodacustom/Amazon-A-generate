from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.schemas.tryon import CreateTryonJobRequest, TryonJobItemList, TryonJobResponse
from app.services.in_memory import store
from app.tryon import create_mock_tryon_job, create_queued_tryon_job, process_queued_tryon_job

router = APIRouter()


@router.post("/jobs", response_model=TryonJobResponse, status_code=status.HTTP_201_CREATED)
def create_tryon_job(payload: CreateTryonJobRequest, background_tasks: BackgroundTasks) -> dict:
    if payload.async_processing:
        job, items = create_queued_tryon_job(
            payload.product_asset_ids,
            payload.model_asset_ids,
            payload.output_count,
            payload.ratio,
            payload.mode,
            payload.product_image_urls,
            payload.model_image_urls,
            payload.prompt,
            payload.image_model,
        )
        store.tryon_jobs[job["id"]] = job
        store.tryon_items[job["id"]] = items
        background_tasks.add_task(process_queued_tryon_job, job, items)
        return job

    job, items = create_mock_tryon_job(
        payload.product_asset_ids,
        payload.model_asset_ids,
        payload.output_count,
        payload.ratio,
        payload.mode,
        payload.product_image_urls,
        payload.model_image_urls,
        payload.prompt,
        payload.image_model,
    )
    store.tryon_jobs[job["id"]] = job
    store.tryon_items[job["id"]] = items
    return job


@router.get("/jobs")
def list_tryon_jobs() -> dict[str, list[dict]]:
    return {"items": list(store.tryon_jobs.values())}


@router.get("/jobs/{job_id}", response_model=TryonJobResponse)
def get_tryon_job(job_id: str) -> dict:
    job = store.tryon_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Try-on job not found")
    return job


@router.get("/jobs/{job_id}/items", response_model=TryonJobItemList)
def list_tryon_job_items(job_id: str) -> TryonJobItemList:
    if job_id not in store.tryon_jobs:
        raise HTTPException(status_code=404, detail="Try-on job not found")
    return TryonJobItemList(items=store.tryon_items.get(job_id, []))


@router.post("/jobs/{job_id}/cancel", response_model=TryonJobResponse)
def cancel_tryon_job(job_id: str) -> dict:
    job = store.tryon_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Try-on job not found")
    if job["status"] not in {"completed", "failed", "partial_success"}:
        job.update({"status": "cancelled", "progress": 100})
    return job
