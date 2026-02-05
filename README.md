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

UrsaProxy is configured via environment variables:

### Required

| Variable | Description |
|----------|-------------|
| `BEARBLOG_URL` | The Bearblog URL to proxy (e.g., `https://example.bearblog.dev`) |
| `BLOG_NAME` | Display name for the blog |
| `CERT_FILE` | Path to TLS certificate file |
| `KEY_FILE` | Path to TLS private key file |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `PAGES` | `{}` | JSON dict of static pages `{"slug": "Title"}` |
| `GEMINI_HOST` | `None` | Hostname for Gemini URLs in feed |
| `CACHE_TTL_FEED` | `300` | Feed cache TTL in seconds (5 min) |
| `CACHE_TTL_POST` | `1800` | Post cache TTL in seconds (30 min) |
| `HOST` | `localhost` | Server bind address |
| `PORT` | `1965` | Server port (Gemini default) |

### Example

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Gemini Blog"
export CERT_FILE="/path/to/cert.pem"
export KEY_FILE="/path/to/key.pem"
export PAGES='{"about": "About Me", "now": "What I am doing now"}'
export GEMINI_HOST="gemini.example.com"
```

## Usage

```bash
ursaproxy
```

The server will start on `gemini://localhost:1965/` by default.

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
# Run all 111 tests
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
