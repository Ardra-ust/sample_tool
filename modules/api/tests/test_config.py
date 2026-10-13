"""Tests for app.config (SP-01: FR-040, FR-042, FR-044, NFR-001).

Test names cite the requirement IDs. Case IDs from docs/test-cases.md are added when
/expand-test-coverage writes the case package.
"""

from pathlib import Path

import pytest

from app.config import (
    DEFAULT_DATABASE,
    DEFAULT_STALE_MINUTES,
    DEFAULT_STATUS_ROW_ID,
    DEFAULT_STATUS_TABLE,
    ConfigError,
    Settings,
    load_settings,
    read_dotenv,
    require,
    settings_from_mapping,
)


def test_fr042_defaults_are_the_brd_values_when_nothing_is_set() -> None:
    settings = settings_from_mapping({})

    assert settings.mysql_database == DEFAULT_DATABASE == "news_app"
    assert settings.refresh_status_table == DEFAULT_STATUS_TABLE == "refresh_status"
    assert settings.refresh_status_row_id == DEFAULT_STATUS_ROW_ID == 1
    assert settings.refresh_stale_minutes == DEFAULT_STALE_MINUTES == 70


def test_fr042_values_are_read_from_the_mapping() -> None:
    settings = settings_from_mapping(
        {
            "MYSQL_HOST": "db.local",
            "MYSQL_USER": "news",
            "MYSQL_PASSWORD": "not-a-real-secret",
            "REFRESH_STALE_MINUTES": "45",
            "REFRESH_STATUS_ROW_ID": "2",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "example-deployment",
        }
    )

    assert settings.mysql_host == "db.local"
    assert settings.mysql_user == "news"
    assert settings.mysql_password == "not-a-real-secret"
    assert settings.refresh_stale_minutes == 45
    assert settings.refresh_status_row_id == 2
    assert settings.azure_openai_chat_deployment == "example-deployment"


def test_blank_values_count_as_unset() -> None:
    settings = settings_from_mapping({"REFRESH_STALE_MINUTES": "   ", "MYSQL_DATABASE": ""})

    assert settings.refresh_stale_minutes == DEFAULT_STALE_MINUTES
    assert settings.mysql_database == DEFAULT_DATABASE


def test_nfr001_secrets_are_hidden_from_repr() -> None:
    settings = settings_from_mapping(
        {
            "MYSQL_PASSWORD": "pw-value-123",
            "TAVILY_API_KEY": "tavily-value-123",
            "AZURE_OPENAI_CHAT_API_KEY": "azure-value-123",
        }
    )

    text = repr(settings)

    assert "pw-value-123" not in text
    assert "tavily-value-123" not in text
    assert "azure-value-123" not in text


@pytest.mark.parametrize("raw", ["0", "-5"])
def test_fr040_stale_minutes_must_be_positive(raw: str) -> None:
    with pytest.raises(ConfigError, match="REFRESH_STALE_MINUTES must be at least 1"):
        settings_from_mapping({"REFRESH_STALE_MINUTES": raw})


def test_fr040_row_id_must_be_at_least_one() -> None:
    with pytest.raises(ConfigError, match="REFRESH_STATUS_ROW_ID must be at least 1"):
        settings_from_mapping({"REFRESH_STATUS_ROW_ID": "0"})


def test_fr040_non_integer_error_names_the_variable_not_the_value() -> None:
    with pytest.raises(ConfigError) as info:
        settings_from_mapping({"REFRESH_STALE_MINUTES": "seventy-secret"})

    assert "REFRESH_STALE_MINUTES must be an integer" in str(info.value)
    assert "seventy-secret" not in str(info.value)


def test_fr039_webjob_is_disabled_unless_the_trigger_url_is_set() -> None:
    assert settings_from_mapping({}).webjob_enabled is False
    assert settings_from_mapping({"AZURE_WEBJOB_TRIGGER_URL": "https://example.invalid/t"}).webjob_enabled


def test_nfr001_require_lists_missing_variable_names_only() -> None:
    settings = settings_from_mapping({"MYSQL_HOST": "db.local"})

    with pytest.raises(ConfigError) as info:
        require(settings, "mysql_host", "mysql_user", "mysql_password")

    message = str(info.value)
    assert message == "Missing required settings: MYSQL_USER, MYSQL_PASSWORD"


def test_nfr001_require_passes_when_values_are_present() -> None:
    settings = settings_from_mapping({"MYSQL_HOST": "db.local"})

    require(settings, "mysql_host")  # no exception


def test_fr042_read_dotenv_returns_pairs_from_the_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MYSQL_HOST=db.local\nMYSQL_USER=news\n", encoding="utf-8")

    assert read_dotenv(env_file) == {"MYSQL_HOST": "db.local", "MYSQL_USER": "news"}


def test_fr042_read_dotenv_returns_empty_when_file_is_missing(tmp_path: Path) -> None:
    assert read_dotenv(tmp_path / "missing.env") == {}


def test_fr042_environment_overrides_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MYSQL_HOST=from-file\n", encoding="utf-8")
    monkeypatch.setenv("MYSQL_HOST", "from-environment")

    settings = load_settings(env_file)

    assert settings.mysql_host == "from-environment"


def test_fr042_dotenv_is_used_when_the_environment_is_silent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MYSQL_HOST=from-file\n", encoding="utf-8")
    monkeypatch.delenv("MYSQL_HOST", raising=False)

    settings = load_settings(env_file)

    assert settings.mysql_host == "from-file"


def test_settings_is_immutable() -> None:
    settings = Settings()

    with pytest.raises(AttributeError):
        settings.mysql_host = "changed"  # type: ignore[misc]
