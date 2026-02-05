# API Reference

Python module and function documentation for UrsaProxy.

## Module Overview

```
ursaproxy/
├── __init__.py   # App, routes, entry point
├── config.py     # Settings
├── fetcher.py    # HTTP client
├── converter.py  # HTML to Gemtext
└── cache.py      # TTL cache
```

## ursaproxy

Main module with the Xitzin application and route handlers.

### Application

::: ursaproxy.app
    options:
      show_source: false
      heading_level: 4

### Entry Point

::: ursaproxy.main
    options:
      show_source: false
      heading_level: 4

## ursaproxy.config

Configuration module using Pydantic Settings.

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

### settings

::: ursaproxy.config.settings
    options:
      show_source: false
      heading_level: 4

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
    async with httpx.AsyncClient() as client:
        # Fetch RSS feed
        feed = await fetch_feed(client)
        print(f"Blog: {feed.feed.title}")

        # Fetch a post
        try:
            html = await fetch_html(client, "my-post")
            print(f"Got {len(html)} bytes")
        except NotFoundError:
            print("Post not found")

asyncio.run(main())
```

## See Also

- [Architecture](../explanation/architecture.md) - How modules work together
- [Conversion Pipeline](../explanation/conversion-pipeline.md) - Conversion details
