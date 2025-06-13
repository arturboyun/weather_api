from datetime import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from weather_api.settings import settings


@pytest.mark.anyio
async def test_health(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("health_check")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_temperatures(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the temperature endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("get_temperature")
    response = await client.get(
        url,
        params={"date": datetime.now().date()},
        headers={"X-Token": settings.x_token},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
