from __future__ import annotations

import pytest

from arch_bot.config import ConfigError, Settings


def test_settings_load_required_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "discord")
    monkeypatch.setenv("OPENAI_API_KEY", "openai")
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)

    settings = Settings.from_env()

    assert settings.discord_guild_id is None
    assert settings.openai_model == "gpt-5.6-terra"
    assert settings.reasoning_effort == "medium"
    assert settings.agent_config_dir.as_posix() == "config/agents"


def test_settings_require_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="DISCORD_TOKEN"):
        Settings.from_env()


def test_settings_reject_invalid_guild_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "discord")
    monkeypatch.setenv("OPENAI_API_KEY", "openai")
    monkeypatch.setenv("DISCORD_GUILD_ID", "not-a-number")

    with pytest.raises(ConfigError, match="integer"):
        Settings.from_env()
