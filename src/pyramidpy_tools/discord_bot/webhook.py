from datetime import datetime
from typing import Any, Dict

import nacl.exceptions
import nacl.signing
from fastapi import APIRouter, Header, HTTPException, Request

from pyramidpy_tools.settings import settings

from .base import DiscordAPI
from .schemas import WebhookPayload


class DiscordWebhookHandler:
    """
    Discord webhook handler.
    Usage:
    from pyramidpy_tools.discord.webhook import DiscordWebhookHandler

    discord_handler = DiscordWebhookHandler()
    app.include_router(discord_handler.get_router(), prefix="/discord")
    """

    def __init__(self):
        self.api = DiscordAPI()
        self.router = APIRouter()
        self.setup_routes()
        self.commands = {
            "help": self.cmd_help,
            "echo": self.cmd_echo,
            "info": self.cmd_info,
            "search": self.cmd_search,
            "ping": self.cmd_ping,
        }

    def setup_routes(self):
        """Setup webhook routes"""
        self.router.post("/webhook", response_model=Dict[str, Any])(self.handle_webhook)

    def verify_signature(self, body: bytes, timestamp: str, signature: str) -> bool:
        """Verify the request signature from Discord"""
        try:
            # Get the public key from settings
            public_key = settings.tool_provider.discord_public_key
            if not public_key:
                raise ValueError("Discord public key not found in settings")

            # Create the message to verify
            message = timestamp.encode() + body

            # Verify the signature
            verify_key = nacl.signing.VerifyKey(bytes.fromhex(public_key))
            verify_key.verify(message, bytes.fromhex(signature))
            return True
        except (nacl.exceptions.BadSignatureError, ValueError):
            return False

    async def handle_webhook(
        self,
        request: Request,
        x_signature_timestamp: str = Header(...),
        x_signature_ed25519: str = Header(...),
    ) -> Dict[str, Any]:
        """Handle incoming webhook requests from Discord"""
        # Get the raw body
        body = await request.body()

        # Verify the signature
        if not self.verify_signature(body, x_signature_timestamp, x_signature_ed25519):
            raise HTTPException(status_code=401, detail="Invalid request signature")

        try:
            # Parse the payload
            payload_data = await request.json()
            payload = WebhookPayload(**payload_data)

            # Handle different types of interactions
            if payload.type == 1:  # PING
                return {"type": 1}  # PONG
            elif payload.type == 2:  # APPLICATION_COMMAND
                # Handle slash commands here
                return await self.handle_command(payload)
            else:
                # Handle other types of interactions
                return await self.handle_other_interaction(payload)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing webhook: {str(e)}"
            )

    async def handle_command(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Handle slash command interactions"""
        command_name = payload.data.get("name")

        if command_name in self.commands:
            return await self.commands[command_name](payload)

        return {"type": 4, "data": {"content": f"Unknown command: {command_name}"}}

    async def handle_other_interaction(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Handle other types of interactions"""
        # Add handling for other interaction types here
        return {"type": 4, "data": {"content": "Interaction received"}}

    async def cmd_help(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Help command that lists available commands"""
        help_text = """
Available commands:
• `/help` - Show this help message
• `/ping` - Check if the bot is responsive
• `/echo <message>` - Repeat your message
• `/info` - Get information about the server and channel
• `/search <query>` - Search for messages containing the query
        """
        return {"type": 4, "data": {"content": help_text.strip()}}

    async def cmd_ping(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Simple ping command to check bot responsiveness"""
        return {"type": 4, "data": {"content": "🏓 Pong! Bot is responsive."}}

    async def cmd_echo(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Echo command that repeats the user's message"""
        options = payload.data.get("options", [])
        message = next(
            (opt["value"] for opt in options if opt["name"] == "message"), ""
        )

        return {"type": 4, "data": {"content": f"Echo: {message}"}}

    async def cmd_info(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Info command that provides information about the server and channel"""
        try:
            channel = await self.api.get_channel(payload.channel_id)

            info_text = f"""
Channel Information:
• Name: {channel.get('name', 'Unknown')}
• ID: {channel.get('id', 'Unknown')}
• Type: {channel.get('type', 'Unknown')}
• Topic: {channel.get('topic', 'No topic set')}

Server ID: {payload.guild_id or 'Not in a server'}
Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
            """

            return {"type": 4, "data": {"content": info_text.strip()}}
        except Exception as e:
            return {
                "type": 4,
                "data": {"content": f"Error getting information: {str(e)}"},
            }

    async def cmd_search(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Search command that looks for messages containing the query"""
        options = payload.data.get("options", [])
        query = next((opt["value"] for opt in options if opt["name"] == "query"), "")

        if not query:
            return {"type": 4, "data": {"content": "Please provide a search query"}}

        try:
            # This is a placeholder for actual message search functionality
            # You would need to implement message history search in the DiscordAPI class
            return {
                "type": 4,
                "data": {
                    "content": f"🔍 Search results for '{query}':\nSearch functionality is coming soon!"
                },
            }
        except Exception as e:
            return {
                "type": 4,
                "data": {"content": f"Error performing search: {str(e)}"},
            }

    def get_router(self) -> APIRouter:
        """Get the FastAPI router for mounting"""
        return self.router
