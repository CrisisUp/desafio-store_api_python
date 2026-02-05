from datetime import datetime
from decimal import Decimal
from typing import Any
from bson import Decimal128
from pydantic import UUID4, BaseModel, Field, model_validator, ConfigDict


class BaseSchemaMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class OutSchema(BaseModel):
    id: UUID4 = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()

    @model_validator(mode="before")
    @classmethod
    def set_schema(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, Decimal128):
                    data[key] = Decimal(str(value))
        return data
