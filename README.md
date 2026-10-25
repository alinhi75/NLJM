# NLJM: NL Job Match

![CI](https://github.com/alinhi75/NLJM/actions/workflows/ci.yml/badge.svg)

Pulls Dutch software vacancies from public job APIs, stores them in PostgreSQL with pgvector, and
ranks them against a CV: vector search picks the closest 50 postings, then an LLM gives each one a
fit score with matched and missing skills.

> Status: phase 0 of 4. Ingestion from Greenhouse and Adzuna, database schema and API skeleton
> are in place. Matching, the UI and the AWS deployment come next (see [Roadmap](#roadmap)).

## Stack

Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16 + pgvector, httpx, pytest, Docker
Compose, GitHub Actions. Planned: React, Claude API, Terraform on AWS.

## Run locally

```bash
cp .env.example .env          # add your Adzuna key and Greenhouse boards
docker compose up --build     # Postgres + API on http://localhost:8000
curl localhost:8000/health
```

Ingest jobs (from the `backend/` folder, with `DATABASE_URL` pointing at the database):

```bash
pip install -e ".[dev]"
python -m app.ingest greenhouse --board <board-token> --dry-run   # print, store nothing
python -m app.ingest greenhouse --board <board-token>
python -m app.ingest adzuna --what "python developer" --pages 2
curl localhost:8000/stats
```

## Tests

```bash
cd backend
alembic upgrade head   # tests that touch the database need a migrated Postgres
pytest -q
```

Source tests run against recorded fixtures in `backend/tests/fixtures/`, so CI never calls the
live APIs. The fixtures are synthetic examples shaped like real responses.

## Data sources

Only official APIs and feeds that companies publish for reuse. No scraping of LinkedIn, Indeed or
other job boards whose terms forbid it.

| Source | Access | Terms |
| --- | --- | --- |
| Greenhouse Job Board API | Public, read-only, no key | [developers.greenhouse.io](https://developers.greenhouse.io/job-board.html) |
| Adzuna | Free API key; listings must credit Adzuna | [Terms of service](https://developer.adzuna.com/docs/terms_of_service) |

Jobs are deduplicated on company + title + city, so the same vacancy from two sources is stored
once.

## Roadmap

- [x] Phase 0: skeleton, schema, first two sources, CI
- [ ] Phase 1: Recruitee and Lever sources, normalisation, retries, daily schedule
- [ ] Phase 2: CV upload, embeddings, vector search, LLM rerank, React UI
- [ ] Phase 3: Terraform on AWS, deploy pipeline, demo

## Licence

MIT
