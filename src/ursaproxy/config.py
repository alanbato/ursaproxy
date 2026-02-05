from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration from environment variables."""

    # Required: the Bearblog URL to proxy
    bearblog_url: str
    blog_name: str

    cache_ttl_feed: int = 300  # 5 minutes
    cache_ttl_post: int = 1800  # 30 minutes

    # Static pages (slug -> title) - pages not in RSS feed
    # Override via PAGES='{"about": "About Me", "now": "Now"}'
    pages: dict[str, str] = {}

    # Gemini capsule hostname (for feed URLs)
    # e.g., "gemini.example.com" -> gemini://gemini.example.com/post/...
    gemini_host: str | None = None

    # Server settings
    host: str = "localhost"
    port: int = 1965
    cert_file: str | None = None
    key_file: str | None = None

    @field_validator("bearblog_url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """Remove trailing slash to prevent double slashes in URLs."""
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("bearblog_url must start with http:// or https://")
        return v


settings = Settings()  # type: ignore[call-arg]  # pydantic-settings reads from env
