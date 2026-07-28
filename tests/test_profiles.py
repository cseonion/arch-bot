from __future__ import annotations

from pathlib import Path

import pytest

from arch_bot.config import ConfigError
from arch_bot.profiles import AgentRegistry


def write_profile(
    root: Path,
    name: str,
    *,
    is_default: bool = False,
    channel_env: str | None = None,
    skills: str = "",
) -> None:
    profile_dir = root / "agents" / name
    profile_dir.mkdir(parents=True)
    channel_line = f'channel_id_env = "{channel_env}"\n' if channel_env else ""
    (profile_dir / "profile.toml").write_text(
        f'id = "{name}"\n'
        f'display_name = "{name}"\n'
        f"default = {str(is_default).lower()}\n"
        f"{channel_line}"
        'system_prompt_file = "system.md"\n'
        "[capabilities]\n"
        f"skills = [{skills}]\n"
        "tools = []\n"
        "mcp_servers = []\n",
        encoding="utf-8",
    )
    (profile_dir / "system.md").write_text(f"{name} prompt", encoding="utf-8")


def test_registry_routes_channels_and_combines_skills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_profile(tmp_path, "default", is_default=True)
    write_profile(
        tmp_path,
        "task1",
        channel_env="TASK1_CHANNEL",
        skills='"shared"',
    )
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "shared.md").write_text("shared instructions", encoding="utf-8")
    monkeypatch.setenv("TASK1_CHANNEL", "123")

    registry = AgentRegistry.load(tmp_path / "agents")
    profile = registry.for_channel(123)

    assert registry.default.agent_id == "default"
    assert profile is not None
    assert profile.agent_id == "task1"
    assert "shared instructions" in profile.system_prompt
    assert registry.for_channel(999) is None


def test_registry_allows_unconfigured_optional_channel(tmp_path: Path) -> None:
    write_profile(tmp_path, "default", is_default=True)
    write_profile(tmp_path, "task1", channel_env="MISSING_CHANNEL")

    registry = AgentRegistry.load(tmp_path / "agents")

    assert registry.configured_channel_count == 0


def test_registry_rejects_duplicate_channels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_profile(tmp_path, "default", is_default=True)
    write_profile(tmp_path, "task1", channel_env="TASK1_CHANNEL")
    write_profile(tmp_path, "task2", channel_env="TASK2_CHANNEL")
    monkeypatch.setenv("TASK1_CHANNEL", "123")
    monkeypatch.setenv("TASK2_CHANNEL", "123")

    with pytest.raises(ConfigError, match="Duplicate"):
        AgentRegistry.load(tmp_path / "agents")
