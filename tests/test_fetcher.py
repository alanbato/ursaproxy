"""Tests for the fetcher module."""

import httpx
import pytest

from ursaproxy.fetcher import (
    FetchError,
    NotFoundError,
    ServerError,
    _fetch,
    fetch_feed,
    fetch_html,
)

TEST_BEARBLOG_URL = "https://test.bearblog.dev"


class TestFetchErrors:
    """Tests for fetch error classes."""

    def test_fetch_error_is_base(self):
        """Test that FetchError is the base exception."""
        assert issubclass(NotFoundError, FetchError)
        assert issubclass(ServerError, FetchError)

    def test_not_found_error_message(self):
        """Test NotFoundError message."""
        error = NotFoundError("Resource not found")
        assert str(error) == "Resource not found"

    def test_server_error_message(self):
        """Test ServerError message."""
        error = ServerError("Internal server error")
        assert str(error) == "Internal server error"


class TestInternalFetch:
    """Tests for the internal _fetch function."""

    @pytest.mark.asyncio
    async def test_fetch_success(self, respx_mock):
        """Test successful fetch."""
        respx_mock.get("https://example.com/test").mock(
            return_value=httpx.Response(200, text="Success")
        )

        async with httpx.AsyncClient() as client:
            response = await _fetch(client, "https://example.com/test", "Not found")

        assert response.status_code == 200
        assert response.text == "Success"

    @pytest.mark.asyncio
    async def test_fetch_404_raises_not_found(self, respx_mock):
        """Test that 404 raises NotFoundError."""
        respx_mock.get("https://example.com/missing").mock(
            return_value=httpx.Response(404)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(NotFoundError) as exc_info:
                await _fetch(
                    client, "https://example.com/missing", "Custom not found message"
                )

        assert str(exc_info.value) == "Custom not found message"

    @pytest.mark.asyncio
    async def test_fetch_500_raises_server_error(self, respx_mock):
        """Test that 5xx raises ServerError."""
        respx_mock.get("https://example.com/error").mock(
            return_value=httpx.Response(500)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/error", "Not found")

        assert "Server error 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_502_raises_server_error(self, respx_mock):
        """Test that 502 Bad Gateway raises ServerError."""
        respx_mock.get("https://example.com/error").mock(
            return_value=httpx.Response(502)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/error", "Not found")

        assert "Server error 502" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_400_raises_server_error(self, respx_mock):
        """Test that 4xx (non-404) raises ServerError."""
        respx_mock.get("https://example.com/bad").mock(return_value=httpx.Response(400))

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/bad", "Not found")

        assert "HTTP error 400" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_403_raises_server_error(self, respx_mock):
        """Test that 403 Forbidden raises ServerError."""
        respx_mock.get("https://example.com/forbidden").mock(
            return_value=httpx.Response(403)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/forbidden", "Not found")

        assert "HTTP error 403" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_network_error(self, respx_mock):
        """Test that network errors raise ServerError."""
        respx_mock.get("https://example.com/timeout").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/timeout", "Not found")

        assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_timeout_error(self, respx_mock):
        """Test that timeout errors raise ServerError."""
        respx_mock.get("https://example.com/slow").mock(
            side_effect=httpx.ReadTimeout("Read timed out")
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError) as exc_info:
                await _fetch(client, "https://example.com/slow", "Not found")

        assert "Network error" in str(exc_info.value)


class TestFetchFeed:
    """Tests for fetch_feed function."""

    @pytest.mark.asyncio
    async def test_fetch_feed_success(self, respx_mock, sample_rss_feed):
        """Test successful feed fetch and parse."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        async with httpx.AsyncClient() as client:
            feed = await fetch_feed(client, TEST_BEARBLOG_URL)

        assert feed.feed.title == "Test Blog"
        assert len(feed.entries) == 3
        assert feed.entries[0].title == "First Post"

    @pytest.mark.asyncio
    async def test_fetch_feed_returns_feedparser_dict(
        self, respx_mock, sample_rss_feed
    ):
        """Test that feed returns a FeedParserDict."""
        import feedparser

        respx_mock.get(f"{TEST_BEARBLOG_URL}/feed/?type=rss").mock(
            return_value=httpx.Response(200, text=sample_rss_feed)
        )

        async with httpx.AsyncClient() as client:
            feed = await fetch_feed(client, TEST_BEARBLOG_URL)

        assert isinstance(feed, feedparser.FeedParserDict)

    @pytest.mark.asyncio
    async def test_fetch_feed_404(self, respx_mock):
        """Test feed 404 raises NotFoundError."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/feed/?type=rss").mock(
            return_value=httpx.Response(404)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(NotFoundError) as exc_info:
                await fetch_feed(client, TEST_BEARBLOG_URL)

        assert "Feed not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_feed_server_error(self, respx_mock):
        """Test feed server error raises ServerError."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/feed/?type=rss").mock(
            return_value=httpx.Response(500)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError):
                await fetch_feed(client, TEST_BEARBLOG_URL)


class TestFetchHtml:
    """Tests for fetch_html function."""

    @pytest.mark.asyncio
    async def test_fetch_html_success(self, respx_mock, sample_post_html):
        """Test successful HTML fetch."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/my-post/").mock(
            return_value=httpx.Response(200, text=sample_post_html)
        )

        async with httpx.AsyncClient() as client:
            html = await fetch_html(client, TEST_BEARBLOG_URL, "my-post")

        assert "My Test Post" in html

    @pytest.mark.asyncio
    async def test_fetch_html_constructs_correct_url(self, respx_mock):
        """Test that URL is constructed with trailing slash."""
        # Verify the exact URL format
        route = respx_mock.get(f"{TEST_BEARBLOG_URL}/test-slug/").mock(
            return_value=httpx.Response(200, text="<html></html>")
        )

        async with httpx.AsyncClient() as client:
            await fetch_html(client, TEST_BEARBLOG_URL, "test-slug")

        assert route.called

    @pytest.mark.asyncio
    async def test_fetch_html_404(self, respx_mock):
        """Test HTML 404 raises NotFoundError."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/nonexistent/").mock(
            return_value=httpx.Response(404)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(NotFoundError) as exc_info:
                await fetch_html(client, TEST_BEARBLOG_URL, "nonexistent")

        assert "Page not found: nonexistent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_html_server_error(self, respx_mock):
        """Test HTML server error raises ServerError."""
        respx_mock.get(f"{TEST_BEARBLOG_URL}/error-page/").mock(
            return_value=httpx.Response(503)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(ServerError):
                await fetch_html(client, TEST_BEARBLOG_URL, "error-page")

    @pytest.mark.asyncio
    async def test_fetch_html_returns_text(self, respx_mock):
        """Test that fetch_html returns response text."""
        expected_html = "<html><body>Test content</body></html>"
        respx_mock.get(f"{TEST_BEARBLOG_URL}/test/").mock(
            return_value=httpx.Response(200, text=expected_html)
        )

        async with httpx.AsyncClient() as client:
            result = await fetch_html(client, TEST_BEARBLOG_URL, "test")

        assert result == expected_html
