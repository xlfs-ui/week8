from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Notebook
from ..schemas import NoteCreate, NotePatch, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])
ALLOWED_SORT_FIELDS = {"id", "title", "created_at", "updated_at"}
DEFAULT_NOTEBOOK_NAME = "General"


def _get_or_create_default_notebook(db: Session) -> Notebook:
    notebook = db.execute(select(Notebook).where(Notebook.name == DEFAULT_NOTEBOOK_NAME)).scalar_one_or_none()
    if notebook:
        return notebook
    notebook = Notebook(name=DEFAULT_NOTEBOOK_NAME)
    db.add(notebook)
    db.flush()
    return notebook


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_field}")
    order_fn = desc if sort.startswith("-") else asc
    stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    if sort_field != "id":
        stmt = stmt.order_by(order_fn(Note.id))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    try:
        notebook_id = payload.notebook_id
        if notebook_id is None:
            notebook_id = _get_or_create_default_notebook(db).id
        elif not db.get(Notebook, notebook_id):
            raise HTTPException(status_code=404, detail="Notebook not found")

        note = Note(title=payload.title, content=payload.content, notebook_id=notebook_id)
        db.add(note)
        db.flush()
        db.refresh(note)
        return NoteRead.model_validate(note)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create note") from exc


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    try:
        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content
        if payload.notebook_id is not None:
            notebook = db.get(Notebook, payload.notebook_id)
            if not notebook:
                raise HTTPException(status_code=404, detail="Notebook not found")
            note.notebook_id = notebook.id
        db.add(note)
        db.flush()
        db.refresh(note)
        return NoteRead.model_validate(note)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update note") from exc


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    try:
        db.delete(note)
        db.flush()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete note") from exc


