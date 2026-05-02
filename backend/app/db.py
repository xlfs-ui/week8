import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "./data/app.db")

engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


def apply_seed_if_needed() -> None:
    db_path = Path(DEFAULT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    newly_created = not db_path.exists()
    if newly_created:
        db_path.touch()

    seed_file = Path("./data/seed.sql")
    if newly_created and seed_file.exists():
        with engine.begin() as conn:
            sql = seed_file.read_text()
            if sql.strip():
                for statement in [s.strip() for s in sql.split(";") if s.strip()]:
                    conn.execute(text(statement))


def migrate_schema_if_needed() -> None:
    """
    Lightweight SQLite migration for week7 model changes.

    Keep this idempotent so startup can run it safely.
    """
    with engine.begin() as conn:
        # Ensure new parent table exists.
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS notebooks (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE,
                  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
                  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
                )
                """
            )
        )
        conn.execute(text("INSERT OR IGNORE INTO notebooks (id, name) VALUES (1, 'General')"))

        notes_columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(notes)")).fetchall()
        }
        if "notebook_id" not in notes_columns:
            conn.execute(
                text(
                    "ALTER TABLE notes ADD COLUMN notebook_id INTEGER REFERENCES notebooks(id) DEFAULT 1"
                )
            )
        conn.execute(text("UPDATE notes SET notebook_id = 1 WHERE notebook_id IS NULL"))

        action_columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(action_items)")).fetchall()
        }
        if "note_id" not in action_columns:
            conn.execute(
                text(
                    "ALTER TABLE action_items ADD COLUMN note_id INTEGER REFERENCES notes(id)"
                )
            )
