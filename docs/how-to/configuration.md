# Configuration

This guide explains how to configure UrsaProxy using environment variables.

## Prerequisites

- UrsaProxy installed
- Access to set environment variables

## Required Configuration

These variables must be set for UrsaProxy to start:

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

## Using a .env File

For convenience, create a `.env` file:

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
