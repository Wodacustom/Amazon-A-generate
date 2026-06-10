from fastapi import APIRouter

from app.api.routes import (
    auth_router,
    conversations_router,
    files_router,
    garment_library_router,
    generation_router,
    health_router,
    mockups_router,
    products_router,
    prompt_options_router,
    style_memories_router,
    tryon_router,
)

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(garment_library_router, prefix="/garment-library", tags=["garment-library"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(generation_router, prefix="/generation", tags=["generation"])
api_router.include_router(mockups_router, prefix="/mockups", tags=["mockups"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(style_memories_router, prefix="/style-memories", tags=["style-memories"])
api_router.include_router(prompt_options_router, tags=["prompt-options"])
api_router.include_router(tryon_router, prefix="/tryon", tags=["tryon"])
