# Installation

UrsaProxy requires Python 3.13 or later.

## Installing UrsaProxy

=== "uv (Recommended)"

    [uv](https://docs.astral.sh/uv/) is a fast Python package manager:

    ```bash
    uv add ursaproxy
    ```

=== "pip"

    Using pip with a virtual environment:

    ```bash
    pip install ursaproxy
    ```

=== "pipx"

    For a globally isolated installation:

    ```bash
    pipx install ursaproxy
    ```

## Verifying Installation

After installation, verify it works:

```bash
ursaproxy --help
```

## Dependencies

UrsaProxy automatically installs these dependencies:

| Package | Purpose |
|---------|---------|
| [xitzin](https://xitzin.readthedocs.io) | Gemini server framework |
| feedparser | RSS/Atom feed parsing |
| httpx | Async HTTP client |
| beautifulsoup4 | HTML parsing |
| markdownify | HTML to Markdown |
| md2gemini | Markdown to Gemtext |
| pydantic-settings | Environment configuration |
| jinja2 | Template rendering |

## Development Installation

To contribute to UrsaProxy:

```bash
git clone https://github.com/alanbato/ursaproxy.git
cd ursaproxy
uv sync --group dev --group test
```

This installs additional tools:

- **ruff** - Linting and formatting
- **ty** - Type checking
- **pytest** - Testing
- **pre-commit** - Git hooks

## Next Steps

Once installed, head to the [Quick Start](quickstart.md) to set up your first proxy.
