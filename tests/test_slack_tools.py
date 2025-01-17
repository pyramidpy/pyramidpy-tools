from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.slack.tools import (
    get_slack_api,
    slack_toolkit,
)


@pytest.fixture
def mock_message_response():
    return {
        "ok": True,
        "ts": "1234567890.123456",
        "channel": "C123",
        "message": {
            "text": "Test message",
            "ts": "1234567890.123456",
            "thread_ts": None,
        },
    }


@pytest.fixture
def mock_channels_response():
    return {
        "ok": True,
        "channels": [
            {"id": "C123", "name": "general", "is_channel": True},
            {"id": "C456", "name": "random", "is_channel": True},
        ],
        "response_metadata": {"next_cursor": ""},
    }


@pytest.fixture
def mock_users_response():
    return {
        "ok": True,
        "members": [
            {
                "id": "U123",
                "name": "user1",
                "real_name": "User One",
                "profile": {
                    "email": "user1@example.com",
                    "title": "Developer",
                },
            },
            {
                "id": "U456",
                "name": "user2",
                "real_name": "User Two",
                "profile": {
                    "email": "user2@example.com",
                    "title": "Manager",
                },
            },
        ],
        "response_metadata": {"next_cursor": ""},
    }


class TestSlackAPI:
    def test_get_slack_api_with_token(self):
        with patch("pyramidpy_tools.slack.tools.get_flow") as mock_get_flow:
            mock_flow = MagicMock()
            mock_flow.context = {"auth": {"slack_api_token": "test-token"}}
            mock_get_flow.return_value = mock_flow

            api = get_slack_api()
            assert api.client.token == "test-token"

    def test_get_slack_api_without_token(self):
        with patch("pyramidpy_tools.slack.tools.get_flow") as mock_get_flow:
            mock_get_flow.return_value = None

            with pytest.raises(AttributeError):
                get_slack_api()

    def test_get_slack_api_error_handling(self):
        with patch("pyramidpy_tools.slack.tools.get_flow") as mock_get_flow:
            mock_get_flow.return_value = None
            with pytest.raises(AttributeError):
                get_slack_api()


