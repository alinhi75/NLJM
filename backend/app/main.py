from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Job

app = FastAPI(title="NL Job Match", version="0.1.0")

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
def health(session: SessionDep) -> dict:
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}


@app.get("/stats")
def stats(session: SessionDep) -> dict:
    total = session.scalar(select(func.count()).select_from(Job))
    return {"jobs": total}
