from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx
from jinja2 import Environment, PackageLoader
from xitzin import NotFound, Request, Response, TemporaryFailure, Xitzin

from .cache import cache
from .config import Settings, load_settings
from .converter import extract_metadata, extract_slug, html_to_gemtext
from .fetcher import NotFoundError, ServerError, fetch_feed, fetch_html

__all__ = ["create_app", "Settings", "load_settings"]


def _rfc822_to_iso(date_str: str) -> str:
    """Convert RFC 822 date to ISO 8601 format for Atom feeds."""
    if not date_str:
        return datetime.now().isoformat() + "Z"
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError):
        return datetime.now().isoformat() + "Z"


# Template environments
templates = Environment(
    loader=PackageLoader("ursaproxy", "templates"),
    autoescape=False,  # Gemtext doesn't need HTML escaping
)

xml_templates = Environment(
    loader=PackageLoader("ursaproxy", "templates"),
    autoescape=True,  # XML escaping for feed
)


def create_app(settings: Settings) -> Xitzin:
    """Create and configure an UrsaProxy application instance.

    This factory function allows ursaproxy to be embedded in other Xitzin apps
    for virtual hosting scenarios.

    Args:
        settings: Configuration for this ursaproxy instance.

    Returns:
        A configured Xitzin application.

    Example:
        For standalone use::

            from ursaproxy import create_app, load_settings

            app = create_app(load_settings())
            app.run()

        For embedding in another app::

            from ursaproxy import create_app, Settings

            ursaproxy_settings = Settings(
                bearblog_url="https://myblog.bearblog.dev",
                blog_name="My Blog",
            )
            ursaproxy_app = create_app(ursaproxy_settings)
            # Mount ursaproxy_app in your main Xitzin app
    """
    app = Xitzin()
    app.state.settings = settings

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
            feed = await fetch_feed(client, settings.bearblog_url)
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
            html = await fetch_html(client, settings.bearblog_url, slug)
        except NotFoundError as e:
            raise NotFound(str(e)) from e
        except ServerError as e:
            raise TemporaryFailure(str(e)) from e

        title, date = extract_metadata(html)
        content = html_to_gemtext(html)

        template = templates.get_template("post.gmi")
        gemtext = template.render(
            title=title,
            date=date if include_date else None,
            content=content,
            web_url=f"{settings.bearblog_url}/{slug}/",
        )

        cache.set(cache_key, gemtext)
        return gemtext

    @app.gemini("/")
    async def index(request: Request) -> str:
        """Landing page with recent posts and page links."""
        feed = await _get_feed(request.app.state.client)

        posts = []
        for entry in feed.entries[:10]:
            link = getattr(entry, "link", None)
            if not link:
                continue
            slug = extract_slug(link)
            if not slug:
                continue
            date = entry.get("published", "")[:16] if entry.get("published") else ""
            title = getattr(entry, "title", "Untitled")
            posts.append({"slug": slug, "title": title, "date": date})

        template = templates.get_template("index.gmi")
        return template.render(
            blog_name=settings.blog_name,
            description=feed.feed.get("description", ""),
            pages=settings.pages,
            posts=posts,
        )

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

        template = templates.get_template("about.gmi")
        return template.render(
            blog_name=settings.blog_name,
            description=description,
            bearblog_url=settings.bearblog_url,
        )

    @app.gemini("/feed")
    async def feed_route(request: Request) -> Response:
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

            entries.append(
                {
                    "title": getattr(entry, "title", "Untitled"),
                    "url": f"{base_url}/post/{slug}",
                    "published": _rfc822_to_iso(entry.get("published", "")),
                    "summary": getattr(entry, "description", ""),
                }
            )

        template = xml_templates.get_template("feed.xml")
        atom_xml = template.render(
            blog_name=settings.blog_name,
            base_url=base_url,
            updated=updated,
            entries=entries,
        )

        return Response(body=atom_xml, mime_type="application/atom+xml")

    return app


def main() -> None:
    """Entry point for standalone execution."""
    settings = load_settings()
    app = create_app(settings)
    app.run(
        host=settings.host,
        port=settings.port,
        certfile=settings.cert_file,
        keyfile=settings.key_file,
    )
