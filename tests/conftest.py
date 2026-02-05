"""Shared fixtures for offline testing."""

from unittest.mock import MagicMock

import feedparser
import httpx
import pytest
import respx

# Sample HTML content that mimics Bearblog structure
SAMPLE_POST_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Post</title></head>
<body>
<main>
    <h1>My Test Post</h1>
    <time datetime="2024-06-15">June 15, 2024</time>
    <p>This is the first paragraph of the post.</p>
    <p>This is another paragraph with a <a href="https://example.com">link</a>.</p>
    <h2>A Subheading</h2>
    <p>More content under the subheading.</p>
    <nav><a href="/">Home</a></nav>
    <footer>Footer content</footer>
</main>
<script>console.log('should be removed');</script>
</body>
</html>
"""

SAMPLE_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>About Page</title></head>
<body>
<main>
    <h1>About Me</h1>
    <p>I am a developer who loves building things.</p>
    <p>Check out my <a href="/projects">projects</a>.</p>
</main>
</body>
</html>
"""

# HTML without <main> element (fallback to body)
SAMPLE_HTML_NO_MAIN = """
<!DOCTYPE html>
<html>
<body>
<h1>No Main Element</h1>
<p>Content directly in body.</p>
</body>
</html>
"""

# HTML with no time element
SAMPLE_HTML_NO_DATE = """
<!DOCTYPE html>
<html>
<body>
<main>
<h1>Post Without Date</h1>
<p>This post has no date element.</p>
</main>
</body>
</html>
"""

# HTML with time element but no datetime attribute
SAMPLE_HTML_TIME_TEXT_ONLY = """
<!DOCTYPE html>
<html>
<body>
<main>
<h1>Post With Text Date</h1>
<time>January 1, 2024</time>
<p>This post has date as text only.</p>
</main>
</body>
</html>
"""

# Minimal HTML
MINIMAL_HTML = """
<!DOCTYPE html>
<html><body></body></html>
"""

# Sample RSS feed content
SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Test Blog</title>
    <link>https://test.bearblog.dev</link>
    <description>A test blog for testing purposes.</description>
    <lastBuildDate>Sun, 15 Jun 2024 12:00:00 +0000</lastBuildDate>
    <item>
        <title>First Post</title>
        <link>https://test.bearblog.dev/first-post/</link>
        <description>Summary of the first post.</description>
        <pubDate>Sun, 15 Jun 2024 10:00:00 +0000</pubDate>
    </item>
    <item>
        <title>Second Post</title>
        <link>https://test.bearblog.dev/second-post/</link>
        <description>Summary of the second post.</description>
        <pubDate>Sat, 14 Jun 2024 09:00:00 +0000</pubDate>
    </item>
    <item>
        <title>Third Post</title>
        <link>https://test.bearblog.dev/third-post/</link>
        <description>Summary of the third post.</description>
        <pubDate>Fri, 13 Jun 2024 08:00:00 +0000</pubDate>
    </item>
</channel>
</rss>
"""


@pytest.fixture
def sample_post_html() -> str:
    """Sample Bearblog post HTML."""
    return SAMPLE_POST_HTML


@pytest.fixture
def sample_page_html() -> str:
    """Sample Bearblog page HTML."""
    return SAMPLE_PAGE_HTML


@pytest.fixture
def sample_html_no_main() -> str:
    """HTML without main element."""
    return SAMPLE_HTML_NO_MAIN


@pytest.fixture
def sample_html_no_date() -> str:
    """HTML without date element."""
    return SAMPLE_HTML_NO_DATE


@pytest.fixture
def sample_html_time_text() -> str:
    """HTML with time text but no datetime attribute."""
    return SAMPLE_HTML_TIME_TEXT_ONLY


@pytest.fixture
def minimal_html() -> str:
    """Minimal empty HTML."""
    return MINIMAL_HTML


@pytest.fixture
def sample_rss_feed() -> str:
    """Sample RSS feed XML."""
    return SAMPLE_RSS_FEED


@pytest.fixture
def parsed_feed() -> feedparser.FeedParserDict:
    """Pre-parsed feed for mocking."""
    return feedparser.parse(SAMPLE_RSS_FEED)


@pytest.fixture
def mock_http_client():
    """Create a mock httpx.AsyncClient."""
    return MagicMock(spec=httpx.AsyncClient)


@pytest.fixture
def respx_mock():
    """RESPX mock for HTTP requests."""
    with respx.mock(assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def fresh_cache():
    """Fresh cache instance for testing."""
    from ursaproxy.cache import Cache

    return Cache()


@pytest.fixture
def small_cache():
    """Small cache for testing eviction."""
    from ursaproxy.cache import Cache

    return Cache(max_size=10)


@pytest.fixture(autouse=True)
def reset_global_cache():
    """Reset the global cache before each test."""
    from ursaproxy.cache import cache

    cache._data.clear()
    yield
    cache._data.clear()


@pytest.fixture
def env_settings(monkeypatch):
    """Helper to set environment variables for Settings."""

    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key.upper(), str(value))

    return _set_env
