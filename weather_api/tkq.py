import logging
from typing import Annotated, Any

import httpx
import taskiq_fastapi
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import (
    AsyncBroker,
    AsyncResultBackend,
    InMemoryBroker,
    TaskiqDepends,
    TaskiqScheduler,
)
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from weather_api.db.dependencies import get_db_session
from weather_api.db.models.temperature import Temperature
from weather_api.settings import settings

result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
    redis_url=str(settings.redis_url.with_path("/1")),
)
broker: AsyncBroker = AioPikaBroker(
    str(settings.rabbit_url),
).with_result_backend(result_backend)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

if settings.environment.lower() == "pytest":
    broker = InMemoryBroker()

taskiq_fastapi.init(
    broker,
    "weather_api.web.application:get_app",
)

logger = logging.getLogger(__name__)


@broker.task(schedule=[{"cron": "0 * * * *"}])
async def log_temperature(
    session: Annotated[AsyncSession, TaskiqDepends(get_db_session)],
) -> None:
    """Fetch current temp for CITY using Open-Meteo API and persist to DB."""

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": settings.weather.city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(geo_url, params=geo_params, timeout=10)  # type: ignore
            if resp.status_code != 200:
                logger.warning(
                    "Open-Meteo Geocoding failed: %s - %s",
                    resp.status_code,
                    resp.text,
                )
                return
            geo_data = resp.json()
        except httpx.TimeoutException:
            logger.warning("Open-Meteo Geocoding request timed out")
            return
        except httpx.RequestError as e:
            logger.warning("Open-Meteo Geocoding request error: %s", e)
            return

    results = geo_data.get("results")
    if not results:
        logger.warning("No results found for city: %s", settings.weather.city)
        return

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    city_name = results[0]["name"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "timezone": "auto",
        "forecast_days": 1,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(weather_url, params=weather_params, timeout=10)
            if resp.status_code != 200:
                logger.warning(
                    "Open-Meteo Weather API failed: %s - %s",
                    resp.status_code,
                    resp.text,
                )
                return
            weather_data = resp.json()
        except httpx.TimeoutException:
            logger.warning("Open-Meteo Weather API request timed out")
            return
        except httpx.RequestError as e:
            logger.warning("Open-Meteo Weather API request error: %s", e)
            return

    try:
        temp_c = weather_data["current"]["temperature_2m"]
    except (KeyError, TypeError) as e:
        logger.warning("Unexpected Open-Meteo API response schema: %s", e)
        logger.debug("Response data: %s", weather_data)
        return

    record = Temperature(
        city=city_name,
        temperature=temp_c,
    )
    session.add(record)
    await session.commit()

    logger.info("Stored temperature %s °C for %s", temp_c, city_name)
