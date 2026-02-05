import feedparser
import httpx


class FetchError(Exception):
    """Base error for fetch operations."""


class NotFoundError(FetchError):
    """Resource not found (404)."""


class ServerError(FetchError):
    """Server or network error."""


async def _fetch(
    client: httpx.AsyncClient, url: str, not_found_msg: str
) -> httpx.Response:
    """Fetch URL with standardized error handling."""
    try:
        response = await client.get(url)
        if response.status_code == 404:
            raise NotFoundError(not_found_msg)
        if response.status_code >= 500:
            raise ServerError(f"Server error {response.status_code}")
        if response.status_code >= 400:
            raise ServerError(f"HTTP error {response.status_code}")
        return response
    except httpx.HTTPStatusError as e:
        raise ServerError(f"HTTP error: {e}") from e
    except httpx.RequestError as e:
        raise ServerError(f"Network error: {e}") from e


async def fetch_feed(
    client: httpx.AsyncClient, bearblog_url: str
) -> feedparser.FeedParserDict:
    """Fetch RSS feed from Bearblog.

    Args:
        client: HTTP client instance.
        bearblog_url: Base URL of the Bearblog site.
    """
    url = f"{bearblog_url}/feed/?type=rss"
    response = await _fetch(client, url, f"Feed not found at {url}")
    return feedparser.parse(response.text)


async def fetch_html(client: httpx.AsyncClient, bearblog_url: str, slug: str) -> str:
    """Fetch HTML page from Bearblog.

    Args:
        client: HTTP client instance.
        bearblog_url: Base URL of the Bearblog site.
        slug: Page slug (without leading/trailing slashes).

    Note: Bearblog URLs have trailing slashes: /{slug}/
    """
    url = f"{bearblog_url}/{slug}/"
    response = await _fetch(client, url, f"Page not found: {slug}")
    return response.text
