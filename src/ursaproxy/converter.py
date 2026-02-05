from bs4 import BeautifulSoup
from markdownify import markdownify
from md2gemini import md2gemini


def html_to_gemtext(html: str) -> str:
    """
    Convert Bearblog HTML to Gemtext.

    Bearblog structure:
    - Content is in <main> element
    - Title is <h1> (extracted separately)
    - Date is in <time> element
    - Nav/footer should be stripped
    """
    soup = BeautifulSoup(html, "html.parser")

    # Bearblog uses <main> for content, not <article>
    main = soup.find("main")
    if not main:
        main = soup.body

    if not main:
        return ""

    # Remove elements we don't want
    for tag in main.find_all(["script", "style", "nav", "footer", "form"]):
        tag.decompose()

    # Remove the h1 (title handled separately)
    if h1 := main.find("h1"):
        h1.decompose()

    # HTML -> Markdown -> Gemtext
    markdown = markdownify(str(main), heading_style="ATX")
    gemtext = md2gemini(markdown, links="paragraph", plain=True)

    return gemtext.strip()


def extract_metadata(html: str) -> tuple[str, str]:
    """
    Extract title and date from Bearblog HTML.

    Returns: (title, date_str)
    """
    soup = BeautifulSoup(html, "html.parser")

    # Title is the first h1
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled"

    # Date is in <time datetime="2026-01-31">
    time_el = soup.find("time")
    if time_el and time_el.get("datetime"):
        date_str = time_el["datetime"]
    elif time_el:
        date_str = time_el.get_text(strip=True)
    else:
        date_str = ""

    return title, date_str


def extract_slug(url: str) -> str:
    """
    Extract slug from Bearblog URL.

    Input:  "https://alanbato.com/el-internetsito/"
    Output: "el-internetsito"
    """
    if not url:
        return ""
    path = url.rstrip("/").split("/")[-1]
    # If it looks like a domain (has a dot), there's no slug
    if "." in path:
        return ""
    return path
