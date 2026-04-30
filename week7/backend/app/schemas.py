from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 200:
            raise ValueError("title must be at most 200 characters")
        if value == "":
            raise ValueError("title must not be empty")
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 5000:
            raise ValueError("content must be at most 5000 characters")
        if value == "":
            raise ValueError("content must not be empty")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "NotePatch":
        if self.title is None and self.content is None:
            raise ValueError("at least one field is required")
        return self


class ActionItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=1000)

    @field_validator("description", mode="before")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None

    @field_validator("description", mode="before")
    @classmethod
    def strip_optional_description(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 1000:
            raise ValueError("description must be at most 1000 characters")
        if value == "":
            raise ValueError("description must not be empty")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ActionItemPatch":
        if self.description is None and self.completed is None:
            raise ValueError("at least one field is required")
        return self


