from datetime import datetime

import httpx

from app.ingest.base import RawPosting, html_to_text

API = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


class AdzunaSource:
    """Adzuna search API. Terms require crediting Adzuna wherever listings are shown."""

    name = "adzuna"
    terms_url = "https://developer.adzuna.com/docs/terms_of_service"

    def __init__(
        self,
        app_id: str,
        app_key: str,
        country: str = "nl",
        what: str = "software developer",
        pages: int = 1,
        client: httpx.Client | None = None,
    ) -> None:
        if not app_id or not app_key:
            raise ValueError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set")
        self.app_id, self.app_key = app_id, app_key
        self.country, self.what, self.pages = country, what, pages
        self.client = client or httpx.Client(timeout=30)

    def fetch(self) -> list[RawPosting]:
        postings: list[RawPosting] = []
        for page in range(1, self.pages + 1):
            resp = self.client.get(
                API.format(country=self.country, page=page),
                params={
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "what": self.what,
                    "results_per_page": 50,
                    "content-type": "application/json",
                },
            )
            resp.raise_for_status()
            batch = parse(resp.json())
            postings.extend(batch)
            if not batch:
                break
        return postings


def parse(payload: dict) -> list[RawPosting]:
    postings = []
    for job in payload.get("results", []):
        location = job.get("location") or {}
        area = location.get("area") or []
        created = job.get("created")
        postings.append(
            RawPosting(
                source=AdzunaSource.name,
                external_id=str(job["id"]),
                title=html_to_text(job["title"]),
                company=(job.get("company") or {}).get("display_name") or "Unknown",
                # area runs country -> province -> city; the last entry is the most specific.
                city=area[-1] if len(area) > 1 else location.get("display_name"),
                description=html_to_text(job.get("description") or ""),
                url=job["redirect_url"],
                posted_at=_parse_time(created),
                salary_min=job.get("salary_min"),
                salary_max=job.get("salary_max"),
            )
        )
    return postings


def _parse_time(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None
