# Quick Start

This guide gets your Bearblog on Gemini as fast as possible.

## Prerequisites

- Python 3.13+
- A Bearblog with an RSS feed
- TLS certificate and key for Gemini

!!! tip "Need a TLS certificate?"

    For local development, you can generate a self-signed certificate:

    ```bash
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
        -days 365 -nodes -subj '/CN=localhost'
    ```

## Step 1: Install UrsaProxy

```bash
uv add ursaproxy
```

## Step 2: Configure Environment

Set the required environment variables:

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Gemini Blog"
export CERT_FILE="./cert.pem"
export KEY_FILE="./key.pem"
```

## Step 3: Start the Proxy

```bash
ursaproxy
```

You should see output indicating the server is running:

```
INFO: Xitzin server listening on localhost:1965
```

## Step 4: Connect

Use a Gemini client to connect:

```bash
# Using amfora
amfora gemini://localhost/

# Using astromo
astromo gemini://localhost/

# Using lagrange
lagrange gemini://localhost/
```

## What You'll See

Your landing page shows:

- Blog name and description
- Links to static pages (if configured)
- Recent posts from your RSS feed

Navigate to any post and you'll see clean Gemtext converted from your Bearblog HTML.

## Available Routes

| Route | Content |
|-------|---------|
| `/` | Landing page with recent posts |
| `/post/{slug}` | Individual blog post |
| `/page/{slug}` | Static page |
| `/about` | About page from feed metadata |
| `/feed` | Atom feed with Gemini URLs |

## Next Steps

<div class="grid cards" markdown>

-   :material-cog: **Configuration**

    ---

    Customize caching, static pages, and more.

    [:octicons-arrow-right-24: Configuration Guide](how-to/configuration.md)

-   :material-school: **Tutorials**

    ---

    Learn UrsaProxy step by step.

    [:octicons-arrow-right-24: Tutorials](tutorials/index.md)

-   :material-rocket-launch: **Deployment**

    ---

    Deploy your proxy to production.

    [:octicons-arrow-right-24: Deployment Guide](how-to/deployment.md)

</div>
