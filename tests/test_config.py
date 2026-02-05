"""Tests for the config module."""

import pytest
from pydantic import ValidationError

from ursaproxy.config import Settings


class TestSettingsRequired:
    """Tests for required settings."""

    def test_requires_bearblog_url(self, monkeypatch):
        """Test that bearblog_url is required."""
        monkeypatch.setenv("BLOG_NAME", "Test Blog")
        monkeypatch.delenv("BEARBLOG_URL", raising=False)

        with pytest.raises(ValidationError):
            Settings()

    def test_requires_blog_name(self, monkeypatch):
        """Test that blog_name is required."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.delenv("BLOG_NAME", raising=False)

        with pytest.raises(ValidationError):
            Settings()

    def test_loads_required_from_env(self, monkeypatch):
        """Test that required settings load from environment."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "My Test Blog")

        settings = Settings()

        assert settings.bearblog_url == "https://test.bearblog.dev"
        assert settings.blog_name == "My Test Blog"


class TestSettingsDefaults:
    """Tests for default setting values."""

    def test_default_cache_ttl_feed(self, monkeypatch):
        """Test default cache TTL for feed is 5 minutes."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.cache_ttl_feed == 300

    def test_default_cache_ttl_post(self, monkeypatch):
        """Test default cache TTL for posts is 30 minutes."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.cache_ttl_post == 1800

    def test_default_pages_empty(self, monkeypatch):
        """Test default pages is empty dict."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.pages == {}

    def test_default_gemini_host_none(self, monkeypatch):
        """Test default gemini_host is None."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.gemini_host is None

    def test_default_host(self, monkeypatch):
        """Test default host is localhost."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.host == "localhost"

    def test_default_port(self, monkeypatch):
        """Test default port is 1965 (Gemini standard)."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.port == 1965

    def test_default_cert_and_key_none(self, monkeypatch):
        """Test default cert and key files are None."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.cert_file is None
        assert settings.key_file is None


class TestUrlNormalization:
    """Tests for URL normalization."""

    def test_removes_trailing_slash(self, monkeypatch):
        """Test that trailing slash is removed from bearblog_url."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev/")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.bearblog_url == "https://test.bearblog.dev"

    def test_removes_multiple_trailing_slashes(self, monkeypatch):
        """Test that multiple trailing slashes are removed."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev///")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.bearblog_url == "https://test.bearblog.dev"

    def test_preserves_url_without_trailing_slash(self, monkeypatch):
        """Test that URL without trailing slash is preserved."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.bearblog_url == "https://test.bearblog.dev"


class TestUrlValidation:
    """Tests for URL protocol validation."""

    def test_accepts_https_url(self, monkeypatch):
        """Test that https:// URLs are accepted."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.bearblog_url.startswith("https://")

    def test_accepts_http_url(self, monkeypatch):
        """Test that http:// URLs are accepted."""
        monkeypatch.setenv("BEARBLOG_URL", "http://localhost:8000")
        monkeypatch.setenv("BLOG_NAME", "Test")

        settings = Settings()
        assert settings.bearblog_url.startswith("http://")

    def test_rejects_gemini_url(self, monkeypatch):
        """Test that gemini:// URLs are rejected."""
        monkeypatch.setenv("BEARBLOG_URL", "gemini://test.example.com")
        monkeypatch.setenv("BLOG_NAME", "Test")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "must start with http:// or https://" in str(exc_info.value)

    def test_rejects_ftp_url(self, monkeypatch):
        """Test that ftp:// URLs are rejected."""
        monkeypatch.setenv("BEARBLOG_URL", "ftp://files.example.com")
        monkeypatch.setenv("BLOG_NAME", "Test")

        with pytest.raises(ValidationError):
            Settings()

    def test_rejects_url_without_protocol(self, monkeypatch):
        """Test that URLs without protocol are rejected."""
        monkeypatch.setenv("BEARBLOG_URL", "test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")

        with pytest.raises(ValidationError):
            Settings()


class TestPagesConfig:
    """Tests for pages configuration."""

    def test_pages_from_json_env(self, monkeypatch):
        """Test that pages can be set via JSON in environment."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("PAGES", '{"about": "About Me", "now": "Now"}')

        settings = Settings()

        assert settings.pages == {"about": "About Me", "now": "Now"}

    def test_pages_empty_json_object(self, monkeypatch):
        """Test that empty JSON object works."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("PAGES", "{}")

        settings = Settings()
        assert settings.pages == {}


class TestOptionalOverrides:
    """Tests for optional setting overrides."""

    def test_override_cache_ttl_feed(self, monkeypatch):
        """Test overriding feed cache TTL."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("CACHE_TTL_FEED", "600")

        settings = Settings()
        assert settings.cache_ttl_feed == 600

    def test_override_cache_ttl_post(self, monkeypatch):
        """Test overriding post cache TTL."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("CACHE_TTL_POST", "3600")

        settings = Settings()
        assert settings.cache_ttl_post == 3600

    def test_override_gemini_host(self, monkeypatch):
        """Test setting gemini_host."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("GEMINI_HOST", "gemini.example.com")

        settings = Settings()
        assert settings.gemini_host == "gemini.example.com"

    def test_override_server_settings(self, monkeypatch):
        """Test overriding server host and port."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("HOST", "0.0.0.0")
        monkeypatch.setenv("PORT", "1966")

        settings = Settings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 1966

    def test_override_cert_files(self, monkeypatch):
        """Test setting certificate files."""
        monkeypatch.setenv("BEARBLOG_URL", "https://test.bearblog.dev")
        monkeypatch.setenv("BLOG_NAME", "Test")
        monkeypatch.setenv("CERT_FILE", "/path/to/cert.pem")
        monkeypatch.setenv("KEY_FILE", "/path/to/key.pem")

        settings = Settings()
        assert settings.cert_file == "/path/to/cert.pem"
        assert settings.key_file == "/path/to/key.pem"
