from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Sequence

from openai import AsyncOpenAI

from arch_bot.config import Settings

DEFAULT_SYSTEM_PROMPT = """
You are an architecture-work assistant communicating through Discord.
Answer in the user's language. Lead with the result and keep routine answers practical.
State assumptions when requirements are ambiguous. Never claim that an external action,
file change, calculation, or verification happened unless it actually did.
For professional architecture, engineering, legal, code-compliance, cost, or safety
questions, distinguish general assistance from conclusions requiring a licensed local
professional and current project documents.
""".strip()


class ArchitectureAgent:
    """Small stateful wrapper around the OpenAI Responses API."""

    def __init__(
        self,
        settings: Settings,
        *,
        agent_id: str = "default",
        display_name: str = "건축봇",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._reasoning_effort = settings.reasoning_effort
        self._max_output_tokens = settings.max_output_tokens
        self._agent_id = agent_id
        self._display_name = display_name
        self._system_prompt = system_prompt
        self._previous_response_ids: dict[str, str] = {}
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def ask(
        self,
        conversation_id: str,
        prompt: str,
        *,
        content_items: Sequence[dict[str, object]] = (),
    ) -> str:
        async with self._locks[conversation_id]:
            request_input: object = prompt
            if content_items:
                request_input = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            *content_items,
                        ],
                    }
                ]
            request: dict[str, object] = {
                "model": self._model,
                "instructions": self._system_prompt,
                "input": request_input,
                "reasoning": {"effort": self._reasoning_effort},
                "max_output_tokens": self._max_output_tokens,
            }
            previous_id = self._previous_response_ids.get(conversation_id)
            if previous_id:
                request["previous_response_id"] = previous_id

            response = await self._client.responses.create(**request)
            self._previous_response_ids[conversation_id] = response.id
            answer = response.output_text.strip()
            return answer or "응답 내용이 비어 있습니다. 질문을 조금 다르게 표현해 주세요."

    def reset(self, conversation_id: str) -> bool:
        return self._previous_response_ids.pop(conversation_id, None) is not None

    @property
    def model(self) -> str:
        return self._model

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def display_name(self) -> str:
        return self._display_name
