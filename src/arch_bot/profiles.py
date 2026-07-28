from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from arch_bot.config import ConfigError


@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    display_name: str
    system_prompt: str
    channel_id: int | None
    channel_id_env: str | None
    is_default: bool
    skills: tuple[str, ...]
    tools: tuple[str, ...]
    mcp_servers: tuple[str, ...]


class AgentRegistry:
    def __init__(self, profiles: tuple[AgentProfile, ...]) -> None:
        defaults = [profile for profile in profiles if profile.is_default]
        if len(defaults) != 1:
            raise ConfigError("Exactly one agent profile must set default = true")

        channel_profiles: dict[int, AgentProfile] = {}
        for profile in profiles:
            if profile.channel_id is None:
                continue
            if profile.channel_id in channel_profiles:
                raise ConfigError(f"Duplicate agent channel ID: {profile.channel_id}")
            channel_profiles[profile.channel_id] = profile

        self._profiles = profiles
        self._default = defaults[0]
        self._channel_profiles = channel_profiles

    @classmethod
    def load(cls, config_dir: Path) -> AgentRegistry:
        if not config_dir.is_dir():
            raise ConfigError(f"Agent config directory not found: {config_dir}")

        manifests = sorted(config_dir.glob("*/profile.toml"))
        if not manifests:
            raise ConfigError(f"No agent profiles found in: {config_dir}")
        return cls(tuple(_load_profile(path, config_dir) for path in manifests))

    @property
    def default(self) -> AgentProfile:
        return self._default

    @property
    def profiles(self) -> tuple[AgentProfile, ...]:
        return self._profiles

    @property
    def configured_channel_count(self) -> int:
        return len(self._channel_profiles)

    def for_channel(self, channel_id: int | None) -> AgentProfile | None:
        if channel_id is None:
            return None
        return self._channel_profiles.get(channel_id)


def _load_profile(manifest_path: Path, config_dir: Path) -> AgentProfile:
    with manifest_path.open("rb") as file:
        data = tomllib.load(file)

    agent_id = _required_string(data, "id", manifest_path)
    display_name = _required_string(data, "display_name", manifest_path)
    prompt_file = _required_string(data, "system_prompt_file", manifest_path)
    system_prompt_path = _safe_path(manifest_path.parent, prompt_file)
    if not system_prompt_path.is_file():
        raise ConfigError(f"System prompt not found: {system_prompt_path}")
    prompt_parts = [system_prompt_path.read_text(encoding="utf-8").strip()]

    capabilities = data.get("capabilities", {})
    skills = _string_tuple(capabilities, "skills", manifest_path)
    tools = _string_tuple(capabilities, "tools", manifest_path)
    mcp_servers = _string_tuple(capabilities, "mcp_servers", manifest_path)

    skills_dir = config_dir.parent / "skills"
    for skill in skills:
        skill_path = _safe_path(skills_dir, f"{skill}.md")
        if not skill_path.is_file():
            raise ConfigError(f"Skill prompt not found: {skill_path}")
        skill_text = skill_path.read_text(encoding="utf-8").strip()
        prompt_parts.append(f'<skill name="{skill}">\n{skill_text}\n</skill>')

    channel_id_env = data.get("channel_id_env")
    channel_id: int | None = None
    if channel_id_env:
        if not isinstance(channel_id_env, str):
            raise ConfigError(f"channel_id_env must be a string: {manifest_path}")
        channel_text = os.getenv(channel_id_env, "").strip()
        if channel_text:
            try:
                channel_id = int(channel_text)
            except ValueError as exc:
                raise ConfigError(f"{channel_id_env} must be an integer") from exc

    return AgentProfile(
        agent_id=agent_id,
        display_name=display_name,
        system_prompt="\n\n".join(prompt_parts),
        channel_id=channel_id,
        channel_id_env=channel_id_env,
        is_default=bool(data.get("default", False)),
        skills=skills,
        tools=tools,
        mcp_servers=mcp_servers,
    )


def _safe_path(base: Path, relative: str) -> Path:
    base = base.resolve()
    candidate = (base / relative).resolve()
    if not candidate.is_relative_to(base):
        raise ConfigError(f"Path escapes its config directory: {relative}")
    return candidate


def _required_string(data: dict[str, object], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string: {path}")
    return value.strip()


def _string_tuple(data: object, key: str, path: Path) -> tuple[str, ...]:
    if not isinstance(data, dict):
        raise ConfigError(f"capabilities must be a table: {path}")
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"capabilities.{key} must be a string list: {path}")
    return tuple(value)
