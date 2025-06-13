from datetime import date
from typing import Annotated, Self, Sequence

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from weather_api.db.dependencies import get_db_session
from weather_api.db.models.temperature import Temperature


class TemperatureDAO:
    """Data Access Object for temperature data."""

    def __init__(
        self: Self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> None:
        self.session = session

    async def get_temperature(self, date: date) -> Sequence[Temperature]:
        """
        Retrieves the current temperature for a given date.

        :param date: The date for which to retrieve the temperature.
        :returns: The current temperature in Celsius.
        :raises ValueError: If no temperature data is found for the specified date.
        """
        stmt = (
            select(Temperature)
            .where(func.date(Temperature.created_at) == date)
            .order_by(Temperature.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_temperature(self: Self, city: str, temperature: float) -> None:
        """
        Creates a new temperature record for a given city.

        :param city: The name of the city.
        :param temperature: The temperature in Celsius.
        :returns: None
        """
        self.session.add(Temperature(city=city, temperature=temperature))
        await self.session.commit()
