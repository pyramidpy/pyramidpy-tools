from typing import Any, Dict, List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from ..toolkit import Toolkit

from .base import DiscordAPI
from .schemas import (
    AddReactionRequest,
    CreateChannelRequest,
    DeleteMessageRequest,
    EditMessageRequest,
    RemoveReactionRequest,
    SendMessageRequest,
)


def get_discord_api() -> DiscordAPI:
    """Get Discord API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        token = flow.context.get("discord_bot_token")
        if token:
            return DiscordAPI(token=token)
    return DiscordAPI()


@tool(
    name="discord_send_message",
    description="Send a message to a Discord channel",
    include_return_description=False,
)
async def discord_send_message(
    channel_id: str,
    content: str,
    tts: bool = False,
    embeds: Optional[List[Dict[str, Any]]] = None,
    allowed_mentions: Optional[Dict[str, Any]] = None,
    message_reference: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    discord = get_discord_api()
    request = SendMessageRequest(
        channel_id=channel_id,
        content=content,
        tts=tts,
        embeds=embeds,
        allowed_mentions=allowed_mentions,
        message_reference=message_reference,
    )
    return await discord.send_message(request)


@tool(
    name="discord_edit_message",
    description="Edit a Discord message",
    include_return_description=False,
)
async def discord_edit_message(
    channel_id: str,
    message_id: str,
    content: Optional[str] = None,
    embeds: Optional[List[Dict[str, Any]]] = None,
    allowed_mentions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    discord = get_discord_api()
    request = EditMessageRequest(
        channel_id=channel_id,
        message_id=message_id,
        content=content,
        embeds=embeds,
        allowed_mentions=allowed_mentions,
    )
    return await discord.edit_message(request)


@tool(
    name="discord_delete_message",
    description="Delete a Discord message",
    include_return_description=False,
)
async def discord_delete_message(
    channel_id: str,
    message_id: str,
) -> bool:
    discord = get_discord_api()
    request = DeleteMessageRequest(
        channel_id=channel_id,
        message_id=message_id,
    )
    return await discord.delete_message(request)


@tool(
    name="discord_add_reaction",
    description="Add a reaction to a Discord message",
    include_return_description=False,
)
async def discord_add_reaction(
    channel_id: str,
    message_id: str,
    emoji: str,
) -> bool:
    discord = get_discord_api()
    request = AddReactionRequest(
        channel_id=channel_id,
        message_id=message_id,
        emoji=emoji,
    )
    return await discord.add_reaction(request)


@tool(
    name="discord_remove_reaction",
    description="Remove a reaction from a Discord message",
    include_return_description=False,
)
async def discord_remove_reaction(
    channel_id: str,
    message_id: str,
    emoji: str,
    user_id: Optional[str] = None,
) -> bool:
    discord = get_discord_api()
    request = RemoveReactionRequest(
        channel_id=channel_id,
        message_id=message_id,
        emoji=emoji,
        user_id=user_id,
    )
    return await discord.remove_reaction(request)


@tool(
    name="discord_create_channel",
    description="Create a new Discord channel in a guild",
    include_return_description=False,
)
async def discord_create_channel(
    guild_id: str,
    name: str,
    topic: Optional[str] = None,
    position: Optional[int] = None,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    discord = get_discord_api()
    request = CreateChannelRequest(
        guild_id=guild_id,
        name=name,
        topic=topic,
        position=position,
        parent_id=parent_id,
    )
    return await discord.create_channel(request)


@tool(
    name="discord_get_channel",
    description="Get information about a Discord channel",
    include_return_description=False,
)
async def discord_get_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    discord = get_discord_api()
    return await discord.get_channel(channel_id)


@tool(
    name="discord_get_message",
    description="Get information about a Discord message",
    include_return_description=False,
)
async def discord_get_message(
    channel_id: str,
    message_id: str,
) -> Optional[Dict[str, Any]]:
    discord = get_discord_api()
    return await discord.get_message(channel_id, message_id)


discord_toolkit = Toolkit.create_toolkit(
    id="discord_toolkit",
    tools=[
        discord_send_message,
        discord_edit_message,
        discord_delete_message,
        discord_add_reaction,
        discord_remove_reaction,
        discord_create_channel,
        discord_get_channel,
        discord_get_message,
    ],
    is_channel=True,
    requires_config=True,
    is_app_default=True,
    auth_key="discord_bot_token",
    name="Discord Bot API Toolkit",
    description="Tools for interacting with Discord using bot API",
)
