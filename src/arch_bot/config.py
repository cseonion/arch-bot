from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when required runtime configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    discord_token: str
    openai_api_key: str
    discord_guild_id: int | None
    openai_model: str
    reasoning_effort: str
    max_output_tokens: int

    @classmethod
    def from_env(cls) -> Settings:
        discord_token = os.getenv("DISCORD_TOKEN", "").strip()
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not discord_token:
            raise ConfigError("DISCORD_TOKEN is required")
        if not openai_api_key:
            raise ConfigError("OPENAI_API_KEY is required")

        guild_id_text = os.getenv("DISCORD_GUILD_ID", "").strip()
        try:
            guild_id = int(guild_id_text) if guild_id_text else None
        except ValueError as exc:
            raise ConfigError("DISCORD_GUILD_ID must be an integer") from exc

        effort = os.getenv("OPENAI_REASONING_EFFORT", "medium").strip().lower()
        allowed_efforts = {"none", "low", "medium", "high", "xhigh", "max"}
        if effort not in allowed_efforts:
            raise ConfigError(
                f"OPENAI_REASONING_EFFORT must be one of: {', '.join(sorted(allowed_efforts))}"
            )

        try:
            max_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "4000"))
        except ValueError as exc:
            raise ConfigError("OPENAI_MAX_OUTPUT_TOKENS must be an integer") from exc
        if not 1 <= max_tokens <= 128_000:
            raise ConfigError("OPENAI_MAX_OUTPUT_TOKENS must be between 1 and 128000")

        return cls(
            discord_token=discord_token,
            openai_api_key=openai_api_key,
            discord_guild_id=guild_id,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6-terra").strip(),
            reasoning_effort=effort,
            max_output_tokens=max_tokens,
        )
