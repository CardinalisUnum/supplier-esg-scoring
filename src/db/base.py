from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def get_sqlite_url(db_path: str | None = None) -> str:
    if db_path is None:
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = str(data_dir / "esg_simulation.db")
    return f"sqlite:///{db_path}"


def get_engine(db_path: str | None = None):
    return create_engine(get_sqlite_url(db_path), echo=False, future=True)


def get_session_factory(db_path: str | None = None):
    engine = get_engine(db_path)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db(db_path: str | None = None) -> None:
    from src.db import models  # noqa: F401

    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
