from typing import Optional, List, Dict

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit
from pyramidpy_tools.utilities.auth import get_auth_from_context

from .base import SlackAPI
from .schemas import SlackAuthConfigSchema

AUTH_KEY = "slack_auth"


def get_slack_api() -> SlackAPI:
    """Get Slack API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        auth = get_auth_from_context(flow.context, AUTH_KEY)
        if auth:
            try:
                auth = SlackAuthConfigSchema(**auth)
                return SlackAPI(token=auth.slack_api_token)
            except Exception as e:
                raise ValueError("Slack API token not configured") from e
    return SlackAPI()


@tool(
    name="slack_list_channels",
    description="List public channels in the workspace with pagination",
    include_return_description=False,
)
async def slack_list_channels(limit: Optional[int] = 100, cursor: Optional[str] = None):
    slack = get_slack_api()
    return await slack.list_channels(limit, cursor)


@tool(
    name="slack_post_message",
    description="Post a new message to a Slack channel",
    include_return_description=False,
)
async def slack_post_message(
    channel_id: str,
    text: str,
    attachments: Optional[List[Dict]] = None,
    thread_ts: Optional[str] = None,
):
    slack = get_slack_api()
    return await slack.post_message(channel_id, text, attachments, thread_ts)


@tool(
    name="slack_reply_to_thread",
    description="Reply to a specific message thread in Slack",
    include_return_description=False,
)
async def slack_reply_to_thread(
    channel_id: str,
    thread_ts: str,
    text: str,
    attachments: Optional[List[Dict]] = None,
):
    slack = get_slack_api()
    return await slack.reply_to_thread(channel_id, thread_ts, text, attachments)


@tool(
    name="slack_add_reaction",
    description="Add a reaction emoji to a message",
    include_return_description=False,
)
async def slack_add_reaction(channel_id: str, timestamp: str, reaction: str):
    slack = get_slack_api()
    return await slack.add_reaction(channel_id, timestamp, reaction)


@tool(
    name="slack_get_channel_history",
    description="Get recent messages from a channel",
    include_return_description=False,
)
async def slack_get_channel_history(channel_id: str, limit: Optional[int] = 10):
    slack = get_slack_api()
    return await slack.get_channel_history(channel_id, limit)


@tool(
    name="slack_get_thread_replies",
    description="Get all replies in a message thread",
    include_return_description=False,
)
async def slack_get_thread_replies(channel_id: str, thread_ts: str):
    slack = get_slack_api()
    return await slack.get_thread_replies(channel_id, thread_ts)


@tool(
    name="slack_get_users",
    description="Get a list of all users in the workspace with their basic profile information",
    include_return_description=False,
)
async def slack_get_users(cursor: Optional[str] = None, limit: Optional[int] = 100):
    slack = get_slack_api()
    return await slack.get_users(limit, cursor)


@tool(
    name="slack_get_user_profile",
    description="Get detailed profile information for a specific user",
    include_return_description=False,
)
async def slack_get_user_profile(user_id: str):
    slack = get_slack_api()
    return await slack.get_user_profile(user_id)


slack_toolkit = Toolkit.create_toolkit(
    id="slack_toolkit",
    tools=[
        slack_list_channels,
        slack_post_message,
        slack_reply_to_thread,
        slack_add_reaction,
        slack_get_channel_history,
        slack_get_thread_replies,
        slack_get_users,
        slack_get_user_profile,
    ],
    auth_key="slack_auth",
    auth_config_schema=SlackAuthConfigSchema,
    requires_config=True,
    name="Slack Toolkit",
    description="Tools for interacting with Slack API",
)
