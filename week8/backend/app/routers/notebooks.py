from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Notebook
from ..schemas import NotebookCreate, NotebookRead

router = APIRouter(prefix="/notebooks", tags=["notebooks"])
ALLOWED_SORT_FIELDS = {"id", "name", "created_at", "updated_at"}


@router.get("/", response_model=list[NotebookRead])
def list_notebooks(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NotebookRead]:
    sort_field = sort.lstrip("-")
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_field}")

    order_fn = desc if sort.startswith("-") else asc
    stmt = select(Notebook).order_by(order_fn(getattr(Notebook, sort_field)))
    if sort_field != "id":
        stmt = stmt.order_by(order_fn(Notebook.id))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
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
