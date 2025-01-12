from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: int
    from_user: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    caption: Optional[str] = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    channel_post: Optional[TelegramMessage] = None
    edited_channel_post: Optional[TelegramMessage] = None


class SendMessageRequest(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: Optional[str] = None
    disable_web_page_preview: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[int] = None


class SendPhotoRequest(BaseModel):
    chat_id: Union[int, str]
    photo: str  # File ID or URL
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[int] = None


class SendDocumentRequest(BaseModel):
    chat_id: Union[int, str]
    document: str  # File ID or URL
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[int] = None


class WebhookInfo(BaseModel):
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: Optional[str] = None
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    allowed_updates: Optional[List[str]] = None
