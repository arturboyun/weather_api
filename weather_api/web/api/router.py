from fastapi.routing import APIRouter

from weather_api.web.api import monitoring, temperature

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(
    temperature.router,
    prefix="/temperature",
    tags=["temperature"],
)
