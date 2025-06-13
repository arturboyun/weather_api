from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TemperatureSchema(BaseModel):
    """Schema for temperature data."""

    temperature: float = Field(..., description="The temperature in Celsius")
    created_at: datetime = Field(
        ...,
        serialization_alias="date",
        description="The date when the temperature was recorded",
    )

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        """Serialize the created_at field to a new format."""

        # Date and time format: "2025-06-13 10:20"
        return value.strftime("%Y-%m-%d %H:%M")
