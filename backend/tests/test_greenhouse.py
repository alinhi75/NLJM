import httpx

from app.ingest.greenhouse import GreenhouseSource, parse


def test_parse_maps_fields(load_fixture):
    postings = parse(load_fixture("greenhouse_jobs.json"), board="examplebv")

    assert len(postings) == 2
    first = postings[0]
    assert first.external_id == "4012345"
    assert first.title == "Backend Engineer (Python)"
    assert first.company == "Example BV"
    assert first.city == "Amsterdam"
    assert first.description == "You will build FastAPI services.\nPython\nPostgreSQL"
    assert first.posted_at is not None


def test_parse_falls_back_to_board_name_for_company(load_fixture):
    postings = parse(load_fixture("greenhouse_jobs.json"), board="examplebv")
    assert postings[1].company == "examplebv"


def test_fetch_requests_each_board_with_content(load_fixture):
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url)
        return httpx.Response(200, json=load_fixture("greenhouse_jobs.json"))

    client = httpx.Client(transport=httpx.MockTransport(handler))
    source = GreenhouseSource(["a", "b"], client=client)
    postings = source.fetch()

    assert len(postings) == 4
    assert [u.path for u in seen] == ["/v1/boards/a/jobs", "/v1/boards/b/jobs"]
    assert all(u.params["content"] == "true" for u in seen)
