import httpx
from xitzin import NotFound, Request, TemporaryFailure, Xitzin

from .cache import cache
from .config import settings
from .converter import extract_metadata, extract_slug, html_to_gemtext
from .fetcher import NotFoundError, ServerError, fetch_feed, fetch_html

app = Xitzin()


@app.on_startup
async def startup() -> None:
    """Initialize shared HTTP client."""
    app.state.client = httpx.AsyncClient(timeout=30.0)


@app.on_shutdown
async def shutdown() -> None:
    """Close HTTP client."""
    await app.state.client.aclose()


async def _get_feed(client: httpx.AsyncClient):
    """Fetch feed with caching and error handling."""
    if cached := cache.get("feed", settings.cache_ttl_feed):
        return cached

    try:
        feed = await fetch_feed(client)
        cache.set("feed", feed)
        return feed
    except ServerError as e:
        raise TemporaryFailure(str(e)) from e
    except NotFoundError as e:
        raise NotFound(str(e)) from e


async def _render_content(
    client: httpx.AsyncClient,
    slug: str,
    content_type: str,
    include_date: bool = True,
) -> str:
    """Fetch and render content as gemtext with caching."""
    cache_key = f"{content_type}:{slug}"

    if cached := cache.get(cache_key, settings.cache_ttl_post):
        return cached

    try:
        html = await fetch_html(client, slug)
    except NotFoundError as e:
        raise NotFound(str(e)) from e
    except ServerError as e:
        raise TemporaryFailure(str(e)) from e

    title, date = extract_metadata(html)
    content = html_to_gemtext(html)

    date_line = f"Published: {date}\n\n" if include_date and date else ""
    gemtext = f"""# {title}

{date_line}{content}

---
=> / ← Back to index
=> {settings.bearblog_url}/{slug}/ View on web
"""

    cache.set(cache_key, gemtext)
    return gemtext


@app.gemini("/")
async def index(request: Request) -> str:
    """Landing page with recent posts and page links."""
    feed = await _get_feed(request.app.state.client)

    lines = [
        f"# {settings.blog_name}",
        "",
        feed.feed.get("description", ""),
        "",
        "## Pages",
    ]

    for slug, title in settings.pages.items():
        lines.append(f"=> /page/{slug} {title}")

    lines.extend(["", "## Recent Posts"])

    for entry in feed.entries[:10]:
        link = getattr(entry, "link", None)
        if not link:
            continue
        slug = extract_slug(link)
        if not slug:
            continue
        date = entry.get("published", "")[:16] if entry.get("published") else ""
        title = getattr(entry, "title", "Untitled")
        lines.append(f"=> /post/{slug} {title} ({date})")

    return "\n".join(lines)


@app.gemini("/post/{slug}")
async def post(request: Request, slug: str) -> str:
    """Individual blog post."""
    return await _render_content(
        request.app.state.client, slug, "post", include_date=True
    )


@app.gemini("/page/{slug}")
async def page(request: Request, slug: str) -> str:
    """Static page (projects, now, etc.)."""
    return await _render_content(
        request.app.state.client, slug, "page", include_date=False
    )


@app.gemini("/about")
async def about(request: Request) -> str:
    """About page from feed metadata."""
    feed = await _get_feed(request.app.state.client)
    description = feed.feed.get("description", "A personal blog.")

    return f"""# About {settings.blog_name}

{description}

=> / ← Back to index
=> {settings.bearblog_url} Visit on the web
"""


def main() -> None:
    """Entry point."""
    app.run(
        host=settings.host,
        port=settings.port,
        certfile=settings.cert_file,
        keyfile=settings.key_file,
    )
