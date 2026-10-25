from sqlalchemy import func, select

from app.ingest.greenhouse import parse
from app.ingest.store import get_or_create_source, upsert_postings
from app.models import Job


def test_upsert_is_idempotent(db_session, load_fixture):
    postings = parse(load_fixture("greenhouse_jobs.json"), board="examplebv")
    source = get_or_create_source(db_session, "greenhouse", "https://example.test/terms")

    upsert_postings(db_session, source, postings)
    first_seen = db_session.scalar(select(Job.last_seen_at).where(Job.external_id == "4012345"))
    upsert_postings(db_session, source, postings)

    assert db_session.scalar(select(func.count()).select_from(Job)) == 2
    db_session.expire_all()
    last_seen = db_session.scalar(select(Job.last_seen_at).where(Job.external_id == "4012345"))
    assert last_seen >= first_seen


def test_same_job_from_two_sources_is_stored_once(db_session, load_fixture):
    postings = parse(load_fixture("greenhouse_jobs.json"), board="examplebv")
    gh = get_or_create_source(db_session, "greenhouse", "https://example.test/terms")
    other = get_or_create_source(db_session, "other", "https://example.test/terms")

    upsert_postings(db_session, gh, postings[:1])
    upsert_postings(db_session, other, postings[:1])

    assert db_session.scalar(select(func.count()).select_from(Job)) == 1


def test_get_or_create_source_reuses_row(db_session):
    a = get_or_create_source(db_session, "adzuna", "https://example.test/terms")
    b = get_or_create_source(db_session, "adzuna", "https://example.test/terms")
    assert a.id == b.id
