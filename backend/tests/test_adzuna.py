import httpx
import pytest

from app.ingest.adzuna import AdzunaSource, parse


def test_parse_maps_fields(load_fixture):
    postings = parse(load_fixture("adzuna_search.json"))

    first = postings[0]
    assert first.title == "Python Developer"
    assert first.company == "Voorbeeld Software B.V."
    assert first.city == "Enschede"
    assert (first.salary_min, first.salary_max) == (3800, 4800)


def test_parse_country_only_location_uses_display_name(load_fixture):
    assert parse(load_fixture("adzuna_search.json"))[1].city == "Nederland"


def test_missing_keys_raise():
    with pytest.raises(ValueError):
        AdzunaSource("", "")


def test_fetch_stops_on_empty_page(load_fixture):
    pages = []

    def handler(request: httpx.Request) -> httpx.Response:
        pages.append(request.url.path)
        body = load_fixture("adzuna_search.json") if len(pages) == 1 else {"results": []}
        return httpx.Response(200, json=body)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    postings = AdzunaSource("id", "key", pages=5, client=client).fetch()

    assert len(postings) == 2
    assert pages == ["/v1/api/jobs/nl/search/1", "/v1/api/jobs/nl/search/2"]
