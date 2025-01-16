from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DiscordUser(BaseModel):
    """Discord user model"""

    id: str
    username: str
    discriminator: str
    bot: Optional[bool] = None
    system: Optional[bool] = None
    avatar: Optional[str] = None


class DiscordChannel(BaseModel):
    """Discord channel model"""

    id: str
    type: int
    name: str
    guild_id: Optional[str] = None
    position: Optional[int] = None
    topic: Optional[str] = None


class DiscordMessage(BaseModel):
    """Discord message model"""

    id: str
    channel_id: str
    author: DiscordUser
    content: str
    timestamp: str
    edited_timestamp: Optional[str] = None
    tts: bool
    mention_everyone: bool
    mentions: List[DiscordUser] = []
    attachments: List[Dict[str, Any]] = []
    embeds: List[Dict[str, Any]] = []


class SendMessageRequest(BaseModel):
    """Request model for sending messages"""

    channel_id: str
    content: str
    tts: Optional[bool] = False
    embeds: Optional[List[Dict[str, Any]]] = None
    allowed_mentions: Optional[Dict[str, Any]] = None
    message_reference: Optional[Dict[str, Any]] = None


class EditMessageRequest(BaseModel):
    """Request model for editing messages"""

    channel_id: str
    message_id: str
    content: Optional[str] = None
    embeds: Optional[List[Dict[str, Any]]] = None
    allowed_mentions: Optional[Dict[str, Any]] = None


class DeleteMessageRequest(BaseModel):
    """Request model for deleting messages"""

    channel_id: str
    message_id: str


class AddReactionRequest(BaseModel):
    """Request model for adding reactions"""

    channel_id: str
    message_id: str
    emoji: str


class RemoveReactionRequest(BaseModel):
    """Request model for removing reactions"""

    channel_id: str
    message_id: str
    emoji: str
    user_id: Optional[str] = None  # If not provided, removes bot's reaction


class CreateChannelRequest(BaseModel):
    """Request model for creating channels"""

    guild_id: str
    name: str
    type: int = 0  # 0 for text channel
    topic: Optional[str] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None  # Category ID


class WebhookPayload(BaseModel):
    """Discord webhook payload model"""

    type: int
    token: str
    guild_id: Optional[str] = None
    channel_id: str
    author: DiscordUser
    content: str
    timestamp: str
    interaction: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
