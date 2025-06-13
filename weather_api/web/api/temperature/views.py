from datetime import date
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from weather_api.db.dao.temperature_dao import TemperatureDAO
from weather_api.settings import settings
from weather_api.web.api.temperature.schema import TemperatureSchema

router = APIRouter()
logger = getLogger(__name__)


@router.get("/", response_model=list[TemperatureSchema])
async def get_temperature(
    dao: Annotated[TemperatureDAO, Depends()],
    date: date = Query(
        ...,
        description="The date with YYYY-MM-DD format",
    ),
    x_token: str = Header(..., description="API token for authentication"),
) -> list[TemperatureSchema]:
    """
    Retrieve temperature history for a specific date.

    This endpoint returns a list of temperature records for the specified date.

    :param dao: Data Access Object for temperature data.
    :param date: The date for which to retrieve the temperature in YYYY-MM-DD format.
    :param x_token: API token for authentication.
    :return: A list of temperature records for the specified date.
    """
    if not x_token or x_token != settings.x_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        return [
            TemperatureSchema.model_validate(temperature)
            for temperature in await dao.get_temperature(date)
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.exception("An error occurred while fetching temperature data")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
