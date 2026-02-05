# Gemini Protocol

This article explains the Gemini protocol, its design philosophy, and why UrsaProxy exists to bridge Bearblog to this alternative internet space.

## What is Gemini?

Gemini is a lightweight internet protocol designed as a middle ground between Gopher (minimal but limited) and the modern web (powerful but complex). It was created in 2019 by "solderpunk" as a response to the increasing complexity of the web.

Key characteristics:

- **Text-focused**: Content is primarily text with minimal markup
- **Privacy-respecting**: No cookies, no JavaScript, no tracking
- **TLS mandatory**: All connections are encrypted
- **Simple by design**: Intentionally limited to prevent feature creep

## Gemini vs HTTP

| Feature | HTTP/Web | Gemini |
|---------|----------|--------|
| Content types | HTML, CSS, JS, images, video | Gemtext (text), optional images |
| Styling | CSS, JavaScript | None (client decides) |
| Tracking | Cookies, scripts, fingerprinting | Not possible |
| Encryption | Optional (HTTPS) | Mandatory (TLS) |
| Complexity | High | Low |
| Interactivity | Forms, AJAX, WebSockets | Single input prompt |

## The Gemtext Format

Gemini uses "Gemtext" as its native document format. It's similar to Markdown but simpler:

```gemtext
# Heading

This is a paragraph. All text on a line is one paragraph.

=> gemini://example.com/ Link text must be on its own line
=> /relative/path Another link

## Subheading

* List item one
* List item two

> A quote block

```preformatted
Code or ASCII art goes here
```
```

### Key Differences from Markdown

1. **No inline formatting** - No bold, italic, or inline code
2. **Links are block-level** - Each link must be on its own line
3. **Three heading levels** - `#`, `##`, `###` only
4. **No tables** - Use preformatted blocks instead
5. **No images inline** - Images are linked, not embedded

## Why Gemini Exists

The modern web has problems:

1. **Bloat**: Average web pages are several megabytes
2. **Tracking**: Pervasive surveillance through cookies and scripts
3. **Accessibility**: Many sites require modern browsers and fast connections
4. **Complexity**: Building for the web requires extensive knowledge

Gemini addresses these by:

- Keeping pages small (typically under 10KB)
- Making tracking technically impossible
- Working well on slow connections and old hardware
- Being simple enough that anyone can write a client or server

## The Geminispace

The collection of Gemini servers and content is called the "Geminispace." It includes:

- Personal blogs and journals
- Community forums (via aggregators)
- News and link collections
- Interactive fiction
- Documentation

## Why Bridge Bearblog to Gemini?

Bearblog is a minimalist blogging platform that aligns with Gemini's philosophy:

- Simple, text-focused posts
- No complex layouts or JavaScript
- Clean, semantic HTML

UrsaProxy bridges these similar philosophies, letting you:

1. Keep writing on Bearblog (familiar interface)
2. Reach the Geminispace audience
3. Have your content in both spaces without duplication

## Gemini Clients

To browse Geminispace, you need a Gemini client:

| Client | Platform | Notes |
|--------|----------|-------|
| [Lagrange](https://gmi.skyjake.fi/lagrange/) | Windows, Mac, Linux | GUI, feature-rich |
| [Amfora](https://github.com/makew0rld/amfora) | All | Terminal-based |
| [Astromo](https://github.com/alanbato/astronomo) | All | Terminal-based, built with Textual |
| [Kristall](https://github.com/MasterQ32/kristall) | Windows, Mac, Linux | GUI, lightweight |
| [Elaho](https://github.com/nickswalker/Elaho) | iOS | Native iOS app |
| [Deedum](https://github.com/nickswalker/deedum) | Android | Native Android app |

## Further Reading

- [Gemini Protocol Specification](gemini://geminiprotocol.net/docs/specification.gmi) (requires Gemini client)
- [Project Gemini FAQ](https://geminiprotocol.net/docs/faq.html)
- [Gemini Quickstart](https://geminiquickst.art/)

## See Also

- [Architecture](architecture.md) - How UrsaProxy works
- [Conversion Pipeline](conversion-pipeline.md) - HTML to Gemtext conversion
