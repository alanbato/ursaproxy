# Customizing Templates

In this tutorial, you'll learn how to customize UrsaProxy's Jinja2 templates to personalize your Gemini capsule.

## What You'll Learn

- How UrsaProxy's template system works
- How to override default templates
- How to add custom content to your pages

## Prerequisites

- Completed [Your First Proxy](your-first-proxy.md) tutorial
- Basic familiarity with Jinja2 templates

## Understanding the Template System

UrsaProxy uses Jinja2 templates to generate Gemtext. The default templates are bundled with the package:

| Template | Purpose |
|----------|---------|
| `index.gmi` | Landing page with posts and links |
| `post.gmi` | Individual post/page display |
| `about.gmi` | About page |
| `feed.xml` | Atom feed generation |

## Step 1: Examine the Default Templates

Let's look at what the default templates contain. The `index.gmi` template renders:

```jinja
# {{ blog_name }}

{{ description }}

{% if pages %}
## Pages

{% for slug, title in pages.items() %}
=> /page/{{ slug }} {{ title }}
{% endfor %}
{% endif %}

## Recent Posts

{% for post in posts %}
=> /post/{{ post.slug }} {{ post.date }} {{ post.title }}
{% endfor %}

## More

=> /about About
=> /feed Atom Feed
```

The `post.gmi` template:

```jinja
# {{ title }}

{% if date %}
{{ date }}

{% endif %}
{{ content }}

=> {{ web_url }} View on web
```

## Step 2: Create a Custom Templates Directory

To override templates, create a `templates` directory in your project:

```bash
mkdir templates
```

## Step 3: Create Custom Templates

Copy and modify the templates you want to customize. Let's create a custom index page:

```bash
# Create templates/index.gmi
cat > templates/index.gmi << 'EOF'
# {{ blog_name }}

Welcome to my Gemini capsule!

{{ description }}

---

{% if pages %}
## Navigation

{% for slug, title in pages.items() %}
=> /page/{{ slug }} {{ title }}
{% endfor %}

{% endif %}
## Latest Writing

{% for post in posts %}
=> /post/{{ post.slug }} {{ post.date }} - {{ post.title }}
{% endfor %}

---

## Subscribe

=> /feed Atom Feed

## About

=> /about Learn more about this capsule

---

Thanks for visiting!
EOF
```

## Step 4: Override the Post Template

Create a custom post template with a different footer:

```bash
cat > templates/post.gmi << 'EOF'
# {{ title }}

{% if date %}
Published: {{ date }}

---

{% endif %}
{{ content }}

---

## Links

=> {{ web_url }} Read on the web
=> / Back to home
=> /feed Subscribe via Atom
EOF
```

## Step 5: Use Custom Templates

Currently, UrsaProxy uses bundled templates. To use custom templates, you would need to modify the application or contribute a feature to support custom template directories.

!!! note "Feature Request"

    Custom template directory support is a planned feature. For now, you can fork UrsaProxy and modify the templates directly in `src/ursaproxy/templates/`.

## Template Variables Reference

### Index Template (`index.gmi`)

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | Blog display name |
| `description` | `str` | Blog description from feed |
| `pages` | `dict[str, str]` | Static pages (slug -> title) |
| `posts` | `list[dict]` | Recent posts |
| `posts[].slug` | `str` | Post URL slug |
| `posts[].title` | `str` | Post title |
| `posts[].date` | `str` | Publication date |

### Post Template (`post.gmi`)

| Variable | Type | Description |
|----------|------|-------------|
| `title` | `str` | Post/page title |
| `date` | `str` | Publication date (empty for pages) |
| `content` | `str` | Converted Gemtext content |
| `web_url` | `str` | Original Bearblog URL |

### About Template (`about.gmi`)

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | Blog display name |
| `description` | `str` | Blog description |
| `bearblog_url` | `str` | Original Bearblog URL |

### Feed Template (`feed.xml`)

| Variable | Type | Description |
|----------|------|-------------|
| `blog_name` | `str` | Blog display name |
| `base_url` | `str` | Gemini base URL |
| `updated` | `str` | Last update timestamp (ISO 8601) |
| `entries` | `list[dict]` | Feed entries |

## Gemtext Formatting Tips

When writing Gemtext templates:

1. **Headings** use `#`, `##`, `###` (max 3 levels)
2. **Links** must be on their own line: `=> url text`
3. **Lists** use `* ` prefix
4. **Preformatted** blocks use triple backticks
5. **No inline formatting** (no bold, italic, etc.)

Example of valid Gemtext:

```gemtext
# Main Heading

This is a paragraph of text.

## Subheading

* First item
* Second item

=> gemini://example.com/ A link

> A quote block

```code
Preformatted text
```
```

## Next Steps

<div class="grid cards" markdown>

-   :material-cog: **Configuration**

    ---

    Explore all configuration options.

    [:octicons-arrow-right-24: Configuration Guide](../how-to/configuration.md)

-   :material-lightbulb: **Conversion Pipeline**

    ---

    Understand how HTML becomes Gemtext.

    [:octicons-arrow-right-24: Conversion Pipeline](../explanation/conversion-pipeline.md)

</div>
