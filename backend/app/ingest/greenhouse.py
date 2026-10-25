from datetime import datetime

import httpx

from app.ingest.base import RawPosting, html_to_text

API = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs"


class GreenhouseSource:
    """Public Greenhouse Job Board API: read-only, no key needed."""

    name = "greenhouse"
    terms_url = "https://developers.greenhouse.io/job-board.html"

    def __init__(self, boards: list[str], client: httpx.Client | None = None) -> None:
        self.boards = boards
        self.client = client or httpx.Client(timeout=30)

    def fetch(self) -> list[RawPosting]:
        postings: list[RawPosting] = []
        for board in self.boards:
            resp = self.client.get(API.format(board=board), params={"content": "true"})
            resp.raise_for_status()
            postings.extend(parse(resp.json(), board))
        return postings


def parse(payload: dict, board: str) -> list[RawPosting]:
    postings = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        updated = job.get("updated_at")
        postings.append(
            RawPosting(
                source=GreenhouseSource.name,
                external_id=str(job["id"]),
                title=job["title"].strip(),
                company=job.get("company_name") or board,
                city=location,
                description=html_to_text(job.get("content") or ""),
                url=job["absolute_url"],
                posted_at=datetime.fromisoformat(updated) if updated else None,
            )
        )
    return postings
