# Static Pages

This guide explains how to add static pages to your Gemini capsule that aren't in your Bearblog RSS feed.

## The Problem

Your Bearblog may have pages like "About", "Now", or "Uses" that aren't blog posts and don't appear in the RSS feed. UrsaProxy can serve these, but it needs to know they exist.

## Prerequisites

- UrsaProxy configured and running
- Static pages published on your Bearblog

## Step 1: Identify Your Static Pages

Check which pages exist on your Bearblog. Common examples:

| Bearblog URL | Slug |
|--------------|------|
| `https://blog.example.com/about/` | `about` |
| `https://blog.example.com/now/` | `now` |
| `https://blog.example.com/uses/` | `uses` |
| `https://blog.example.com/projects/` | `projects` |

The slug is the last part of the URL path (without slashes).

## Step 2: Configure the PAGES Variable

Set the `PAGES` environment variable as a JSON dictionary mapping slugs to display titles:

```bash
export PAGES='{"about": "About Me", "now": "What I Am Doing Now", "uses": "Tools I Use"}'
```

!!! warning "JSON Formatting"

    The value must be valid JSON. Use double quotes for keys and values, and ensure proper escaping if your shell requires it.

## Step 3: Restart UrsaProxy

The configuration is read at startup:

```bash
# Stop the running server (Ctrl+C)
# Start it again
ursaproxy
```

## Step 4: Verify

Connect to your Gemini capsule and check:

1. The landing page should show links to your static pages
2. Navigate to `/page/about` (or your page slug) to view the content

Example landing page:

```gemtext
# My Gemini Blog

A personal blog.

## Pages

=> /page/about About Me
=> /page/now What I Am Doing Now
=> /page/uses Tools I Use

## Recent Posts
...
```

## Route Differences

Static pages and blog posts use different routes:

| Type | Route | Shows Date |
|------|-------|------------|
| Blog post | `/post/{slug}` | Yes |
| Static page | `/page/{slug}` | No |

The `/about` route (without `/page/` prefix) shows metadata from your feed, not the page content.

## Example: Complete Configuration

```bash
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Gemini Blog"
export CERT_FILE="./cert.pem"
export KEY_FILE="./key.pem"
export PAGES='{"about": "About Me", "now": "Now", "uses": "Uses", "projects": "Projects", "contact": "Contact"}'
```

## Troubleshooting

### Page Not Found

If you get a "not found" error:

1. Verify the page exists on your Bearblog
2. Check the slug matches exactly (case-sensitive)
3. Ensure your Bearblog URL is correct

### JSON Parse Error

If UrsaProxy fails to start with a JSON error:

1. Validate your JSON with a tool like `jq`:
   ```bash
   echo '{"about": "About"}' | jq
   ```
2. Check for unescaped quotes or special characters

## See Also

- [Configuration](configuration.md) - All configuration options
- [Routes Reference](../reference/routes.md) - Route documentation
