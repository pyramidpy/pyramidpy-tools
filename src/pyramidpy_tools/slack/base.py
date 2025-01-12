import re
from typing import Any, Dict, List, Optional

from fastapi.logger import logger
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient

from app.settings import settings


def convert_md_links_to_slack(text: str) -> str:
    """Convert markdown links to Slack format"""
    md_link_pattern = r"\[(?P<text>[^\]]+)]\((?P<url>[^\)]+)\)"

    def to_slack_link(match):
        return f'<{match.group("url")}|{match.group("text")}>'

    return re.sub(
        r"\*\*(.*?)\*\*", r"*\1*", re.sub(md_link_pattern, to_slack_link, text)
    )


def format_as_chat_message(message: dict) -> dict:
    """Format a Slack message as a chat message."""
    return {
        "text": message.get("text"),
    }


class SlackAPI:
    def __init__(self, token: str | None = None):
        self.client = WebClient(
            token=token or settings.tool_provider.slack_api_token.get_secret_value()
        )

    async def list_channels(
        self, limit: int = 100, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            return await self.client.conversations_list(
                types="public_channel",
                exclude_archived=True,
                limit=min(limit, 200),
                cursor=cursor,
            )
        except SlackApiError as e:
            logger.error(f"Error listing channels: {e}")
            return e.response

    async def post_message(
        self,
        channel_id: str,
        text: str,
        attachments: List[Dict] | None = None,
        thread_ts: str | None = None,
    ) -> Dict[str, Any]:
        try:
            return await self.client.chat_postMessage(
                channel=channel_id,
                text=convert_md_links_to_slack(text),
                attachments=attachments if attachments else [],
                thread_ts=thread_ts,
            )
        except SlackApiError as e:
            logger.error(f"Error posting message: {e}")
            return e.response

    async def reply_to_thread(
        self,
        channel_id: str,
        thread_ts: str,
        text: str,
        attachments: List[Dict] | None = None,
    ) -> Dict[str, Any]:
        return await self.post_message(
            channel_id=channel_id,
            thread_ts=thread_ts,
            text=text,
            attachments=attachments,
        )

    async def add_reaction(
        self, channel_id: str, timestamp: str, reaction: str
    ) -> Dict[str, Any]:
        try:
            return await self.client.reactions_add(
                channel=channel_id, timestamp=timestamp, name=reaction
            )
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e}")
            return e.response

    async def get_channel_history(
        self, channel_id: str, limit: int = 10
    ) -> Dict[str, Any]:
        try:
            return await self.client.conversations_history(
                channel=channel_id, limit=limit
            )
        except SlackApiError as e:
            logger.error(f"Error getting channel history: {e}")
            return e.response

    async def get_thread_replies(
        self, channel_id: str, thread_ts: str, as_chat_messages: bool = True
    ) -> List[Dict] | Dict[str, Any]:
        try:
            result = await self.client.conversations_replies(
                channel=channel_id, ts=thread_ts
            )
            if as_chat_messages:
                return [
                    format_as_chat_message(message) for message in result["messages"]
                ]
            return result["messages"]
        except SlackApiError as e:
            logger.error(f"Error getting thread replies: {e}")
            return []

    async def get_users(
        self, limit: int = 100, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            return await self.client.users_list(limit=min(limit, 200), cursor=cursor)
        except SlackApiError as e:
            logger.error(f"Error getting users: {e}")
            return e.response

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        try:
            return await self.client.users_profile_get(
                user=user_id, include_labels=True
            )
        except SlackApiError as e:
            logger.error(f"Error getting user profile: {e}")
            return e.response
