import asyncio
import logging
import sys
from typing import Optional, Callable, Any
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from pyramidpy_tools.settings import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
        self, token: str, message_handler: Optional[Callable[[Message], Any]] = None
    ):
        """Initialize the bot with token and optional message handler."""
        self.token = token
        self.dp = Dispatcher()
        self.bot: Optional[Bot] = None
        self.setup_handlers(message_handler)

    def setup_handlers(self, custom_message_handler: Optional[Callable] = None):
        """Setup message handlers."""

        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message) -> None:
            """Handle /start command."""
            await message.answer(
                f"Hello, {html.bold(message.from_user.full_name)}!\n"
                f"Your chat ID is: {html.code(message.chat.id)}"
            )
            logger.info(f"New chat started. Chat ID: {message.chat.id}")

        @self.dp.message()
        async def message_handler(message: Message) -> None:
            """Handle all other messages."""
            if custom_message_handler:
                await custom_message_handler(message)
            else:
                # Default echo behavior
                try:
                    await message.send_copy(chat_id=message.chat.id)
                except TypeError:
                    await message.answer("Nice try!")

                logger.info(
                    f"Message from {message.from_user.full_name} "
                    f"(chat_id: {message.chat.id}): {message.text}"
                )

    async def start(self):
        """Start the bot with polling."""
        self.bot = Bot(
            token=self.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        logger.info("Starting bot polling...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error in bot polling: {e}")
            raise

    async def stop(self):
        """Stop the bot."""
        if self.bot:
            await self.bot.session.close()
            logger.info("Bot stopped")


def run_bot(token: Optional[str] = None, message_handler: Optional[Callable] = None):
    """
    Run the bot with polling.

    Args:
        token: Bot token. If not provided, will use from settings
        message_handler: Optional custom message handler
    """
    token = token or settings.tool_provider.telegram_bot_token
    if not token:
        raise ValueError("Telegram bot token not provided")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    bot = TelegramBot(token=token, message_handler=message_handler)

    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
