from fastapi import APIRouter

from app.api.routes import agent, files, health, products, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
