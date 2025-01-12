from typing import Any, Dict, List, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile, Message
from aiogram.utils.text_decorations import html_decoration, markdown_decoration

from app.settings import settings

from .schemas import (
    SendDocumentRequest,
    SendMessageRequest,
    SendPhotoRequest,
    WebhookInfo,
)


class TelegramAPI:
    """Client for interacting with Telegram Bot API"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.tool_provider.telegram_bot_token
        if not self.token:
            raise ValueError("Telegram bot token not found")

        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

    async def send_message(self, request: SendMessageRequest) -> Dict[str, Any]:
        """Send a text message"""
        # Escape text based on parse mode
        text = request.text
        if request.parse_mode == "MarkdownV2":
            text = self.escape_markdown(text)
        elif request.parse_mode == "HTML":
            text = self.escape_html(text)

        message = await self.bot.send_message(
            chat_id=request.chat_id,
            text=text,
            parse_mode=request.parse_mode,
            disable_web_page_preview=request.disable_web_page_preview,
            disable_notification=request.disable_notification,
            reply_to_message_id=request.reply_to_message_id,
        )
        return message.model_dump()

    async def send_photo(self, request: SendPhotoRequest) -> Dict[str, Any]:
        """Send a photo"""
        if request.photo.startswith(("http://", "https://")):
            photo = request.photo
        else:
            photo = FSInputFile(request.photo)

        # Escape caption based on parse mode
        caption = request.caption
        if caption:
            if request.parse_mode == "MarkdownV2":
                caption = self.escape_markdown(caption)
            elif request.parse_mode == "HTML":
                caption = self.escape_html(caption)

        message = await self.bot.send_photo(
            chat_id=request.chat_id,
            photo=photo,
            caption=caption,
            parse_mode=request.parse_mode,
            disable_notification=request.disable_notification,
            reply_to_message_id=request.reply_to_message_id,
        )
        return message.model_dump()

    async def send_document(self, request: SendDocumentRequest) -> Dict[str, Any]:
        """Send a document"""
        if request.document.startswith(("http://", "https://")):
            document = request.document
        else:
            document = FSInputFile(request.document)

        # Escape caption based on parse mode
        caption = request.caption
        if caption:
            if request.parse_mode == "MarkdownV2":
                caption = self.escape_markdown(caption)
            elif request.parse_mode == "HTML":
                caption = self.escape_html(caption)

        message = await self.bot.send_document(
            chat_id=request.chat_id,
            document=document,
            caption=caption,
            parse_mode=request.parse_mode,
            disable_notification=request.disable_notification,
            reply_to_message_id=request.reply_to_message_id,
        )
        return message.model_dump()

    async def get_webhook_info(self) -> WebhookInfo:
        """Get current webhook status"""
        info = await self.bot.get_webhook_info()
        return WebhookInfo(**info.model_dump())

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
    ) -> bool:
        """Set webhook for the bot"""
        return await self.bot.set_webhook(
            url=url,
            certificate=FSInputFile(certificate) if certificate else None,
            ip_address=ip_address,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token or settings.tool_provider.telegram_webhook_secret,
        )

    async def delete_webhook(self, drop_pending_updates: bool = False) -> bool:
        """Remove webhook integration"""
        return await self.bot.delete_webhook(drop_pending_updates=drop_pending_updates)

    def escape_markdown(self, text: str) -> str:
        """Escape markdown characters in text"""
        return markdown_decoration.quote(text)

    def escape_html(self, text: str) -> str:
        """Escape HTML characters in text"""
        return html_decoration.quote(text)
