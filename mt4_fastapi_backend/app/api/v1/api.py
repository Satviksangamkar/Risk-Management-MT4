"""
Main API Router
Combines all v1 API endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints.mt4_analysis import router as mt4_analysis_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    mt4_analysis_router,
    prefix="/mt4",
    tags=["MT4 Analysis"]
)

# Health and utility endpoints can be added here
@api_router.get("/version", tags=["Utilities"])
async def get_api_version():
    """Get API version information"""
    from app.core.config import settings

    return {
        "api_version": "v1",
        "service_version": settings.VERSION,
        "project_name": settings.PROJECT_NAME
    }
