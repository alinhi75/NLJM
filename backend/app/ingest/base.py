import hashlib
import html
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"[ \t\r\f\v]+")
_BLOCK_RE = re.compile(r"</?(p|br|li|ul|ol|div|h[1-6])[^>]*>", re.IGNORECASE)


@dataclass(frozen=True)
class RawPosting:
    """One job posting as a source returns it, before it is stored."""

    source: str
    external_id: str
    title: str
    company: str
    city: str | None
    description: str
    url: str
    posted_at: datetime | None = None
    salary_min: float | None = None
    salary_max: float | None = None


class Source(Protocol):
    name: str
    terms_url: str

    def fetch(self) -> list[RawPosting]: ...


def html_to_text(raw: str) -> str:
    """Strip tags from a (possibly entity-escaped) HTML description."""
    unescaped = html.unescape(html.unescape(raw))
    with_breaks = _BLOCK_RE.sub("\n", unescaped)
    stripped = _TAG_RE.sub("", with_breaks)
    lines = (_SPACE_RE.sub(" ", line).strip() for line in stripped.splitlines())
    return "\n".join(line for line in lines if line)


def _norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def content_hash(company: str, title: str, city: str | None) -> str:
    key = "|".join((_norm(company), _norm(title), _norm(city)))
    return hashlib.sha256(key.encode()).hexdigest()
