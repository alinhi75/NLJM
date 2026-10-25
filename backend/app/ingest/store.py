from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingest.base import RawPosting, content_hash
from app.models import Job, Source


def get_or_create_source(session: Session, name: str, terms_url: str) -> Source:
    source = session.scalar(select(Source).where(Source.name == name))
    if source is None:
        source = Source(name=name, terms_url=terms_url)
        session.add(source)
        session.flush()
    return source


def upsert_postings(session: Session, source: Source, postings: list[RawPosting]) -> int:
    """Insert new postings; for ones already stored, only bump last_seen_at.

    Returns the number of rows written (new or refreshed).
    """
    now = datetime.now(UTC)
    rows = {}
    for p in postings:
        h = content_hash(p.company, p.title, p.city)
        rows[h] = {
            "source_id": source.id,
            "external_id": p.external_id,
            "title": p.title,
            "company": p.company,
            "city": p.city,
            "description": p.description,
            "url": p.url,
            "posted_at": p.posted_at,
            "salary_min": p.salary_min,
            "salary_max": p.salary_max,
            "content_hash": h,
            "last_seen_at": now,
        }
    if not rows:
        return 0
    stmt = insert(Job).values(list(rows.values()))
    stmt = stmt.on_conflict_do_update(
        index_elements=[Job.content_hash], set_={"last_seen_at": stmt.excluded.last_seen_at}
    )
    result = session.execute(stmt)
    session.commit()
    return result.rowcount
