"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import spaces, videos, tasks, system, ai_providers, prompt_templates, downloads

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(spaces.router, prefix="/spaces", tags=["spaces"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(ai_providers.router, prefix="/ai-providers", tags=["ai-providers"])
api_router.include_router(prompt_templates.router, prefix="/prompt-templates", tags=["prompt-templates"])