from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)


# Whitespace is stripped before the length limits are checked.
Title = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]
Description = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
]


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title
    description: Description


class DocumentResponse(BaseModel):
    id: int
    title: str
    description: str


class DocumentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    description: Description | None = None

    # Fields may be omitted, but not explicitly set to null.
    @field_validator("title", "description", mode="before")
    @classmethod
    def reject_null(cls, value: object, info: ValidationInfo) -> object:
        if value is None:
            raise ValueError(f"{info.field_name.capitalize()} cannot be null")

        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        return self
