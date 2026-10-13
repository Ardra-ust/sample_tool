"""Configuration for the AI News Agent (FR-040, FR-042, NFR-001).

Settings come from the repo-root .env (through python-dotenv) and from the process
environment. Real environment variables win over .env values. Nothing is hardcoded:
defaults are only the values the BRD fixes (news_app, refresh_status, row 1, 70 minutes).

Secret values are excluded from repr() and from error messages. Errors name the
missing variables, never their values.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

# This file is modules/api/app/config.py, so parents[3] is the repo root.
REPO_ROOT: Path = Path(__file__).resolve().parents[3]
DOTENV_PATH: Path = REPO_ROOT / ".env"

DEFAULT_DATABASE: str = "news_app"
DEFAULT_STATUS_TABLE: str = "refresh_status"
DEFAULT_STATUS_ROW_ID: int = 1
DEFAULT_STALE_MINUTES: int = 70  # owner decision, DQ-018 (notes say 20)


class ConfigError(ValueError):
    """Raised for missing or invalid configuration. Messages never include secret values."""


@dataclass(frozen=True)
class Settings:
    """Typed application settings. Secret fields are hidden from repr()."""

    mysql_host: str = ""
    mysql_user: str = ""
    mysql_password: str = field(default="", repr=False)
    mysql_database: str = DEFAULT_DATABASE

    refresh_status_table: str = DEFAULT_STATUS_TABLE
    refresh_status_row_id: int = DEFAULT_STATUS_ROW_ID
    refresh_stale_minutes: int = DEFAULT_STALE_MINUTES

    searchapi_io_key: str = field(default="", repr=False)
    tavily_api_key: str = field(default="", repr=False)

    azure_openai_chat_endpoint: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_chat_api_key: str = field(default="", repr=False)
    azure_openai_embed_endpoint: str = ""
    azure_openai_embed_deployment: str = ""
    azure_openai_embed_api_key: str = field(default="", repr=False)
    azure_openai_embed_api_version: str = ""

    # Optional WebJob trigger (FR-039): used only when the URL is set.
    azure_webjob_trigger_url: str = ""
    azure_webjob_user: str = ""
    azure_webjob_pass: str = field(default="", repr=False)

    @property
    def webjob_enabled(self) -> bool:
        """True only when AZURE_WEBJOB_TRIGGER_URL is set (FR-039)."""
        return bool(self.azure_webjob_trigger_url)


def read_dotenv(path: Path = DOTENV_PATH) -> dict[str, str]:
    """Return the .env key/value pairs without changing the process environment."""
    if not path.is_file():
        return {}
    return {key: value for key, value in dotenv_values(path).items() if value is not None}


def _pick(env: Mapping[str, str], name: str, default: str = "") -> str:
    """Read one variable; blank values count as unset."""
    value = env.get(name, "")
    value = value.strip() if value else ""
    return value or default


def _as_int(env: Mapping[str, str], name: str, default: int, minimum: int) -> int:
    """Read an integer variable with a lower bound. Errors name the variable only."""
    raw = _pick(env, name)
    if not raw:
        return default
    try:
        number = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if number < minimum:
        raise ConfigError(f"{name} must be at least {minimum}")
    return number


def settings_from_mapping(env: Mapping[str, str]) -> Settings:
    """Build Settings from a mapping. Pure function: used by tests and by load_settings()."""
    return Settings(
        mysql_host=_pick(env, "MYSQL_HOST"),
        mysql_user=_pick(env, "MYSQL_USER"),
        mysql_password=_pick(env, "MYSQL_PASSWORD"),
        mysql_database=_pick(env, "MYSQL_DATABASE", DEFAULT_DATABASE),
        refresh_status_table=_pick(env, "REFRESH_STATUS_TABLE", DEFAULT_STATUS_TABLE),
        refresh_status_row_id=_as_int(env, "REFRESH_STATUS_ROW_ID", DEFAULT_STATUS_ROW_ID, 1),
        refresh_stale_minutes=_as_int(env, "REFRESH_STALE_MINUTES", DEFAULT_STALE_MINUTES, 1),
        searchapi_io_key=_pick(env, "SEARCHAPI_IO_KEY"),
        tavily_api_key=_pick(env, "TAVILY_API_KEY"),
        azure_openai_chat_endpoint=_pick(env, "AZURE_OPENAI_CHAT_ENDPOINT"),
        azure_openai_chat_deployment=_pick(env, "AZURE_OPENAI_CHAT_DEPLOYMENT"),
        azure_openai_chat_api_key=_pick(env, "AZURE_OPENAI_CHAT_API_KEY"),
        azure_openai_embed_endpoint=_pick(env, "AZURE_OPENAI_EMBED_ENDPOINT"),
        azure_openai_embed_deployment=_pick(env, "AZURE_OPENAI_EMBED_DEPLOYMENT"),
        azure_openai_embed_api_key=_pick(env, "AZURE_OPENAI_EMBED_API_KEY"),
        azure_openai_embed_api_version=_pick(env, "AZURE_OPENAI_EMBED_API_VERSION"),
        azure_webjob_trigger_url=_pick(env, "AZURE_WEBJOB_TRIGGER_URL"),
        azure_webjob_user=_pick(env, "AZURE_WEBJOB_USER"),
        azure_webjob_pass=_pick(env, "AZURE_WEBJOB_PASS"),
    )


def load_settings(dotenv_path: Path = DOTENV_PATH) -> Settings:
    """Load settings from .env, then let real environment variables override them."""
    merged: dict[str, str] = {**read_dotenv(dotenv_path), **os.environ}
    return settings_from_mapping(merged)


def require(settings: Settings, *names: str) -> None:
    """Fail fast when a feature's required settings are blank.

    Takes attribute names (for example "mysql_host"). The error lists the environment
    variable names that are missing, never their values.
    """
    missing = [name for name in names if not getattr(settings, name)]
    if missing:
        env_names = ", ".join(name.upper() for name in missing)
        raise ConfigError(f"Missing required settings: {env_names}")
