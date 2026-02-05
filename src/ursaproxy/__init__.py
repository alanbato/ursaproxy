from datetime import datetime
from email.utils import parsedate_to_datetime
from html import escape

import httpx
from xitzin import NotFound, Request, Response, TemporaryFailure, Xitzin

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

    lines.extend(["", "## Recent Posts", "=> /feed Atom Feed", ""])

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


def _rfc822_to_iso(date_str: str) -> str:
    """Convert RFC 822 date to ISO 8601 format for Atom feeds."""
    if not date_str:
        return datetime.now().isoformat() + "Z"
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError):
        return datetime.now().isoformat() + "Z"


@app.gemini("/feed")
async def feed(request: Request) -> Response:
    """Atom feed with Gemini URLs."""
    rss = await _get_feed(request.app.state.client)

    # Use configured gemini_host or fall back to request hostname
    host = settings.gemini_host or request.hostname or "localhost"
    base_url = f"gemini://{host}"

    # Get the most recent update time
    updated = _rfc822_to_iso(rss.feed.get("updated", ""))

    entries = []
    for entry in rss.entries:
        link = getattr(entry, "link", None)
        if not link:
            continue
        slug = extract_slug(link)
        if not slug:
            continue

        title = escape(getattr(entry, "title", "Untitled"))
        summary = escape(getattr(entry, "description", ""))
        published = _rfc822_to_iso(entry.get("published", ""))
        entry_url = f"{base_url}/post/{slug}"

        entries.append(f"""  <entry>
    <title>{title}</title>
    <link href="{entry_url}" rel="alternate"/>
    <id>{entry_url}</id>
    <published>{published}</published>
    <updated>{published}</updated>
    <summary>{summary}</summary>
  </entry>""")

    atom_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{escape(settings.blog_name)}</title>
  <link href="{base_url}/" rel="alternate"/>
  <link href="{base_url}/feed" rel="self"/>
  <id>{base_url}/</id>
  <updated>{updated}</updated>
{chr(10).join(entries)}
</feed>"""

    return Response(body=atom_xml, mime_type="application/atom+xml")


def main() -> None:
    """Entry point."""
    app.run(
        host=settings.host,
        port=settings.port,
        certfile=settings.cert_file,
        keyfile=settings.key_file,
    )
