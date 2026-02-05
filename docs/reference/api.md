# API Reference

Python module and function documentation for UrsaProxy.

## Module Overview

```
ursaproxy/
├── __init__.py   # App factory, routes, entry point
├── config.py     # Settings and configuration loading
├── fetcher.py    # HTTP client
├── converter.py  # HTML to Gemtext
└── cache.py      # TTL cache
```

## ursaproxy

Main module with the app factory and public API.

### Public Exports

The main module exports:

- `create_app(settings)` - Factory function to create app instances
- `Settings` - Configuration class
- `load_settings()` - Load settings from TOML/environment

### create_app

```python
def create_app(settings: Settings) -> Xitzin:
    """Create and configure an UrsaProxy application instance.

    This factory function allows ursaproxy to be embedded in other Xitzin apps
    for virtual hosting scenarios.

    Args:
        settings: Configuration for this ursaproxy instance.

    Returns:
        A configured Xitzin application.
    """
```

**Example - Standalone:**

```python
from ursaproxy import create_app, load_settings

app = create_app(load_settings())
app.run()
```

**Example - Embedding:**

```python
from ursaproxy import create_app, Settings

settings = Settings(
    bearblog_url="https://myblog.bearblog.dev",
    blog_name="My Blog",
)
ursaproxy_app = create_app(settings)
# Mount in your main Xitzin app for virtual hosting
```

### main

::: ursaproxy.main
    options:
      show_source: false
      heading_level: 4

## ursaproxy.config

Configuration module using Pydantic Settings with TOML support.

### Settings

::: ursaproxy.config.Settings
    options:
      show_source: true
      heading_level: 4
      members:
        - bearblog_url
        - blog_name
        - cache_ttl_feed
        - cache_ttl_post
        - pages
        - gemini_host
        - host
        - port
        - cert_file
        - key_file

### load_settings

```python
def load_settings() -> Settings:
    """Load settings from TOML file and/or environment variables.

    Use this when running ursaproxy standalone. For embedding in other apps,
    create a Settings instance directly with the desired configuration.

    Returns:
        Configured Settings instance.
    """
```

**Example:**

```python
from ursaproxy.config import load_settings

settings = load_settings()
print(settings.blog_name)
```

## ursaproxy.fetcher

HTTP client module for fetching Bearblog content.

### Exceptions

::: ursaproxy.fetcher.FetchError
    options:
      show_source: true
      heading_level: 4

::: ursaproxy.fetcher.NotFoundError
    options:
      show_source: true
      heading_level: 4

::: ursaproxy.fetcher.ServerError
    options:
      show_source: true
      heading_level: 4

### Functions

::: ursaproxy.fetcher.fetch_feed
    options:
      show_source: true
      heading_level: 4

::: ursaproxy.fetcher.fetch_html
    options:
      show_source: true
      heading_level: 4

## ursaproxy.converter

HTML to Gemtext conversion module.

### Functions

::: ursaproxy.converter.html_to_gemtext
    options:
      show_source: true
      heading_level: 4

::: ursaproxy.converter.extract_metadata
    options:
      show_source: true
      heading_level: 4

::: ursaproxy.converter.extract_slug
    options:
      show_source: true
      heading_level: 4

## ursaproxy.cache

Simple TTL cache implementation.

### Cache

::: ursaproxy.cache.Cache
    options:
      show_source: true
      heading_level: 4
      members:
        - __init__
        - get
        - set

### cache

::: ursaproxy.cache.cache
    options:
      show_source: false
      heading_level: 4

## Usage Examples

### Using the Converter

```python
from ursaproxy.converter import html_to_gemtext, extract_metadata, extract_slug

html = """
<main>
    <h1>My Post</h1>
    <time datetime="2024-01-15">January 15</time>
    <p>Hello, world!</p>
</main>
"""

# Extract metadata
title, date = extract_metadata(html)
print(f"Title: {title}, Date: {date}")
# Output: Title: My Post, Date: 2024-01-15

# Convert to Gemtext
gemtext = html_to_gemtext(html)
print(gemtext)
# Output: Hello, world!

# Extract slug from URL
slug = extract_slug("https://blog.example.com/my-post/")
print(slug)
# Output: my-post
```

### Using the Cache

```python
from ursaproxy.cache import Cache

cache = Cache(max_size=100)

# Store a value
cache.set("key", "value")

# Retrieve with TTL (seconds)
result = cache.get("key", ttl=300)
print(result)  # "value"

# Expired entries return None
import time
time.sleep(2)
result = cache.get("key", ttl=1)
print(result)  # None (expired)
```

### Using the Fetcher

```python
import asyncio
import httpx
from ursaproxy.fetcher import fetch_feed, fetch_html, NotFoundError

async def main():
    bearblog_url = "https://example.bearblog.dev"

    async with httpx.AsyncClient() as client:
        # Fetch RSS feed
        feed = await fetch_feed(client, bearblog_url)
        print(f"Blog: {feed.feed.title}")

        # Fetch a post
        try:
            html = await fetch_html(client, bearblog_url, "my-post")
            print(f"Got {len(html)} bytes")
        except NotFoundError:
            print("Post not found")

asyncio.run(main())
```

## See Also

- [Architecture](../explanation/architecture.md) - How modules work together
- [Conversion Pipeline](../explanation/conversion-pipeline.md) - Conversion details
