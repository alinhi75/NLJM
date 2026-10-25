import json
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import get_engine

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> dict:
        return json.loads((FIXTURES / name).read_text())

    return _load


@pytest.fixture
def db_session():
    """A session on a migrated database (run `alembic upgrade head` first), emptied per test."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL is not reachable at DATABASE_URL")
    with Session(engine) as session:
        session.execute(text("TRUNCATE sources, jobs, cv_profiles RESTART IDENTITY CASCADE"))
        session.commit()
        yield session
