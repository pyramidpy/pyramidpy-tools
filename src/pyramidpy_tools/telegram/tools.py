from typing import Any, Dict, List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit
from pyramidpy_tools.settings import settings

from .base import TelegramAPI
from .schemas import SendDocumentRequest, SendMessageRequest, SendPhotoRequest


def get_telegram_api() -> TelegramAPI:
    """Get Telegram API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        token = flow.context.get("telegram_bot_token")
        if token:
            return TelegramAPI(token=token)
    return TelegramAPI()


@tool(
    name="telegram_send_message",
    description="Send a text message to a Telegram chat",
    include_return_description=False,
)
async def telegram_send_message(
    chat_id: str,
    text: str,
    parse_mode: Optional[str] = None,
    disable_web_page_preview: Optional[bool] = None,
    disable_notification: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
) -> Dict[str, Any]:
    telegram = get_telegram_api()
    request = SendMessageRequest(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
    )
    return await telegram.send_message(request)


@tool(
    name="telegram_send_photo",
    description="Send a photo to a Telegram chat",
    include_return_description=False,
)
async def telegram_send_photo(
    chat_id: str,
    photo: str,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = None,
    disable_notification: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
) -> Dict[str, Any]:
    telegram = get_telegram_api()
    request = SendPhotoRequest(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode=parse_mode,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
    )
    return await telegram.send_photo(request)


@tool(
    name="telegram_send_document",
    description="Send a document to a Telegram chat",
    include_return_description=False,
)
async def telegram_send_document(
    chat_id: str,
    document: str,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = None,
    disable_notification: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
) -> Dict[str, Any]:
    telegram = get_telegram_api()
    request = SendDocumentRequest(
        chat_id=chat_id,
        document=document,
        caption=caption,
        parse_mode=parse_mode,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
    )
    return await telegram.send_document(request)


@tool(
    name="telegram_get_webhook_info",
    description="Get current webhook status",
    include_return_description=False,
)
async def telegram_get_webhook_info():
    telegram = get_telegram_api()
    return await telegram.get_webhook_info()


@tool(
    name="telegram_set_webhook",
    description="Set webhook for the bot",
    include_return_description=False,
)
async def telegram_set_webhook(
    url: str,
    certificate: Optional[str] = None,
    ip_address: Optional[str] = None,
    max_connections: Optional[int] = None,
    allowed_updates: Optional[List[str]] = None,
    drop_pending_updates: bool = False,
    secret_token: Optional[str] = None,
) -> bool:
    telegram = get_telegram_api()
    return await telegram.set_webhook(
        url=url,
        certificate=certificate,
        ip_address=ip_address,
        max_connections=max_connections,
        allowed_updates=allowed_updates,
        drop_pending_updates=drop_pending_updates,
        secret_token=secret_token,
    )


@tool(
    name="telegram_delete_webhook",
    description="Remove webhook integration",
    include_return_description=False,
)
async def telegram_delete_webhook(drop_pending_updates: bool = False) -> bool:
    telegram = get_telegram_api()
    return await telegram.delete_webhook(drop_pending_updates=drop_pending_updates)


telegram_toolkit = Toolkit.create_toolkit(
    id="telegram_toolkit",
    tools=[
        telegram_send_message,
        telegram_send_photo,
        telegram_send_document,
        telegram_get_webhook_info,
        telegram_set_webhook,
        telegram_delete_webhook,
    ],
    auth_key="telegram_bot_token",
    name="Telegram Toolkit",
    description="Tools for interacting with Telegram Bot API",
)
