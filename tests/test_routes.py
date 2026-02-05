"""Tests for route handlers."""

from datetime import datetime
from unittest.mock import patch

import httpx
import pytest
import respx

from ursaproxy import _rfc822_to_iso, app


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
def test_client(mock_settings):
    """Create a test client with mocked settings and HTTP client."""
    from xitzin.testing import TestClient

    with patch("ursaproxy.settings", mock_settings):
        # Create client in app state
        app.state.client = httpx.AsyncClient()
        client = TestClient(app)
        yield client
        # Note: AsyncClient cleanup happens automatically when it goes out of scope


class TestIndexRoute:
    """Tests for the index route."""

    @respx.mock
    def test_index_returns_gemtext(self, sample_rss_feed, mock_settings):
        """Test that index returns gemtext content."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/")

                assert response.is_success
                assert response.status == 20
                assert mock_settings.blog_name in response.body

    @respx.mock
    def test_index_includes_posts(self, sample_rss_feed, mock_settings):
        """Test that index includes posts from feed."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/")

                assert "First Post" in response.body
                assert "Second Post" in response.body
                assert "/post/first-post" in response.body

    @respx.mock
    def test_index_includes_pages(self, sample_rss_feed, mock_settings):
        """Test that index includes static pages."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/")

                # Check pages from mock_settings
                assert "/page/about" in response.body
                assert "About" in response.body


class TestPostRoute:
    """Tests for the post route."""

    @respx.mock
    def test_post_returns_content(self, sample_post_html, mock_settings):
        """Test that post route returns converted content."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/my-post/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/post/my-post")

                assert response.is_success
                assert "My Test Post" in response.body

    @respx.mock
    def test_post_includes_date(self, sample_post_html, mock_settings):
        """Test that post includes publication date."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/dated-post/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/post/dated-post")

                assert "2024-06-15" in response.body

    @respx.mock
    def test_post_not_found(self, mock_settings):
        """Test 404 for non-existent post."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/nonexistent/").mock(
            return_value=httpx.Response(404)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/post/nonexistent")

                assert response.status == 51  # Gemini NotFound

    @respx.mock
    def test_post_server_error(self, mock_settings):
        """Test handling of server errors."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/error-post/").mock(
            return_value=httpx.Response(500)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/post/error-post")

                assert response.status == 40  # Gemini TemporaryFailure


class TestPageRoute:
    """Tests for the page route."""

    @respx.mock
    def test_page_returns_content(self, sample_page_html, mock_settings):
        """Test that page route returns converted content."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/about/").mock(
            return_value=httpx.Response(200, text=sample_page_html)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/page/about")

                assert response.is_success
                assert "About Me" in response.body

    @respx.mock
    def test_page_excludes_date(self, sample_post_html, mock_settings):
        """Test that page does NOT include date (unlike posts)."""
        from xitzin.testing import TestClient

        # Even if HTML has a date, pages shouldn't show it
        respx.get("https://test.bearblog.dev/projects/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/page/projects")

                # The date from sample_post_html is 2024-06-15
                # Pages use include_date=False, so "Published:" shouldn't appear
                assert "Published:" not in response.body


class TestAboutRoute:
    """Tests for the about route."""

    @respx.mock
    def test_about_returns_content(self, sample_rss_feed, mock_settings):
        """Test that about route returns content."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/about")

                assert response.is_success
                assert mock_settings.blog_name in response.body

    @respx.mock
    def test_about_includes_description(self, sample_rss_feed, mock_settings):
        """Test that about includes feed description."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/about")

                # From sample_rss_feed
                assert "test blog for testing purposes" in response.body


class TestFeedRoute:
    """Tests for the Atom feed route."""

    @respx.mock
    def test_feed_returns_atom_xml(self, sample_rss_feed, mock_settings):
        """Test that feed returns Atom XML."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/feed")

                assert response.is_success
                assert response.meta == "application/atom+xml"
                assert '<?xml version="1.0"' in response.body
                assert "<feed" in response.body

    @respx.mock
    def test_feed_includes_entries(self, sample_rss_feed, mock_settings):
        """Test that feed includes entries from RSS."""
        from xitzin.testing import TestClient

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/feed")

                assert "<entry>" in response.body
                assert "First Post" in response.body
                assert "gemini://" in response.body

    @respx.mock
    def test_feed_uses_gemini_host(self, sample_rss_feed, mock_settings):
        """Test that feed uses configured gemini_host."""
        from xitzin.testing import TestClient

        mock_settings.gemini_host = "gemini.example.com"

        respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
                app.state.client = httpx.AsyncClient()
                client = TestClient(app)
                response = client.get("/feed")

                assert "gemini://gemini.example.com" in response.body


class TestCaching:
    """Tests for caching behavior."""

    @respx.mock
    def test_feed_is_cached(self, sample_rss_feed, mock_settings):
        """Test that feed data is cached."""
        from xitzin.testing import TestClient

        route = respx.get("https://test.bearblog.dev/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
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
    def test_post_is_cached(self, sample_post_html, mock_settings):
        """Test that post content is cached."""
        from xitzin.testing import TestClient

        route = respx.get("https://test.bearblog.dev/test-cache/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        with patch("ursaproxy.settings", mock_settings):
            with patch("ursaproxy.fetcher.settings", mock_settings):
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
