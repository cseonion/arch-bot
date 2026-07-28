from __future__ import annotations

import logging

import discord
from discord import app_commands

from arch_bot.agent import ArchitectureAgent
from arch_bot.config import Settings
from arch_bot.text import split_message

logger = logging.getLogger(__name__)


def conversation_id(interaction: discord.Interaction) -> str:
    location = interaction.channel_id or interaction.user.id
    return f"{interaction.guild_id or 'dm'}:{location}"


class ArchBot(discord.Client):
    def __init__(self, settings: Settings) -> None:
        super().__init__(intents=discord.Intents.none())
        self.settings = settings
        self.agent = ArchitectureAgent(settings)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if self.settings.discord_guild_id:
            guild = discord.Object(id=self.settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info("Synced %d commands to development guild %s", len(synced), guild.id)
        else:
            synced = await self.tree.sync()
            logger.info("Synced %d global commands", len(synced))

    async def on_ready(self) -> None:
        logger.info("Connected as %s (%s)", self.user, self.user.id if self.user else "unknown")


def create_bot(settings: Settings) -> ArchBot:
    bot = ArchBot(settings)

    @bot.tree.command(name="ask", description="건축 업무 비서에게 질문합니다")
    @app_commands.describe(question="질문 또는 요청")
    async def ask(interaction: discord.Interaction, question: str) -> None:
        await interaction.response.defer(thinking=True)
        try:
            answer = await bot.agent.ask(conversation_id(interaction), question)
            chunks = split_message(answer)
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        except Exception:
            logger.exception("Agent request failed")
            await interaction.followup.send(
                "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
                ephemeral=True,
            )

    @bot.tree.command(name="reset", description="현재 채널의 대화 맥락을 초기화합니다")
    async def reset(interaction: discord.Interaction) -> None:
        had_context = bot.agent.reset(conversation_id(interaction))
        message = "대화 맥락을 초기화했습니다." if had_context else "초기화할 대화 맥락이 없습니다."
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(name="status", description="봇의 연결 상태와 모델을 확인합니다")
    async def status(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"정상 작동 중입니다. 모델: `{bot.agent.model}`",
            ephemeral=True,
        )

    return bot