@pytest.mark.asyncio
class TestSlackTools:
    @pytest.fixture
    def mock_api(self):
        with patch("pyramidpy_tools.slack.tools.get_slack_api") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    async def test_tools_configuration(self):
        """Test that all tools are properly configured in the toolkit"""
        assert isinstance(slack_toolkit.tools[0], Tool)
        for tool in slack_toolkit.tools:
            assert isinstance(tool, Tool)
            assert tool.name.startswith("slack_")
            assert tool.description
            assert callable(tool.fn)

        assert slack_toolkit.id == "slack_toolkit"
        assert slack_toolkit.requires_config is True
        assert "slack" in slack_toolkit.description.lower()

    async def test_slack_list_channels(self, mock_api, mock_channels_response):
        mock_api.list_channels.return_value = mock_channels_response

        list_channels_tool = next(
            t for t in slack_toolkit.tools if t.name == "slack_list_channels"
        )
        result = await list_channels_tool.run_async({})

        assert result["ok"] is True
        assert len(result["channels"]) == 2
        assert result["channels"][0]["name"] == "general"
        mock_api.list_channels.assert_called_once_with(100, None)

    async def test_slack_post_message(self, mock_api, mock_message_response):
        mock_api.post_message.return_value = mock_message_response

        post_message_tool = next(
            t for t in slack_toolkit.tools if t.name == "slack_post_message"
        )
        result = await post_message_tool.run_async(
            {
                "channel_id": "C123",
                "text": "Test message",
            }
        )

        assert result["ok"] is True
        assert result["message"]["text"] == "Test message"
        assert result["channel"] == "C123"
        mock_api.post_message.assert_called_once_with(
            "C123", "Test message", None, None
        )

    async def test_slack_reply_to_thread(self, mock_api, mock_message_response):
        response = {**mock_message_response}
        response["message"]["thread_ts"] = "1234567890.123456"
        mock_api.reply_to_thread.return_value = response

        reply_thread_tool = next(
            t for t in slack_toolkit.tools if t.name == "slack_reply_to_thread"
        )
        result = await reply_thread_tool.run_async(
            {
                "channel_id": "C123",
                "thread_ts": "1234567890.123456",
                "text": "Test reply",
            }
        )

        assert result["ok"] is True
        assert result["message"]["text"] == "Test message"
        assert result["message"]["thread_ts"] == "1234567890.123456"
        mock_api.reply_to_thread.assert_called_once_with(
            "C123", "1234567890.123456", "Test reply", None
        )

    async def test_slack_add_reaction(self, mock_api):
        mock_api.add_reaction.return_value = {"ok": True}

        add_reaction_tool = next(
            t for t in slack_toolkit.tools if t.name == "slack_add_reaction"
        )
        result = await add_reaction_tool.run_async(
            {
                "channel_id": "C123",
                "timestamp": "1234567890.123456",
                "reaction": "thumbsup",
            }
        )

        assert result["ok"] is True
        mock_api.add_reaction.assert_called_once_with(
            "C123", "1234567890.123456", "thumbsup"
        )

    async def test_slack_get_channel_history(self, mock_api):
        mock_api.get_channel_history.return_value = {
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
        result = await get_history_tool.run_async(
            {
                "channel_id": "C123",
            }
        )

        assert result["ok"] is True
        assert len(result["messages"]) == 2
        assert result["messages"][0]["text"] == "Message 1"
        assert not result["has_more"]
        mock_api.get_channel_history.assert_called_once_with("C123", 10)

    async def test_slack_get_thread_replies(self, mock_api):
        mock_api.get_thread_replies.return_value = {
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
            {
                "channel_id": "C123",
                "thread_ts": "1234567890.123456",
            }
        )

        assert result["ok"] is True
        assert len(result["messages"]) == 3
        assert result["messages"][1]["text"] == "Reply 1"
        mock_api.get_thread_replies.assert_called_once_with("C123", "1234567890.123456")

    async def test_slack_get_users(self, mock_api, mock_users_response):
        mock_api.get_users.return_value = mock_users_response

        get_users_tool = next(
            t for t in slack_toolkit.tools if t.name == "slack_get_users"
        )
        result = await get_users_tool.run_async({})

        assert result["ok"] is True
        assert len(result["members"]) == 2
        assert result["members"][0]["name"] == "user1"
        assert result["members"][0]["profile"]["email"] == "user1@example.com"
        mock_api.get_users.assert_called_once_with(100, None)

    async def test_slack_get_user_profile(self, mock_api):
        mock_api.get_user_profile.return_value = {
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

        assert result["ok"] is True
        assert result["profile"]["real_name"] == "User One"
        assert result["profile"]["email"] == "user1@example.com"
        mock_api.get_user_profile.assert_called_once_with("U123")

    async def test_error_handling(self, mock_api):
        """Test error handling for all tools"""
        mock_api.list_channels.side_effect = Exception("API Error")
        mock_api.post_message.side_effect = Exception("API Error")
        mock_api.reply_to_thread.side_effect = Exception("API Error")
        mock_api.add_reaction.side_effect = Exception("API Error")
        mock_api.get_channel_history.side_effect = Exception("API Error")
        mock_api.get_thread_replies.side_effect = Exception("API Error")
        mock_api.get_users.side_effect = Exception("API Error")
        mock_api.get_user_profile.side_effect = Exception("API Error")

        for tool in slack_toolkit.tools:
            with pytest.raises(Exception) as exc_info:
                params = {}
                if tool.name == "slack_post_message":
                    params = {"channel_id": "C123", "text": "test"}
                elif tool.name == "slack_reply_to_thread":
                    params = {"channel_id": "C123", "thread_ts": "123", "text": "test"}
                elif tool.name == "slack_add_reaction":
                    params = {
                        "channel_id": "C123",
                        "timestamp": "123",
                        "reaction": "thumbsup",
                    }
                elif tool.name == "slack_get_user_profile":
                    params = {"user_id": "U123"}
                elif tool.name == "slack_get_thread_replies":
                    params = {"channel_id": "C123", "thread_ts": "123"}
                elif tool.name == "slack_get_channel_history":
                    params = {"channel_id": "C123"}
                await tool.run_async(params)
            assert str(exc_info.value) == "API Error"
