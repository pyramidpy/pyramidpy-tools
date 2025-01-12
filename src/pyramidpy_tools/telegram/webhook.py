from typing import Any, Dict

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from fastapi import APIRouter, Header, HTTPException, Request

from pyramidpy_tools.settings import settings

from .base import TelegramAPI


class TelegramWebhookHandler:
    def __init__(self):
        self.api = TelegramAPI()
        self.bot = self.api.bot
        self.dp = self.api.dp
        self.router = APIRouter()
        self.setup_routes()
        self.setup_handlers()

    def setup_routes(self):
        """Setup webhook routes"""
        self.router.post("/webhook", response_model=Dict[str, Any])(self.handle_webhook)

    def setup_handlers(self):
        """Setup message handlers"""

        @self.dp.message()
        async def handle_message(message: Update):
            # Handle incoming messages here
            # This is just an example echo handler
            if message.text:
                await self.bot.send_message(
                    chat_id=message.chat.id, text=f"Echo: {message.text}"
                )

    async def handle_webhook(
        self, request: Request, x_telegram_bot_api_secret_token: str = Header(None)
    ) -> Dict[str, Any]:
        """Handle incoming webhook requests"""
        # Verify secret token
        if (
            x_telegram_bot_api_secret_token
            != settings.tool_provider.telegram_webhook_secret
        ):
            raise HTTPException(status_code=401, detail="Invalid secret token")

        # Get update data
        update_data = await request.json()

        try:
            # Process update
            update = Update(**update_data)
            await self.dp.feed_update(self.bot, update)

            return {"status": "ok"}

        except TelegramBadRequest as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid update data: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing update: {str(e)}"
            )

    def get_router(self) -> APIRouter:
        """Get the FastAPI router for mounting"""
        return self.router
