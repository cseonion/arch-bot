from __future__ import annotations

import logging

import discord
from discord import app_commands

from arch_bot.agent import ArchitectureAgent
from arch_bot.config import Settings
from arch_bot.profiles import AgentProfile, AgentRegistry
from arch_bot.text import split_message

logger = logging.getLogger(__name__)


def conversation_id(interaction: discord.Interaction) -> str:
    location = interaction.channel_id or interaction.user.id
    return f"{interaction.guild_id or 'dm'}:{location}"


class ArchBot(discord.Client):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.settings = settings
        self.registry = AgentRegistry.load(settings.agent_config_dir)
        self.agents = {
            profile.agent_id: ArchitectureAgent(
                settings,
                agent_id=profile.agent_id,
                display_name=profile.display_name,
                system_prompt=profile.system_prompt,
            )
            for profile in self.registry.profiles
        }
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
        logger.info(
            "Connected as %s (%s); %d autonomous channels configured",
            self.user,
            self.user.id if self.user else "unknown",
            self.registry.configured_channel_count,
        )

    def profile_for_channel(self, channel_id: int | None) -> AgentProfile | None:
        return self.registry.for_channel(channel_id)

    def agent_for_profile(self, profile: AgentProfile) -> ArchitectureAgent:
        return self.agents[profile.agent_id]

    def agent_for_interaction(
        self, interaction: discord.Interaction
    ) -> tuple[ArchitectureAgent, AgentProfile]:
        profile = self.profile_for_channel(interaction.channel_id) or self.registry.default
        return self.agent_for_profile(profile), profile

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.content.strip():
            return
        profile = self.profile_for_channel(message.channel.id)
        if profile is None:
            return

        agent = self.agent_for_profile(profile)
        prompt = f"{message.author.display_name}: {message.content}"
        try:
            async with message.channel.typing():
                answer = await agent.ask(
                    f"{message.guild.id if message.guild else 'dm'}:{message.channel.id}",
                    prompt,
                )
            for chunk in split_message(answer):
                await message.channel.send(
                    chunk,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
        except Exception:
            logger.exception("Autonomous channel request failed for agent %s", profile.agent_id)
            await message.channel.send(
                "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
            )


def create_bot(settings: Settings) -> ArchBot:
    bot = ArchBot(settings)

    @bot.tree.command(name="ask", description="건축 업무 비서에게 질문합니다")
    @app_commands.describe(question="질문 또는 요청")
    async def ask(interaction: discord.Interaction, question: str) -> None:
        await interaction.response.defer(thinking=True)
        try:
            agent, _ = bot.agent_for_interaction(interaction)
            answer = await agent.ask(conversation_id(interaction), question)
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
        agent, _ = bot.agent_for_interaction(interaction)
        had_context = agent.reset(conversation_id(interaction))
        message = "대화 맥락을 초기화했습니다." if had_context else "초기화할 대화 맥락이 없습니다."
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(name="status", description="봇의 연결 상태와 모델을 확인합니다")
    async def status(interaction: discord.Interaction) -> None:
        agent, profile = bot.agent_for_interaction(interaction)
        capabilities = (
            f"skills={list(profile.skills)}, tools={list(profile.tools)}, "
            f"mcp={list(profile.mcp_servers)}"
        )
        await interaction.response.send_message(
            f"정상 작동 중입니다.\n"
            f"에이전트: `{agent.display_name}` (`{agent.agent_id}`)\n"
            f"모델: `{agent.model}`\n"
            f"선언된 기능: `{capabilities}`",
            ephemeral=True,
        )

    return bot
