# Routes Reference

Complete reference for all UrsaProxy routes.

## Route Overview

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page |
| `/post/{slug}` | GET | Blog post |
| `/page/{slug}` | GET | Static page |
| `/about` | GET | About page |
| `/feed` | GET | Atom feed |

## Landing Page

### `GET /`

Returns the landing page with blog name, description, static pages, and recent posts.

**Response**: `text/gemini`

**Template Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | From `BLOG_NAME` setting |
| `description` | `str` | From RSS feed metadata |
| `pages` | `dict[str, str]` | From `PAGES` setting |
| `posts` | `list[dict]` | Recent posts (max 10) |

**Example Response**:

```gemtext
# My Gemini Blog

A personal blog about technology and life.

## Pages

=> /page/about About Me
=> /page/now What I Am Doing Now

## Recent Posts

=> /post/hello-world 2024-01-15 Hello World
=> /post/second-post 2024-01-10 My Second Post

## More

=> /about About
=> /feed Atom Feed
```

## Blog Post

### `GET /post/{slug}`

Returns a blog post converted from Bearblog HTML to Gemtext.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `slug` | `str` | Post URL slug |

**Response**: `text/gemini`

**Cache**: Uses `CACHE_TTL_POST` setting.

**Errors**:

| Status | Condition |
|--------|-----------|
| `51 NOT FOUND` | Post doesn't exist on Bearblog |
| `40 TEMPORARY FAILURE` | Network or server error |

**Example Response**:

```gemtext
# Hello World

2024-01-15

This is my first blog post!

## Introduction

Welcome to my corner of the internet.

=> https://example.bearblog.dev/hello-world/ View on web
```

## Static Page

### `GET /page/{slug}`

Returns a static page. Similar to blog posts but without the date.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `slug` | `str` | Page URL slug |

**Response**: `text/gemini`

**Cache**: Uses `CACHE_TTL_POST` setting.

**Note**: The slug must be listed in the `PAGES` configuration for links to appear on the landing page, but any valid Bearblog page can be accessed directly.

**Example Response**:

```gemtext
# About Me

I'm a software developer who enjoys writing about technology.

## Contact

Feel free to reach out via email.

=> https://example.bearblog.dev/about/ View on web
```

## About Page

### `GET /about`

Returns an about page generated from RSS feed metadata.

**Response**: `text/gemini`

**Template Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | From `BLOG_NAME` setting |
| `description` | `str` | From RSS feed metadata |
| `bearblog_url` | `str` | From `BEARBLOG_URL` setting |

**Note**: This is different from `/page/about`. The `/about` route uses feed metadata, while `/page/about` fetches the actual Bearblog about page.

**Example Response**:

```gemtext
# About My Gemini Blog

A personal blog about technology and life.

=> https://example.bearblog.dev View on Bearblog
```

## Atom Feed

### `GET /feed`

Returns an Atom XML feed with Gemini URLs.

**Response**: `application/atom+xml`

**Template Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | Feed title |
| `base_url` | `str` | Gemini base URL |
| `updated` | `str` | Last update (ISO 8601) |
| `entries` | `list[dict]` | Feed entries |

**URL Generation**: Entry URLs use `GEMINI_HOST` if set, otherwise the request hostname.

**Example Response**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>My Gemini Blog</title>
  <link href="gemini://gemini.example.com/"/>
  <updated>2024-01-15T12:00:00Z</updated>
  <id>gemini://gemini.example.com/</id>
  <entry>
    <title>Hello World</title>
    <link href="gemini://gemini.example.com/post/hello-world"/>
    <id>gemini://gemini.example.com/post/hello-world</id>
    <published>2024-01-15T12:00:00Z</published>
    <summary>First post summary...</summary>
  </entry>
</feed>
```

## Error Responses

UrsaProxy uses standard Gemini status codes:

| Code | Status | Description |
|------|--------|-------------|
| `20` | SUCCESS | Content follows |
| `40` | TEMPORARY FAILURE | Try again later |
| `51` | NOT FOUND | Resource doesn't exist |

### Not Found (51)

Returned when a post or page doesn't exist on Bearblog.

```
51 Page not found: nonexistent-slug
```

### Temporary Failure (40)

Returned for network errors or Bearblog server errors.

```
40 Network error: Connection refused
```

## See Also

- [Configuration Reference](configuration.md) - Settings that affect routes
- [Architecture](../explanation/architecture.md) - How routes are handled
