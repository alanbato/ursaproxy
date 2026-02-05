"""Tests for the converter module."""

import pytest

from ursaproxy.converter import extract_metadata, extract_slug, html_to_gemtext


class TestHtmlToGemtext:
    """Tests for HTML to Gemtext conversion."""

    def test_basic_conversion(self, sample_post_html):
        """Test basic HTML to Gemtext conversion."""
        result = html_to_gemtext(sample_post_html)

        # Should contain paragraph content
        assert "first paragraph" in result
        assert "another paragraph" in result

        # Should contain subheading
        assert "Subheading" in result

        # Should NOT contain h1 (extracted separately)
        assert "My Test Post" not in result

    def test_removes_nav_and_footer(self, sample_post_html):
        """Test that nav and footer elements are removed."""
        result = html_to_gemtext(sample_post_html)

        assert "Home" not in result  # From nav
        assert "Footer content" not in result

    def test_removes_script_elements(self, sample_post_html):
        """Test that script elements are removed."""
        result = html_to_gemtext(sample_post_html)
        assert "console.log" not in result
        assert "should be removed" not in result

    def test_fallback_to_body(self, sample_html_no_main):
        """Test fallback to body when main element is missing."""
        result = html_to_gemtext(sample_html_no_main)

        # Should still process body content
        assert "Content directly in body" in result

    def test_empty_html_returns_empty_string(self, minimal_html):
        """Test that minimal/empty HTML returns empty string."""
        result = html_to_gemtext(minimal_html)
        assert result == ""

    def test_no_body_returns_empty_string(self):
        """Test that HTML without body returns empty string."""
        html = "<html><head></head></html>"
        result = html_to_gemtext(html)
        assert result == ""

    def test_link_conversion(self, sample_post_html):
        """Test that links are converted properly."""
        result = html_to_gemtext(sample_post_html)

        # md2gemini with links="paragraph" puts links at end of paragraph
        assert "example.com" in result

    def test_removes_style_elements(self):
        """Test that style elements are removed."""
        html = """
        <html><body><main>
        <h1>Title</h1>
        <style>.test { color: red; }</style>
        <p>Content</p>
        </main></body></html>
        """
        result = html_to_gemtext(html)
        assert ".test" not in result
        assert "color: red" not in result
        assert "Content" in result

    def test_removes_form_elements(self):
        """Test that form elements are removed."""
        html = """
        <html><body><main>
        <h1>Title</h1>
        <form><input type="text" name="email"><button>Submit</button></form>
        <p>Content after form</p>
        </main></body></html>
        """
        result = html_to_gemtext(html)
        assert "Submit" not in result
        assert "Content after form" in result

    def test_preserves_headings(self):
        """Test that h2-h6 headings are preserved."""
        html = """
        <html><body><main>
        <h1>Title</h1>
        <h2>Section One</h2>
        <p>Content</p>
        <h3>Subsection</h3>
        <p>More content</p>
        </main></body></html>
        """
        result = html_to_gemtext(html)
        assert "Section One" in result
        assert "Subsection" in result

    def test_output_is_stripped(self):
        """Test that output is stripped of leading/trailing whitespace."""
        html = """
        <html><body><main>
        <h1>Title</h1>
        <p>Content</p>
        </main></body></html>
        """
        result = html_to_gemtext(html)
        assert not result.startswith("\n")
        assert not result.endswith("\n")


class TestExtractMetadata:
    """Tests for metadata extraction."""

    def test_extracts_title_from_h1(self, sample_post_html):
        """Test that title is extracted from h1."""
        title, _ = extract_metadata(sample_post_html)
        assert title == "My Test Post"

    def test_extracts_date_from_datetime_attr(self, sample_post_html):
        """Test that date is extracted from datetime attribute."""
        _, date = extract_metadata(sample_post_html)
        assert date == "2024-06-15"

    def test_fallback_title_when_no_h1(self):
        """Test fallback to 'Untitled' when no h1 present."""
        html = "<html><body><p>No heading here</p></body></html>"
        title, _ = extract_metadata(html)
        assert title == "Untitled"

    def test_empty_date_when_no_time_element(self, sample_html_no_date):
        """Test empty date when no time element present."""
        _, date = extract_metadata(sample_html_no_date)
        assert date == ""

    def test_date_from_time_text_content(self, sample_html_time_text):
        """Test date extraction from time element text when no datetime attr."""
        _, date = extract_metadata(sample_html_time_text)
        assert date == "January 1, 2024"

    def test_title_strips_whitespace(self):
        """Test that title text is stripped of whitespace."""
        html = "<html><body><h1>   Title with spaces   </h1></body></html>"
        title, _ = extract_metadata(html)
        assert title == "Title with spaces"


class TestExtractSlug:
    """Tests for slug extraction from URLs."""

    def test_extract_slug_basic(self):
        """Test basic slug extraction."""
        url = "https://example.bearblog.dev/my-post/"
        assert extract_slug(url) == "my-post"

    def test_extract_slug_without_trailing_slash(self):
        """Test slug extraction without trailing slash."""
        url = "https://example.bearblog.dev/my-post"
        assert extract_slug(url) == "my-post"

    def test_extract_slug_domain_only(self):
        """Test that domain-only URLs return empty string."""
        url = "https://example.bearblog.dev/"
        assert extract_slug(url) == ""

    def test_extract_slug_empty_string(self):
        """Test that empty string returns empty string."""
        assert extract_slug("") == ""

    def test_extract_slug_with_subdomain(self):
        """Test slug extraction with custom domain."""
        url = "https://blog.example.com/my-post/"
        assert extract_slug(url) == "my-post"

    def test_extract_slug_complex_path(self):
        """Test that only last path segment is extracted."""
        url = "https://example.com/blog/posts/my-post/"
        assert extract_slug(url) == "my-post"

    def test_extract_slug_with_numbers(self):
        """Test slug with numbers."""
        url = "https://example.com/post-2024-01/"
        assert extract_slug(url) == "post-2024-01"

    def test_extract_slug_domain_with_dot_returns_empty(self):
        """Test that domain-like paths (with dots) return empty."""
        # This handles cases where the "slug" looks like a domain
        url = "https://example.com"
        assert extract_slug(url) == ""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://a.com/hello-world/", "hello-world"),
            ("https://a.com/test/", "test"),
            ("https://a.com/", ""),
            ("https://a.com", ""),
            ("", ""),
            ("https://blog.example.dev/my-awesome-post/", "my-awesome-post"),
        ],
    )
    def test_extract_slug_parametrized(self, url, expected):
        """Parametrized test for various URL formats."""
        assert extract_slug(url) == expected
