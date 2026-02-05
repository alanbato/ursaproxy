# UrsaProxy

A Bearblog-to-Gemini proxy built with [Xitzin](https://github.com/alanbato/xitzin). It fetches content from a Bearblog RSS feed and HTML pages, converts them to Gemtext format, and serves them over the Gemini protocol.

## Features

- Proxies Bearblog content to Gemini protocol
- Converts HTML to Gemtext via Markdown intermediate format
- Generates Atom feeds with Gemini URLs
- Configurable TTL caching for feed and post data
- Support for static pages not in RSS feed

## Installation

Requires Python 3.13+.

```bash
# Using uv
uv add ursaproxy

# Using pip
pip install ursaproxy
```

## Configuration

UrsaProxy can be configured via a TOML file or environment variables.

### TOML Configuration (Recommended)

Create an `ursaproxy.toml` file in your working directory:

```toml
bearblog_url = "https://example.bearblog.dev"
blog_name = "My Gemini Blog"
cert_file = "/path/to/cert.pem"
key_file = "/path/to/key.pem"

# Optional settings
gemini_host = "gemini.example.com"
cache_ttl_feed = 300
cache_ttl_post = 1800
host = "localhost"
port = 1965

[pages]
about = "About Me"
now = "What I am doing now"
```

### Environment Variables

Environment variables override TOML settings:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BEARBLOG_URL` | Yes | - | The Bearblog URL to proxy |
| `BLOG_NAME` | Yes | - | Display name for the blog |
| `CERT_FILE` | No | `None` | Path to TLS certificate file |
| `KEY_FILE` | No | `None` | Path to TLS private key file |
| `PAGES` | No | `{}` | JSON dict of static pages |
| `GEMINI_HOST` | No | `None` | Hostname for Gemini URLs in feed |
| `CACHE_TTL_FEED` | No | `300` | Feed cache TTL in seconds |
| `CACHE_TTL_POST` | No | `1800` | Post cache TTL in seconds |
| `HOST` | No | `localhost` | Server bind address |
| `PORT` | No | `1965` | Server port |

### Configuration Priority

Settings are loaded in this order (highest to lowest priority):

1. Environment variables
2. `ursaproxy.toml` file
3. Default values

## Usage

### Standalone

```bash
ursaproxy
```

The server will start on `gemini://localhost:1965/` by default.

### As a Library

UrsaProxy can be embedded in other Xitzin applications for virtual hosting:

```python
from ursaproxy import create_app, Settings

# Create settings programmatically
settings = Settings(
    bearblog_url="https://myblog.bearblog.dev",
    blog_name="My Blog",
)

# Create the app
app = create_app(settings)

# Mount in your main Xitzin app or run directly
app.run(certfile="cert.pem", keyfile="key.pem")
```

Or load settings from TOML/environment:

```python
from ursaproxy import create_app, load_settings

app = create_app(load_settings())
```

### Routes

| Route | Description |
|-------|-------------|
| `/` | Landing page with recent posts and page links |
| `/post/{slug}` | Individual blog post with date |
| `/page/{slug}` | Static page (without date) |
| `/about` | About page from feed metadata |
| `/feed` | Atom feed with Gemini URLs |

## Development

For contributing, clone the repository and install with dev dependencies:

```bash
git clone https://github.com/alanbato/ursaproxy.git
cd ursaproxy
uv sync --group dev --group test
```

### Commands

```bash
# Run linting
uv run ruff check .

# Run linting with auto-fix
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type check
uv run ty check

# Run all pre-commit hooks
uv run pre-commit run --all-files

# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v
```

### Project Structure

```
src/ursaproxy/
├── __init__.py      # Xitzin app, routes, and entry point
├── config.py        # Pydantic settings for environment config
├── fetcher.py       # HTTP client for fetching Bearblog content
├── converter.py     # HTML -> Markdown -> Gemtext pipeline
├── cache.py         # Simple TTL cache implementation
└── templates/       # Jinja2 templates
    ├── index.gmi    # Landing page template
    ├── post.gmi     # Post/page template
    ├── about.gmi    # About page template
    └── feed.xml     # Atom feed template
```

### Testing

The test suite uses pytest with fixtures for offline testing:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_converter.py

# Run with coverage (if installed)
uv run pytest --cov=ursaproxy
```

HTTP requests are mocked using [respx](https://github.com/lundberg/respx), so tests run completely offline.

## How It Works

1. **Feed Fetching**: Fetches RSS feed from `{BEARBLOG_URL}/feed/?type=rss`
2. **HTML Fetching**: Fetches individual pages from `{BEARBLOG_URL}/{slug}/`
3. **Conversion Pipeline**:
   - Parse HTML with BeautifulSoup
   - Extract content from `<main>` element
   - Remove nav, footer, scripts, styles
   - Convert to Markdown with markdownify
   - Convert to Gemtext with md2gemini
4. **Caching**: Feed and posts are cached with configurable TTLs
5. **Serving**: Content served via Gemini protocol using Xitzin

## License

MIT
