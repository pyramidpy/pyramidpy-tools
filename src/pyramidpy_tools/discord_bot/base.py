from typing import Any, Dict, Optional

import discord
from discord import Intents
from discord.ext import commands

from pyramidpy_tools.settings import settings

from .schemas import (
    AddReactionRequest,
    CreateChannelRequest,
    DeleteMessageRequest,
    EditMessageRequest,
    RemoveReactionRequest,
    SendMessageRequest,
)


class DiscordAPI:
    """Client for interacting with Discord API"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.tool_provider.discord_bot_token
        if not self.token:
            raise ValueError("Discord bot token not found")

        # Setup intents
        intents = Intents.default()
        intents.message_content = True
        intents.members = True

        # Initialize bot with command prefix and intents
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self._setup_events()

    def _setup_events(self):
        """Setup bot event handlers"""

        @self.bot.event
        async def on_ready():
            print(f"Bot is ready. Logged in as {self.bot.user.name}")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            await self.bot.process_commands(message)

    async def start_bot(self):
        """Start the Discord bot"""
        await self.bot.start(self.token)

    async def close_bot(self):
        """Close the Discord bot connection"""
        await self.bot.close()

    async def send_message(self, request: SendMessageRequest) -> Dict[str, Any]:
        """Send a message to a channel"""
        channel = await self.bot.fetch_channel(request.channel_id)
        message = await channel.send(
            content=request.content,
            tts=request.tts,
            embeds=request.embeds,
            allowed_mentions=discord.AllowedMentions(**request.allowed_mentions)
            if request.allowed_mentions
            else None,
            reference=discord.MessageReference(**request.message_reference)
            if request.message_reference
            else None,
        )
        return message.to_dict()

    async def edit_message(self, request: EditMessageRequest) -> Dict[str, Any]:
        """Edit a message"""
        channel = await self.bot.fetch_channel(request.channel_id)
        message = await channel.fetch_message(request.message_id)
        edited_message = await message.edit(
            content=request.content,
            embeds=request.embeds,
            allowed_mentions=discord.AllowedMentions(**request.allowed_mentions)
            if request.allowed_mentions
            else None,
        )
        return edited_message.to_dict()

    async def delete_message(self, request: DeleteMessageRequest) -> bool:
        """Delete a message"""
        channel = await self.bot.fetch_channel(request.channel_id)
        message = await channel.fetch_message(request.message_id)
        await message.delete()
        return True

    async def add_reaction(self, request: AddReactionRequest) -> bool:
        """Add a reaction to a message"""
        channel = await self.bot.fetch_channel(request.channel_id)
        message = await channel.fetch_message(request.message_id)
        await message.add_reaction(request.emoji)
        return True

    async def remove_reaction(self, request: RemoveReactionRequest) -> bool:
        """Remove a reaction from a message"""
        channel = await self.bot.fetch_channel(request.channel_id)
        message = await channel.fetch_message(request.message_id)
        if request.user_id:
            user = await self.bot.fetch_user(request.user_id)
            await message.remove_reaction(request.emoji, user)
        else:
            await message.remove_reaction(request.emoji, self.bot.user)
        return True

    async def create_channel(self, request: CreateChannelRequest) -> Dict[str, Any]:
        """Create a new channel in a guild"""
        guild = await self.bot.fetch_guild(request.guild_id)
        channel = await guild.create_text_channel(
            name=request.name,
            topic=request.topic,
            position=request.position,
            category=await self.bot.fetch_channel(request.parent_id)
            if request.parent_id
            else None,
        )
        return channel.to_dict()

    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel information"""
        try:
            channel = await self.bot.fetch_channel(channel_id)
            return channel.to_dict()
        except discord.NotFound:
            return None

    async def get_message(
        self, channel_id: str, message_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get message information"""
        try:
            channel = await self.bot.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            return message.to_dict()
        except discord.NotFound:
            return None
