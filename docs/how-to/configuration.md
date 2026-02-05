# Configuration

This guide explains how to configure UrsaProxy using a TOML file or environment variables.

## Prerequisites

- UrsaProxy installed

## Configuration Methods

UrsaProxy supports two configuration methods:

1. **TOML file** (recommended) - Create an `ursaproxy.toml` file
2. **Environment variables** - Set variables in your shell

Settings are loaded in this priority order (highest to lowest):

1. Environment variables
2. `ursaproxy.toml` file in current directory
3. Default values

## Using a TOML File (Recommended)

Create an `ursaproxy.toml` file in your working directory:

```toml
# Required settings
bearblog_url = "https://example.bearblog.dev"
blog_name = "My Gemini Blog"

# TLS certificates (required for serving)
cert_file = "/etc/ssl/cert.pem"
key_file = "/etc/ssl/key.pem"

# Optional settings
gemini_host = "gemini.example.com"
host = "0.0.0.0"
port = 1965
cache_ttl_feed = 300
cache_ttl_post = 1800

# Static pages as a TOML table
[pages]
about = "About Me"
now = "What I Am Doing Now"
uses = "Tools I Use"
```

Then simply run:

```bash
ursaproxy
```

## Using Environment Variables

You can also configure UrsaProxy via environment variables. This is useful for:

- Docker deployments
- CI/CD pipelines
- Overriding TOML settings

## Required Configuration

These must be set (via TOML or environment) for UrsaProxy to start:

### BEARBLOG_URL

The URL of your Bearblog.

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
```

!!! note

    Include the protocol (`https://`) but not a trailing slash.

### BLOG_NAME

The display name for your blog in the Gemini capsule.

```bash
export BLOG_NAME="My Gemini Blog"
```

### CERT_FILE and KEY_FILE

Paths to your TLS certificate and private key.

```bash
export CERT_FILE="/path/to/cert.pem"
export KEY_FILE="/path/to/key.pem"
```

## Optional Configuration

### GEMINI_HOST

The hostname for your Gemini capsule. Used to generate absolute URLs in the Atom feed.

```bash
export GEMINI_HOST="gemini.example.com"
```

If not set, UrsaProxy uses the hostname from incoming requests.

### HOST and PORT

Server binding address and port.

```bash
export HOST="0.0.0.0"  # Listen on all interfaces
export PORT="1965"     # Default Gemini port
```

Default: `localhost:1965`

### PAGES

JSON dictionary of static pages not in your RSS feed.

```bash
export PAGES='{"about": "About Me", "now": "What I Am Doing Now", "uses": "Tools I Use"}'
```

See [Static Pages](static-pages.md) for details.

### Cache TTLs

Control how long content is cached. See [Caching](caching.md) for details.

```bash
export CACHE_TTL_FEED="300"   # Feed cache: 5 minutes
export CACHE_TTL_POST="1800"  # Post cache: 30 minutes
```

## Overriding TOML with Environment Variables

Environment variables always take precedence over TOML settings. This is useful for:

- Secrets management (don't commit passwords to TOML)
- Per-environment overrides
- Docker/container deployments

```bash
# Override blog name from TOML
export BLOG_NAME="Production Blog"
ursaproxy
```

## Using a .env File

For Docker or environments without TOML support, use a `.env` file:

```bash
# .env
BEARBLOG_URL=https://example.bearblog.dev
BLOG_NAME=My Gemini Blog
CERT_FILE=/etc/ursaproxy/cert.pem
KEY_FILE=/etc/ursaproxy/key.pem
GEMINI_HOST=gemini.example.com
PAGES={"about": "About", "now": "Now"}
CACHE_TTL_FEED=300
CACHE_TTL_POST=1800
```

Load it before running:

```bash
export $(cat .env | xargs)
ursaproxy
```

Or use a tool like `direnv` or `dotenv`.

!!! tip "Prefer TOML for local development"

    The `ursaproxy.toml` file is cleaner and doesn't require manual loading.

## Verification

Check your configuration by starting UrsaProxy:

```bash
ursaproxy
```

If configuration is missing, you'll see an error like:

```
pydantic_settings.sources.EnvSettingsError: environment variable "BEARBLOG_URL" is required
```

## See Also

- [Configuration Reference](../reference/configuration.md) - Complete configuration specification
- [Caching](caching.md) - Cache configuration details
- [Static Pages](static-pages.md) - Adding custom pages
