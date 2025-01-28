import logging
from typing import Callable, Dict, Coroutine, Any
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, Update, WebhookInfo
import uvicorn
from pyramidpy_tools.settings import settings
import asyncio

logger = logging.getLogger(__name__)


def echo_message_handler(bot: Bot, message: Message):
    """
    Handle a message from a Telegram bot.
    """
    logger.info(f"Received message: {message}")
    return "Received message from " + message.from_user.full_name


class MultiBotWebhookHandler:
    """
    Handle webhook updates for multiple bots.
    """

    message_handler: Callable[[Bot, Message], Coroutine[Any, Any, None]]

    def __init__(
        self,
        message_handler: Callable[[Bot, Message], Coroutine[Any, Any, None]]
        | None = None,
        app: FastAPI | None = None,
    ):
        self.bots: Dict[str, Bot] = {}
        self.dp = Dispatcher()
        self.app = app or FastAPI()
        self.setup_handlers()
        self.setup_routes()
        self.message_handler = message_handler or echo_message_handler

    def setup_handlers(self):
        """Setup default message handlers"""

        @self.dp.message()
        async def handle_message(message: Message, bot: Bot) -> None:
            """Default message handler"""
            try:
                await self.message_handler(bot, message)

            except Exception as e:
                logger.error(f"Error handling message: {e}")

    def setup_routes(self):
        """Setup webhook routes for each bot"""

        @self.app.post("/webhook/{bot_token}")
        async def handle_webhook(bot_token: str, request: Request):
            """Handle webhook updates for specific bot"""
            try:
                # Get or create bot instance
                bot = await self.get_or_create_bot(bot_token)

                # Get update data
                update_data = await request.json()
                update = Update.model_validate(update_data)

                # Process update
                await self.dp.feed_update(bot, update)

                return {"status": "ok"}
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def get_or_create_bot(self, token: str) -> Bot:
        """Get existing bot instance or create new one"""
        if token not in self.bots:
            bot = Bot(
                token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            self.bots[token] = bot
            # Don't automatically set webhook - let it be done explicitly
            logger.info("Created new bot instance")
        return self.bots[token]

    async def setup_webhook(self, token: str) -> WebhookInfo:
        """
        Explicitly set up webhook for a bot.

        Args:
            token: Bot token to set up webhook for

        Returns:
            WebhookInfo with current webhook status
        """
        bot = await self.get_or_create_bot(token)

        # Construct webhook URL
        webhook_url = (
            f"{settings.tool_provider.telegram_webhook_base_url}/webhook/{token}"
        )

        # Set webhook with secret token for additional security
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.tool_provider.telegram_webhook_secret,
            drop_pending_updates=True,  # Optional: ignore updates that arrived while bot was offline
        )

        # Get and return webhook info
        webhook_info = await bot.get_webhook_info()
        logger.info(
            f"Webhook set for bot. URL: {webhook_url}, "
            f"Pending updates: {webhook_info.pending_update_count}"
        )
        return webhook_info

    async def remove_webhook(self, token: str):
        """Remove webhook for a bot"""
        bot = await self.get_or_create_bot(token)
        await bot.delete_webhook()
        logger.info("Webhook removed for bot")

    async def get_webhook_info(self, token: str) -> WebhookInfo:
        """Get current webhook info for a bot"""
        bot = await self.get_or_create_bot(token)
        return await bot.get_webhook_info()

    async def stop(self):
        """Stop all bots and close connections"""
        for bot in self.bots.values():
            try:
                await bot.delete_webhook()  # Remove webhooks when stopping
                if hasattr(bot, "session") and bot.session:
                    await bot.session.close()
                    # Ensure the session is fully closed
                    await asyncio.sleep(0.25)  # Give a moment for connections to close
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")

        # Clear the bots dictionary
        self.bots.clear()
        logger.info("All bots stopped and connections closed")


def run_webhook_server(
    host: str = "0.0.0.0",
    port: int = 8003,
    message_handler: Callable[[Bot, Message], str] | None = None,
    app: FastAPI | None = None,
):
    """Run webhook server"""
    handler = MultiBotWebhookHandler(message_handler, app)

    logger.info(f"Starting webhook server on {host}:{port}")
    try:
        uvicorn.run(handler.app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        logger.info("Webhook server stopped by user")
    except Exception as e:
        logger.error(f"Webhook server error: {e}")
        raise
    finally:
        # Ensure we close all bot connections and cleanup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handler.stop())
        finally:
            loop.close()
            logger.info("Cleaned up all resources")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_webhook_server()
