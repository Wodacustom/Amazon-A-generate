from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import settings
from app.services.gemini_image import GeminiImageGenerationClient


def estimate_item_count(product_asset_ids: list[str], model_asset_ids: list[str], output_count: int) -> int:
    return len(product_asset_ids) * len(model_asset_ids) * max(output_count, 1)


def create_mock_tryon_job(
    product_asset_ids: list[str],
    model_asset_ids: list[str],
    output_count: int,
    ratio: str,
    mode: str,
    product_image_urls: list[str] | None = None,
    model_image_urls: list[str] | None = None,
    prompt: str = "",
    image_model: str | None = None,
) -> tuple[dict, list[dict]]:
    now = datetime.now(UTC).isoformat()
    job_id = str(uuid4())
    items = []
    products = product_image_urls or product_asset_ids
    models = model_image_urls or model_asset_ids
    image_client = GeminiImageGenerationClient()
    for product_index, product_asset_id in enumerate(products):
        for model_index, model_asset_id in enumerate(models):
            for _ in range(max(output_count, 1)):
                output_url = _generate_tryon_image(
                    image_client,
                    product_asset_id,
                    model_asset_id,
                    ratio,
                    prompt,
                    image_model,
                )
                items.append(
                    {
                        "id": str(uuid4()),
                        "jobId": job_id,
                        "productAssetId": product_asset_ids[product_index] if product_index < len(product_asset_ids) else product_asset_id,
                        "modelAssetId": model_asset_ids[model_index] if model_index < len(model_asset_ids) else model_asset_id,
                        "status": "completed",
                        "progress": 100,
                        "outputImageUrl": output_url,
                        "prompt": prompt,
                        "metadata": {"ratio": ratio, "mode": mode, "garmentUrl": product_asset_id, "modelUrl": model_asset_id},
                    }
                )
    job = {
        "id": job_id,
        "status": "completed",
        "progress": 100,
        "totalItems": len(items),
        "completedItems": len(items),
        "failedItems": 0,
        "cancelledItems": 0,
        "createdAt": now,
    }
    return job, items


def create_queued_tryon_job(
    product_asset_ids: list[str],
    model_asset_ids: list[str],
    output_count: int,
    ratio: str,
    mode: str,
    product_image_urls: list[str] | None = None,
    model_image_urls: list[str] | None = None,
    prompt: str = "",
    image_model: str | None = None,
) -> tuple[dict, list[dict]]:
    now = datetime.now(UTC).isoformat()
    job_id = str(uuid4())
    items = []
    products = product_image_urls or product_asset_ids
    models = model_image_urls or model_asset_ids
    for product_index, product_asset_id in enumerate(products):
        for model_index, model_asset_id in enumerate(models):
            for _ in range(max(output_count, 1)):
                items.append(
                    {
                        "id": str(uuid4()),
                        "jobId": job_id,
                        "productAssetId": product_asset_ids[product_index] if product_index < len(product_asset_ids) else product_asset_id,
                        "modelAssetId": model_asset_ids[model_index] if model_index < len(model_asset_ids) else model_asset_id,
                        "status": "queued",
                        "progress": 0,
                        "outputImageUrl": None,
                        "prompt": prompt,
                        "metadata": {
                            "ratio": ratio,
                            "mode": mode,
                            "garmentUrl": product_asset_id,
                            "modelUrl": model_asset_id,
                            "imageModel": image_model,
                        },
                    }
                )
    job = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "totalItems": len(items),
        "completedItems": 0,
        "failedItems": 0,
        "cancelledItems": 0,
        "createdAt": now,
    }
    return job, items


def process_queued_tryon_job(job: dict, items: list[dict]) -> None:
    if job.get("status") == "cancelled":
        return
    image_client = GeminiImageGenerationClient()
    job.update({"status": "running", "progress": 1})
    completed = 0
    failed = 0
    total = len(items) or 1
    for item in items:
        if job.get("status") == "cancelled":
            item.update({"status": "cancelled", "progress": 100})
            continue
        item.update({"status": "running", "progress": 50})
        metadata = item.get("metadata", {})
        try:
            output_url = _generate_tryon_image(
                image_client,
                metadata.get("garmentUrl") or item["productAssetId"],
                metadata.get("modelUrl") or item["modelAssetId"],
                metadata.get("ratio", "4_5"),
                item.get("prompt") or "",
                metadata.get("imageModel"),
            )
            item.update({"status": "completed", "progress": 100, "outputImageUrl": output_url})
            completed += 1
        except Exception as error:
            item.update({"status": "failed", "progress": 100, "errorMessage": str(error)})
            failed += 1
        job.update(
            {
                "completedItems": completed,
                "failedItems": failed,
                "progress": round(((completed + failed) / total) * 100),
            }
        )
    final_status = "completed" if failed == 0 else "partial_success" if completed else "failed"
    job.update({"status": final_status, "progress": 100})


def _generate_tryon_image(
    image_client: GeminiImageGenerationClient,
    garment_url: str,
    model_url: str,
    ratio: str,
    prompt: str,
    image_model: str | None,
) -> str:
    fallback_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80"
    if settings.image_generation_provider != "gemini":
        return fallback_url
    try:
        return (
            image_client.generate_module_image(
                prompt or DEFAULT_TRYON_PROMPT,
                "fashion_tryon",
                ratio,
                [garment_url],
                model_url,
                image_model,
            )
            or fallback_url
        )
    except Exception:
        return fallback_url


DEFAULT_TRYON_PROMPT = (
    "Use the model reference image as the person and pose reference. Put the uploaded garment on the model. "
    "Preserve the garment exactly as provided: do not change the clothing silhouette, fabric texture, color, print, "
    "pattern, logo, buttons, zipper, seams, collar, sleeves, hem, decorations, embroidery, labels, pockets, or any "
    "visible design elements. Keep the garment proportions faithful to the source clothing image. Fit it naturally "
    "onto the model's body with realistic drape, folds, shadows, and occlusion. Keep the model identity, face, body "
    "pose, hands, background, camera angle, and lighting consistent with the reference model image. Produce a clean "
    "commercial fashion ecommerce try-on image."
)
