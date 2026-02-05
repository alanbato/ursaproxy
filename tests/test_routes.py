"""Tests for route handlers."""

from datetime import datetime

import httpx
import pytest
import respx
from xitzin.testing import TestClient

from ursaproxy import _rfc822_to_iso, create_app


class TestRfc822ToIso:
    """Tests for RFC 822 to ISO 8601 date conversion."""

    def test_converts_valid_rfc822_date(self):
        """Test conversion of valid RFC 822 date."""
        rfc822 = "Sun, 15 Jun 2024 12:00:00 +0000"
        result = _rfc822_to_iso(rfc822)

        assert "2024-06-15" in result
        assert "12:00:00" in result
        assert result.endswith("Z")

    def test_replaces_plus_zero_with_z(self):
        """Test that +00:00 is replaced with Z."""
        rfc822 = "Sun, 15 Jun 2024 12:00:00 +0000"
        result = _rfc822_to_iso(rfc822)

        assert "+00:00" not in result
        assert result.endswith("Z")

    def test_empty_string_returns_current_time(self):
        """Test that empty string returns current time with Z suffix."""
        result = _rfc822_to_iso("")

        assert result.endswith("Z")
        # Should be recent
        assert str(datetime.now().year) in result

    def test_invalid_date_returns_current_time(self):
        """Test that invalid date returns current time."""
        result = _rfc822_to_iso("not a date")

        assert result.endswith("Z")
        assert str(datetime.now().year) in result


@pytest.fixture
def test_settings(tmp_path, monkeypatch):
    """Create test settings using env vars (avoids TOML source issues)."""
    monkeypatch.chdir(tmp_path)  # No ursaproxy.toml here
    monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
    monkeypatch.setenv("BLOG_NAME", "Test Blog")
    monkeypatch.setenv("PAGES", '{"about": "About"}')
    from ursaproxy import load_settings

    return load_settings()


@pytest.fixture
def test_app(test_settings):
    """Create a test app with mocked HTTP client."""
    app = create_app(test_settings)
    app.state.client = httpx.AsyncClient()
    return app


class TestIndexRoute:
    """Tests for the index route."""

    @respx.mock
    def test_index_returns_gemtext(self, sample_rss_feed, test_settings):
        """Test that index returns gemtext content."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/")

        assert response.is_success
        assert response.status == 20
        assert test_settings.blog_name in response.body

    @respx.mock
    def test_index_includes_posts(self, sample_rss_feed, test_settings):
        """Test that index includes posts from feed."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/")

        assert "First Post" in response.body
        assert "Second Post" in response.body
        assert "/post/first-post" in response.body

    @respx.mock
    def test_index_includes_pages(self, sample_rss_feed, test_settings):
        """Test that index includes static pages."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/")

        # Check pages from test_settings
        assert "/page/about" in response.body
        assert "About" in response.body


class TestPostRoute:
    """Tests for the post route."""

    @respx.mock
    def test_post_returns_content(self, sample_post_html, test_settings):
        """Test that post route returns converted content."""
        respx.get("https://test.bearblog.dev/my-post/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/post/my-post")

        assert response.is_success
        assert "My Test Post" in response.body

    @respx.mock
    def test_post_includes_date(self, sample_post_html, test_settings):
        """Test that post includes publication date."""
        respx.get("https://test.bearblog.dev/dated-post/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/post/dated-post")

        assert "2024-06-15" in response.body

    @respx.mock
    def test_post_not_found(self, test_settings):
        """Test 404 for non-existent post."""
        respx.get("https://test.bearblog.dev/nonexistent/").mock(
            return_value=httpx.Response(404)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/post/nonexistent")

        assert response.status == 51  # Gemini NotFound

    @respx.mock
    def test_post_server_error(self, test_settings):
        """Test handling of server errors."""
        respx.get("https://test.bearblog.dev/error-post/").mock(
            return_value=httpx.Response(500)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/post/error-post")

        assert response.status == 40  # Gemini TemporaryFailure


class TestPageRoute:
    """Tests for the page route."""

    @respx.mock
    def test_page_returns_content(self, sample_page_html, test_settings):
        """Test that page route returns converted content."""
        respx.get("https://test.bearblog.dev/about/").mock(
            return_value=httpx.Response(200, text=sample_page_html)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/page/about")

        assert response.is_success
        assert "About Me" in response.body

    @respx.mock
    def test_page_excludes_date(self, sample_post_html, test_settings):
        """Test that page does NOT include date (unlike posts)."""
        # Even if HTML has a date, pages shouldn't show it
        respx.get("https://test.bearblog.dev/projects/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/page/projects")

        # The date from sample_post_html is 2024-06-15
        # Pages use include_date=False, so "Published:" shouldn't appear
        assert "Published:" not in response.body


class TestAboutRoute:
    """Tests for the about route."""

    @respx.mock
    def test_about_returns_content(self, sample_rss_feed, test_settings):
        """Test that about route returns content."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/about")

        assert response.is_success
        assert test_settings.blog_name in response.body

    @respx.mock
    def test_about_includes_description(self, sample_rss_feed, test_settings):
        """Test that about includes feed description."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/about")

        # From sample_rss_feed
        assert "test blog for testing purposes" in response.body


class TestFeedRoute:
    """Tests for the Atom feed route."""

    @respx.mock
    def test_feed_returns_atom_xml(self, sample_rss_feed, test_settings):
        """Test that feed returns Atom XML."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/feed")

        assert response.is_success
        assert response.meta == "application/atom+xml"
        assert '<?xml version="1.0"' in response.body
        assert "<feed" in response.body

    @respx.mock
    def test_feed_includes_entries(self, sample_rss_feed, test_settings):
        """Test that feed includes entries from RSS."""
        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/feed")

        assert "<entry>" in response.body
        assert "First Post" in response.body
        assert "gemini://" in response.body

    @respx.mock
    def test_feed_uses_gemini_host(self, sample_rss_feed, tmp_path, monkeypatch):
        """Test that feed uses configured gemini_host."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test Blog")
        monkeypatch.setenv("GEMINI_HOST", "gemini.example.com")
        from ursaproxy import load_settings

        settings_with_host = load_settings()

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(settings_with_host)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        response = client.get("/feed")

        assert "gemini://gemini.example.com" in response.body


class TestCaching:
    """Tests for caching behavior."""

    @respx.mock
    def test_feed_is_cached(self, sample_rss_feed, test_settings):
        """Test that feed data is cached."""
        route = respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)

        # First request
        response1 = client.get("/")
        assert response1.is_success

        # Second request should use cache
        response2 = client.get("/")
        assert response2.is_success

        # HTTP should only be called once
        assert route.call_count == 1

    @respx.mock
    def test_post_is_cached(self, sample_post_html, test_settings):
        """Test that post content is cached."""
        route = respx.get("https://test.bearblog.dev/test-cache/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        app = create_app(test_settings)
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)

        # First request
        response1 = client.get("/post/test-cache")
        assert response1.is_success

        # Second request should use cache
        response2 = client.get("/post/test-cache")
        assert response2.is_success

        # HTTP should only be called once
        assert route.call_count == 1
