from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Notebook
from ..schemas import NotebookCreate, NotebookRead

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("/", response_model=list[NotebookRead])
def list_notebooks(db: Session = Depends(get_db)) -> list[NotebookRead]:
    rows = db.execute(select(Notebook).order_by(Notebook.created_at.desc())).scalars().all()
    return [NotebookRead.model_validate(row) for row in rows]


@router.post("/", response_model=NotebookRead, status_code=201)
def create_notebook(payload: NotebookCreate, db: Session = Depends(get_db)) -> NotebookRead:
    existing = db.execute(select(Notebook).where(Notebook.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Notebook name already exists")
    try:
        notebook = Notebook(name=payload.name)
        db.add(notebook)
        db.flush()
        db.refresh(notebook)
        return NotebookRead.model_validate(notebook)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create notebook") from exc
