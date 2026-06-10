from app.api.routes.auth import router as auth_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.files import router as files_router
from app.api.routes.garment_library import router as garment_library_router
from app.api.routes.generation import router as generation_router
from app.api.routes.health import router as health_router
from app.api.routes.mockups import router as mockups_router
from app.api.routes.products import router as products_router
from app.api.routes.prompt_options import router as prompt_options_router
from app.api.routes.style_memories import router as style_memories_router
from app.api.routes.tryon import router as tryon_router

__all__ = [
    "auth_router",
    "conversations_router",
    "files_router",
    "garment_library_router",
    "generation_router",
    "health_router",
    "mockups_router",
    "products_router",
    "prompt_options_router",
    "style_memories_router",
    "tryon_router",
]
