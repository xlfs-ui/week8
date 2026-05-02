from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class _NonEmptyStringModel(BaseModel):
    @staticmethod
    def _validate_required_text(value: str, field_name: str) -> str:
        if value.strip() == "":
            raise ValueError(f"{field_name} must not be blank")
        return value


class NotebookCreate(_NonEmptyStringModel):
    name: str

    @model_validator(mode="after")
    def validate_name(self) -> "NotebookCreate":
        self.name = self._validate_required_text(self.name, "name")
        return self


class NotebookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class NoteCreate(_NonEmptyStringModel):
    title: str
    content: str
    notebook_id: int | None = None

    @model_validator(mode="after")
    def validate_text_fields(self) -> "NoteCreate":
        self.title = self._validate_required_text(self.title, "title")
        self.content = self._validate_required_text(self.content, "content")
        return self


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    notebook_id: int
    created_at: datetime
    updated_at: datetime


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None
    notebook_id: int | None = None

    @model_validator(mode="after")
    def validate_patch_payload(self) -> "NotePatch":
        if self.title is None and self.content is None and self.notebook_id is None:
            raise ValueError("At least one field must be provided")
        if self.title is not None and self.title.strip() == "":
            raise ValueError("title must not be blank")
        if self.content is not None and self.content.strip() == "":
            raise ValueError("content must not be blank")
        return self


class ActionItemCreate(_NonEmptyStringModel):
    description: str
    note_id: int | None = None

    @model_validator(mode="after")
    def validate_description(self) -> "ActionItemCreate":
        self.description = self._validate_required_text(self.description, "description")
        return self


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    note_id: int | None
    created_at: datetime
    updated_at: datetime


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None
    note_id: int | None = None

    @model_validator(mode="after")
    def validate_patch_payload(self) -> "ActionItemPatch":
        if self.description is None and self.completed is None and self.note_id is None:
            raise ValueError("At least one field must be provided")
        if self.description is not None and self.description.strip() == "":
            raise ValueError("description must not be blank")
        return self