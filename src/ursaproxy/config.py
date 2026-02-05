from pydantic import field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class Settings(BaseSettings):
    """Configuration from ursaproxy.toml file and/or environment variables.

    Settings are loaded in this priority order (highest to lowest):
    1. Constructor arguments (e.g., Settings(bearblog_url="..."))
    2. Environment variables (e.g., BEARBLOG_URL)
    3. ursaproxy.toml file in current directory
    4. Default values

    Example ursaproxy.toml:
        bearblog_url = "https://example.bearblog.dev"
        blog_name = "My Blog"
        pages = { about = "About Me", now = "Now" }
    """

    model_config = SettingsConfigDict(
        toml_file="ursaproxy.toml",
    )

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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configure settings sources with TOML file support.

        Priority (highest to lowest): init args -> env vars -> TOML file -> defaults.
        """
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    @field_validator("bearblog_url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """Remove trailing slash to prevent double slashes in URLs."""
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("bearblog_url must start with http:// or https://")
        return v


def load_settings() -> Settings:
    """Load settings from TOML file and/or environment variables.

    Use this when running ursaproxy standalone. For embedding in other apps,
    create a Settings instance directly with the desired configuration.
    """
    try:
        return Settings()  # type: ignore[call-arg]
    except FileNotFoundError:
        # No TOML file - disable TOML source and rely on env vars only
        class _EnvOnlySettings(Settings):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                return (init_settings, env_settings)

        return _EnvOnlySettings()  # type: ignore[call-arg]
