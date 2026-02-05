# Changelog

All notable changes to UrsaProxy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-15

### Added

- Initial release of UrsaProxy
- Bearblog-to-Gemini proxy functionality
- HTML to Gemtext conversion pipeline (BeautifulSoup → Markdown → Gemtext)
- RSS feed parsing with feedparser
- Atom feed generation with Gemini URLs
- TTL-based caching for feed and post data
- Support for static pages via `PAGES` configuration
- Jinja2 templates for Gemtext and Atom output
- Environment-based configuration via Pydantic Settings
- Built on Xitzin Gemini framework

### Routes

- `/` - Landing page with recent posts
- `/post/{slug}` - Individual blog posts
- `/page/{slug}` - Static pages
- `/about` - About page from feed metadata
- `/feed` - Atom feed

### Configuration

- `BEARBLOG_URL` - Source blog URL (required)
- `BLOG_NAME` - Display name (required)
- `CERT_FILE` / `KEY_FILE` - TLS certificates (required)
- `PAGES` - Static page definitions
- `GEMINI_HOST` - Hostname for feed URLs
- `CACHE_TTL_FEED` / `CACHE_TTL_POST` - Cache durations

[Unreleased]: https://github.com/alanbato/ursaproxy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alanbato/ursaproxy/releases/tag/v0.1.0
