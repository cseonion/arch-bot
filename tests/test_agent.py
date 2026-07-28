from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

from arch_bot.agent import ArchitectureAgent
from arch_bot.config import Settings


class FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def create(self, **request: object) -> SimpleNamespace:
        self.calls.append(request)
        return SimpleNamespace(
            id=f"response-{len(self.calls)}",
            output_text="answer",
        )


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


def test_agent_builds_multimodal_response_input_and_continues_context() -> None:
    agent = ArchitectureAgent(settings())
    responses = FakeResponses()
    agent._client = SimpleNamespace(responses=responses)  # type: ignore[assignment]
    file_item = {
        "type": "input_file",
        "filename": "drawing.pdf",
        "file_data": "data:application/pdf;base64,example",
        "detail": "high",
    }

    first = asyncio.run(agent.ask("channel", "analyze", content_items=[file_item]))
    second = asyncio.run(agent.ask("channel", "continue"))

    assert first == "answer"
    first_input = responses.calls[0]["input"]
    assert isinstance(first_input, list)
    assert first_input[0]["content"][0] == {"type": "input_text", "text": "analyze"}
    assert first_input[0]["content"][1] == file_item
    assert "previous_response_id" not in responses.calls[0]
    assert second == "answer"
    assert responses.calls[1]["previous_response_id"] == "response-1"
