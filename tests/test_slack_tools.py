from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.slack.tools import (
    get_slack_api,
    slack_toolkit,
)


@pytest.fixture
def mock_slack_response():
    return {
        "ok": True,
        "ts": "1234567890.123456",
        "message": {
            "text": "Test message",
            "ts": "1234567890.123456",
        },
    }


@pytest.fixture
def mock_api():
    with patch("pyramidpy_tools.tools.slack.tools.get_slack_api") as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


def test_tools_are_properly_configured():
    """Test that all tools are properly configured in the toolkit"""
    assert isinstance(slack_toolkit.tools[0], Tool)
    for tool in slack_toolkit.tools:
        assert isinstance(tool, Tool)
        assert tool.name.startswith("slack_")
        assert tool.description
        assert callable(tool.fn)


def test_get_slack_api_with_token():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_flow = MagicMock()
        mock_flow.context = {
            "slack_bot_token": "test-token",
            "slack_team_id": "test-team",
        }
        mock_get_flow.return_value = mock_flow

        api = get_slack_api()
        assert api.bot_token == "test-token"
        assert api.team_id == "test-team"


def test_get_slack_api_without_token():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_get_flow.return_value = None

        api = get_slack_api()
        assert api.bot_token is None
        assert api.team_id is None


@pytest.mark.asyncio
async def test_slack_list_channels(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "channels": [
            {"id": "C123", "name": "general"},
            {"id": "C456", "name": "random"},
        ],
        "response_metadata": {"next_cursor": ""},
    }

    list_channels_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_list_channels"
    )
    result = await list_channels_tool.run_async({})

    assert result["ok"] == True
    assert len(result["channels"]) == 2
    assert result["channels"][0]["name"] == "general"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_post_message(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "channel": "C123",
        "ts": "1234567890.123456",
        "message": {"text": "Test message"},
    }

    post_message_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_post_message"
    )
    result = await post_message_tool.run_async(
        {"channel_id": "C123", "text": "Test message"}
    )

    assert result["ok"] == True
    assert result["message"]["text"] == "Test message"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_reply_to_thread(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "channel": "C123",
        "ts": "1234567890.123457",
        "message": {"text": "Test reply", "thread_ts": "1234567890.123456"},
    }

    reply_thread_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_reply_to_thread"
    )
    result = await reply_thread_tool.run_async(
        {"channel_id": "C123", "thread_ts": "1234567890.123456", "text": "Test reply"}
    )

    assert result["ok"] == True
    assert result["message"]["text"] == "Test reply"
    assert result["message"]["thread_ts"] == "1234567890.123456"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_add_reaction(mock_api):
    mock_api._make_request.return_value = {"ok": True}

    add_reaction_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_add_reaction"
    )
    result = await add_reaction_tool.run_async(
        {"channel_id": "C123", "timestamp": "1234567890.123456", "reaction": "thumbsup"}
    )

    assert result["ok"] == True
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_get_channel_history(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "messages": [
            {"type": "message", "text": "Message 1", "ts": "1234567890.123456"},
            {"type": "message", "text": "Message 2", "ts": "1234567890.123457"},
        ],
        "has_more": False,
    }

    get_history_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_get_channel_history"
    )
    result = await get_history_tool.run_async({"channel_id": "C123", "limit": 2})

    assert result["ok"] == True
    assert len(result["messages"]) == 2
    assert result["messages"][0]["text"] == "Message 1"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_get_thread_replies(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "messages": [
            {"type": "message", "text": "Parent", "ts": "1234567890.123456"},
            {"type": "message", "text": "Reply 1", "ts": "1234567890.123457"},
            {"type": "message", "text": "Reply 2", "ts": "1234567890.123458"},
        ],
        "has_more": False,
    }

    get_replies_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_get_thread_replies"
    )
    result = await get_replies_tool.run_async(
        {"channel_id": "C123", "thread_ts": "1234567890.123456"}
    )

    assert result["ok"] == True
    assert len(result["messages"]) == 3
    assert result["messages"][1]["text"] == "Reply 1"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_get_users(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "members": [
            {"id": "U123", "name": "user1", "real_name": "User One"},
            {"id": "U456", "name": "user2", "real_name": "User Two"},
        ],
        "response_metadata": {"next_cursor": ""},
    }

    get_users_tool = next(t for t in slack_toolkit.tools if t.name == "slack_get_users")
    result = await get_users_tool.run_async({})

    assert result["ok"] == True
    assert len(result["members"]) == 2
    assert result["members"][0]["name"] == "user1"
    mock_api._make_request.assert_called_once()


@pytest.mark.asyncio
async def test_slack_get_user_profile(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "profile": {
            "real_name": "User One",
            "email": "user1@example.com",
            "title": "Developer",
        },
    }

    get_profile_tool = next(
        t for t in slack_toolkit.tools if t.name == "slack_get_user_profile"
    )
    result = await get_profile_tool.run_async({"user_id": "U123"})

    assert result["ok"] == True
    assert result["profile"]["real_name"] == "User One"
    assert result["profile"]["email"] == "user1@example.com"
    mock_api._make_request.assert_called_once()
