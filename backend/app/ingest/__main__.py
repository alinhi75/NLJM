"""Run an ingest from the command line: python -m app.ingest greenhouse|adzuna"""

import argparse
import logging

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_engine
from app.ingest.adzuna import AdzunaSource
from app.ingest.base import Source
from app.ingest.greenhouse import GreenhouseSource
from app.ingest.store import get_or_create_source, upsert_postings

log = logging.getLogger("nljm.ingest")


def build_source(name: str, args: argparse.Namespace) -> Source:
    settings = get_settings()
    if name == "greenhouse":
        boards = args.board or settings.greenhouse_board_list
        if not boards:
            raise SystemExit("Pass --board or set GREENHOUSE_BOARDS")
        return GreenhouseSource(boards)
    return AdzunaSource(
        settings.adzuna_app_id,
        settings.adzuna_app_key,
        country=settings.adzuna_country,
        what=args.what,
        pages=args.pages,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.ingest")
    parser.add_argument("source", choices=["greenhouse", "adzuna"])
    parser.add_argument("--board", action="append", help="Greenhouse board token (repeatable)")
    parser.add_argument("--what", default="software developer", help="Adzuna search keywords")
    parser.add_argument("--pages", type=int, default=1, help="Adzuna pages of 50 results")
    parser.add_argument("--dry-run", action="store_true", help="Print postings, store nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    source = build_source(args.source, args)
    postings = source.fetch()
    log.info("fetched %d postings from %s", len(postings), source.name)

    if args.dry_run:
        for p in postings:
            print(f"{p.company} | {p.title} | {p.city}")
        return

    with Session(get_engine()) as session:
        row = get_or_create_source(session, source.name, source.terms_url)
        written = upsert_postings(session, row, postings)
    log.info("stored %d postings", written)


if __name__ == "__main__":
    main()
