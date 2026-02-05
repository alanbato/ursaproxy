# UrsaProxy

A Bearblog-to-Gemini proxy built with [Xitzin](https://xitzin.readthedocs.io). UrsaProxy fetches content from a Bearblog RSS feed and HTML pages, converts them to Gemtext format, and serves them over the Gemini protocol.

```bash
# Set up your environment
export BEARBLOG_URL="https://example.bearblog.dev"
export BLOG_NAME="My Gemini Blog"
export CERT_FILE="/path/to/cert.pem"
export KEY_FILE="/path/to/key.pem"

# Start the proxy
ursaproxy
```

Your Bearblog is now available at `gemini://localhost:1965/`.

## Key Features

<div class="grid cards" markdown>

-   :material-sync: **Automatic Conversion**

    ---

    Fetches Bearblog content and converts HTML to clean Gemtext through a Markdown intermediate format.

-   :material-cached: **Smart Caching**

    ---

    Configurable TTL caching for feed and post data to reduce load on your Bearblog.

-   :material-rss: **Atom Feeds**

    ---

    Generates Atom feeds with Gemini URLs for feed readers in the Geminispace.

-   :material-file-document-multiple: **Static Pages**

    ---

    Support for static pages like "About" or "Now" that aren't in your RSS feed.

</div>

## How It Works

| Bearblog (HTTP) | UrsaProxy | Gemini |
|-----------------|-----------|--------|
| RSS Feed | Fetched & parsed | Index page with posts |
| HTML Pages | Converted to Gemtext | Clean text content |
| Images & styles | Stripped | Text-only output |

## Installation

=== "uv"

    ```bash
    uv add ursaproxy
    ```

=== "pip"

    ```bash
    pip install ursaproxy
    ```

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch: **Quick Start**

    ---

    Get your Bearblog on Gemini in under 5 minutes.

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-school: **Tutorials**

    ---

    Step-by-step guides to learn UrsaProxy.

    [:octicons-arrow-right-24: Tutorials](tutorials/index.md)

-   :material-book-open-variant: **How-to Guides**

    ---

    Solve specific problems and configure features.

    [:octicons-arrow-right-24: How-to Guides](how-to/index.md)

-   :material-api: **Reference**

    ---

    Technical details and configuration options.

    [:octicons-arrow-right-24: Reference](reference/index.md)

</div>
