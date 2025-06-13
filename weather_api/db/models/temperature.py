from sqlalchemy.orm import Mapped, mapped_column

from weather_api.db.base import Base
from weather_api.db.fields import uuid_pk


class Temperature(Base):
    """Model for storing temperature data."""

    __tablename__ = "temperatures"

    id: Mapped[uuid_pk]

    city: Mapped[str] = mapped_column(index=True, comment="City name")
    temperature: Mapped[float]
