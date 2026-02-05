# Configuration Reference

Complete reference for all UrsaProxy configuration options.

## Environment Variables

All configuration is via environment variables. UrsaProxy uses Pydantic Settings for validation and parsing.

### Required Variables

These must be set for UrsaProxy to start.

#### BEARBLOG_URL

| | |
|---|---|
| **Type** | `str` |
| **Required** | Yes |
| **Example** | `https://example.bearblog.dev` |

The base URL of your Bearblog. Must include protocol (`http://` or `https://`). Trailing slash is automatically removed.

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
```

#### BLOG_NAME

| | |
|---|---|
| **Type** | `str` |
| **Required** | Yes |
| **Example** | `My Gemini Blog` |

Display name for your blog, shown on the landing page and in the Atom feed.

```bash
export BLOG_NAME="My Gemini Blog"
```

#### CERT_FILE

| | |
|---|---|
| **Type** | `str` |
| **Required** | Yes |
| **Example** | `/etc/ssl/cert.pem` |

Path to your TLS certificate file (PEM format).

```bash
export CERT_FILE="/etc/letsencrypt/live/example.com/fullchain.pem"
```

#### KEY_FILE

| | |
|---|---|
| **Type** | `str` |
| **Required** | Yes |
| **Example** | `/etc/ssl/key.pem` |

Path to your TLS private key file (PEM format).

```bash
export KEY_FILE="/etc/letsencrypt/live/example.com/privkey.pem"
```

### Optional Variables

#### HOST

| | |
|---|---|
| **Type** | `str` |
| **Default** | `localhost` |
| **Example** | `0.0.0.0` |

Network interface to bind to.

- `localhost` - Local connections only
- `0.0.0.0` - All interfaces (for production)

```bash
export HOST="0.0.0.0"
```

#### PORT

| | |
|---|---|
| **Type** | `int` |
| **Default** | `1965` |
| **Example** | `1965` |

Port to listen on. The standard Gemini port is 1965.

```bash
export PORT="1965"
```

#### GEMINI_HOST

| | |
|---|---|
| **Type** | `str \| None` |
| **Default** | `None` |
| **Example** | `gemini.example.com` |

Hostname for generating absolute Gemini URLs in the Atom feed. If not set, uses the hostname from incoming requests.

```bash
export GEMINI_HOST="gemini.example.com"
```

#### PAGES

| | |
|---|---|
| **Type** | `dict[str, str]` (JSON) |
| **Default** | `{}` |
| **Example** | `{"about": "About Me", "now": "Now"}` |

JSON dictionary mapping page slugs to display titles. Used for static pages not in your RSS feed.

```bash
export PAGES='{"about": "About Me", "now": "What I Am Doing Now", "uses": "Tools I Use"}'
```

#### CACHE_TTL_FEED

| | |
|---|---|
| **Type** | `int` |
| **Default** | `300` (5 minutes) |
| **Unit** | Seconds |

How long to cache the RSS feed before fetching again.

```bash
export CACHE_TTL_FEED="600"  # 10 minutes
```

#### CACHE_TTL_POST

| | |
|---|---|
| **Type** | `int` |
| **Default** | `1800` (30 minutes) |
| **Unit** | Seconds |

How long to cache individual post/page content.

```bash
export CACHE_TTL_POST="3600"  # 1 hour
```

## Configuration Examples

### Minimal Configuration

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Blog"
export CERT_FILE="./cert.pem"
export KEY_FILE="./key.pem"
```

### Production Configuration

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Gemini Blog"
export CERT_FILE="/etc/letsencrypt/live/gemini.example.com/fullchain.pem"
export KEY_FILE="/etc/letsencrypt/live/gemini.example.com/privkey.pem"
export HOST="0.0.0.0"
export PORT="1965"
export GEMINI_HOST="gemini.example.com"
export PAGES='{"about": "About", "now": "Now", "uses": "Uses"}'
export CACHE_TTL_FEED="600"
export CACHE_TTL_POST="3600"
```

### Development Configuration

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="Dev Blog"
export CERT_FILE="./cert.pem"
export KEY_FILE="./key.pem"
export CACHE_TTL_FEED="60"   # 1 minute
export CACHE_TTL_POST="60"   # 1 minute
```

## Validation

UrsaProxy validates configuration at startup:

- `BEARBLOG_URL` must start with `http://` or `https://`
- `CERT_FILE` and `KEY_FILE` must point to readable files
- `PAGES` must be valid JSON
- Integer values must be parseable as integers

Invalid configuration produces a Pydantic validation error:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
bearblog_url
  Value error, bearblog_url must start with http:// or https://
```

## See Also

- [How-to: Configuration](../how-to/configuration.md) - Configuration guide
- [How-to: Caching](../how-to/caching.md) - Cache configuration details
