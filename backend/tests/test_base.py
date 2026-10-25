from app.ingest.base import content_hash, html_to_text


def test_html_to_text_handles_escaped_html():
    raw = (
        "&lt;p&gt;Build &lt;b&gt;APIs&lt;/b&gt;&lt;/p&gt;"
        "&lt;ul&gt;&lt;li&gt;Python&lt;/li&gt;&lt;/ul&gt;"
    )
    assert html_to_text(raw) == "Build APIs\nPython"


def test_html_to_text_decodes_double_escaped_entities():
    assert html_to_text("React &amp;amp; TypeScript") == "React & TypeScript"


def test_content_hash_ignores_case_and_whitespace():
    a = content_hash("Example BV", "Backend  Engineer", "Amsterdam")
    b = content_hash("example bv", " backend engineer ", "AMSTERDAM")
    assert a == b


def test_content_hash_differs_by_city():
    assert content_hash("X", "Dev", "Enschede") != content_hash("X", "Dev", "Hengelo")
