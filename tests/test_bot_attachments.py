from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from arch_bot.bot import ArchBot
from arch_bot.config import Settings


@dataclass
class FakeAttachment:
    filename: str
    data: bytes
    content_type: str | None = None

    @property
    def size(self) -> int:
        return len(self.data)

    async def read(self, *, use_cached: bool = False) -> bytes:
        return self.data


class FakeTyping:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *args: object) -> None:
        return None


class FakeChannel:
    id = 123

    def __init__(self) -> None:
        self.sent: list[str] = []

    def typing(self) -> FakeTyping:
        return FakeTyping()

    async def send(self, text: str, **kwargs: object) -> None:
        self.sent.append(text)


class FakeAgent:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, tuple[dict[str, object], ...]]] = []

    async def ask(
        self,
        conversation_id: str,
        prompt: str,
        *,
        content_items: tuple[dict[str, object], ...] = (),
    ) -> str:
        self.calls.append((conversation_id, prompt, content_items))
        return "분석 결과"


class FailingAgent(FakeAgent):
    async def ask(
        self,
        conversation_id: str,
        prompt: str,
        *,
        content_items: tuple[dict[str, object], ...] = (),
    ) -> str:
        raise AssertionError("rejected attachments must not call the model")


def settings() -> Settings:
    return Settings(
        discord_token="discord",
        openai_api_key="openai",
        discord_guild_id=None,
        openai_model="gpt-5.6-terra",
        reasoning_effort="medium",
        max_output_tokens=4000,
        agent_config_dir=Path("config/agents"),
    )


def fake_message(channel: FakeChannel, attachment: FakeAttachment, content: str = "") -> object:
    author = type("Author", (), {"bot": False, "display_name": "사용자"})()
    guild = type("Guild", (), {"id": 456})()
    return type(
        "Message",
        (),
        {
            "author": author,
            "content": content,
            "attachments": [attachment],
            "channel": channel,
            "guild": guild,
        },
    )()


def test_file_only_task1_message_is_analyzed(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_TASK1_CHANNEL_ID", "123")
    bot = ArchBot(settings())
    agent = FakeAgent()
    bot.agents["task1"] = agent  # type: ignore[assignment]
    channel = FakeChannel()

    asyncio.run(
        bot.on_message(
            fake_message(
                channel,
                FakeAttachment("drawing.pdf", b"%PDF-1.7\nexample", "application/pdf"),
            )
        )
    )

    assert len(agent.calls) == 1
    assert agent.calls[0][2][0]["type"] == "input_file"
    assert channel.sent == ["분석 결과"]


def test_rejected_attachment_short_circuits_model(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_TASK1_CHANNEL_ID", "123")
    bot = ArchBot(settings())
    bot.agents["task1"] = FailingAgent()  # type: ignore[assignment]
    channel = FakeChannel()

    asyncio.run(
        bot.on_message(
            fake_message(
                channel,
                FakeAttachment("broken.pdf", b"not-pdf", "application/pdf"),
                "이 파일을 분석해줘",
            )
        )
    )

    assert len(channel.sent) == 1
    assert "서명" in channel.sent[0]
