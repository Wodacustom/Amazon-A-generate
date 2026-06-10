from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.product import ProductInfoRecommendationRequest, ProductInfoRecommendationResponse
from app.services.product_info_recommendation import ProductInfoRecommendationAgent
from app.services.in_memory import store

router = APIRouter()
recommendation_agent = ProductInfoRecommendationAgent()


@router.post("/recommend-info", response_model=ProductInfoRecommendationResponse)
def recommend_product_info(payload: ProductInfoRecommendationRequest) -> dict:
    return recommendation_agent.recommend(payload)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(payload: dict) -> dict:
    product_id = payload.get("id") or str(uuid4())
    record = {**payload, "id": product_id, "createdAt": datetime.now(UTC).isoformat()}
    store.products[product_id] = record
    return record


@router.get("")
def list_products() -> dict[str, list[dict]]:
    return {"items": list(store.products.values())}


@router.get("/{product_id}")
def get_product(product_id: str) -> dict:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}")
def update_product(product_id: str, payload: dict) -> dict:
    current = store.products.get(product_id, {"id": product_id})
    current.update(payload)
    store.products[product_id] = current
    return current


@router.delete("/{product_id}")
def delete_product(product_id: str) -> dict[str, bool]:
    store.products.pop(product_id, None)
    return {"ok": True}
