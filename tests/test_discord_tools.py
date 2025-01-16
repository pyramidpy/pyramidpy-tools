from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pyramidpy_tools.discord_bot.base import DiscordAPI
from pyramidpy_tools.discord_bot.schemas import (
    AddReactionRequest,
    CreateChannelRequest,
    DeleteMessageRequest,
    EditMessageRequest,
    RemoveReactionRequest,
    SendMessageRequest,
)
from pyramidpy_tools.discord_bot.tools import (
    discord_add_reaction,
    discord_create_channel,
    discord_delete_message,
    discord_edit_message,
    discord_get_channel,
    discord_get_message,
    discord_remove_reaction,
    discord_send_message,
    get_discord_api,
)


@pytest.fixture
def mock_discord_api():
    with patch("pyramidpy_tools.tools.discord.tools.DiscordAPI") as mock:
        mock_instance = Mock()
        mock_instance.send_message = AsyncMock()
        mock_instance.edit_message = AsyncMock()
        mock_instance.delete_message = AsyncMock()
        mock_instance.add_reaction = AsyncMock()
        mock_instance.remove_reaction = AsyncMock()
        mock_instance.create_channel = AsyncMock()
        mock_instance.get_channel = AsyncMock()
        mock_instance.get_message = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_message_response() -> Dict[str, Any]:
    return {
        "id": "123456789",
        "channel_id": "987654321",
        "content": "Test message",
        "author": {
            "id": "111111111",
            "username": "test_user",
        },
    }


@pytest.mark.asyncio
class TestDiscordTools:
    async def test_send_message(self, mock_discord_api, sample_message_response):
        mock_discord_api.send_message.return_value = sample_message_response

        result = await discord_send_message.run_async(
            {"channel_id": "123", "content": "Hello, World!", "tts": False}
        )

        assert result == sample_message_response
        mock_discord_api.send_message.assert_called_once()
        request = mock_discord_api.send_message.call_args[0][0]
        assert isinstance(request, SendMessageRequest)
        assert request.channel_id == "123"
        assert request.content == "Hello, World!"

    async def test_edit_message(self, mock_discord_api, sample_message_response):
        mock_discord_api.edit_message.return_value = sample_message_response

        result = await discord_edit_message.run_async(
            {"channel_id": "123", "message_id": "456", "content": "Updated message"}
        )

        assert result == sample_message_response
        mock_discord_api.edit_message.assert_called_once()
        request = mock_discord_api.edit_message.call_args[0][0]
        assert isinstance(request, EditMessageRequest)
        assert request.channel_id == "123"
        assert request.message_id == "456"
        assert request.content == "Updated message"

    async def test_delete_message(self, mock_discord_api):
        mock_discord_api.delete_message.return_value = True

        result = await discord_delete_message.run_async(
            {"channel_id": "123", "message_id": "456"}
        )

        assert result is True
        mock_discord_api.delete_message.assert_called_once()
        request = mock_discord_api.delete_message.call_args[0][0]
        assert isinstance(request, DeleteMessageRequest)
        assert request.channel_id == "123"
        assert request.message_id == "456"

    async def test_add_reaction(self, mock_discord_api):
        mock_discord_api.add_reaction.return_value = True

        result = await discord_add_reaction.run_async(
            {"channel_id": "123", "message_id": "456", "emoji": "👍"}
        )

        assert result is True
        mock_discord_api.add_reaction.assert_called_once()
        request = mock_discord_api.add_reaction.call_args[0][0]
        assert isinstance(request, AddReactionRequest)
        assert request.channel_id == "123"
        assert request.message_id == "456"
        assert request.emoji == "👍"

    async def test_remove_reaction(self, mock_discord_api):
        mock_discord_api.remove_reaction.return_value = True

        result = await discord_remove_reaction.run_async(
            {"channel_id": "123", "message_id": "456", "emoji": "👍", "user_id": "789"}
        )

        assert result is True
        mock_discord_api.remove_reaction.assert_called_once()
        request = mock_discord_api.remove_reaction.call_args[0][0]
        assert isinstance(request, RemoveReactionRequest)
        assert request.channel_id == "123"
        assert request.message_id == "456"
        assert request.emoji == "👍"
        assert request.user_id == "789"

    async def test_create_channel(self, mock_discord_api):
        channel_response = {
            "id": "123456789",
            "name": "test-channel",
            "type": 0,
            "guild_id": "987654321",
        }
        mock_discord_api.create_channel.return_value = channel_response

        result = await discord_create_channel.run_async(
            {"guild_id": "123", "name": "test-channel", "topic": "Test topic"}
        )

        assert result == channel_response
        mock_discord_api.create_channel.assert_called_once()
        request = mock_discord_api.create_channel.call_args[0][0]
        assert isinstance(request, CreateChannelRequest)
        assert request.guild_id == "123"
        assert request.name == "test-channel"
        assert request.topic == "Test topic"

    async def test_get_channel(self, mock_discord_api):
        channel_response = {
            "id": "123456789",
            "name": "test-channel",
            "type": 0,
            "guild_id": "987654321",
        }
        mock_discord_api.get_channel.return_value = channel_response

        result = await discord_get_channel.run_async({"channel_id": "123"})

        assert result == channel_response
        mock_discord_api.get_channel.assert_called_once_with("123")

    async def test_get_message(self, mock_discord_api, sample_message_response):
        mock_discord_api.get_message.return_value = sample_message_response

        result = await discord_get_message.run_async(
            {"channel_id": "123", "message_id": "456"}
        )

        assert result == sample_message_response
        mock_discord_api.get_message.assert_called_once_with("123", "456")

    def test_get_discord_api_with_token(self):
        with patch("pyramidpy_tools.tools.discord.tools.get_flow") as mock_get_flow:
            mock_flow = Mock()
            mock_flow.context = {"discord_bot_token": "test-token"}
            mock_get_flow.return_value = mock_flow

            api = get_discord_api()
            assert isinstance(api, DiscordAPI)

    def test_get_discord_api_without_token(self):
        with patch("pyramidpy_tools.tools.discord.tools.get_flow") as mock_get_flow:
            mock_get_flow.return_value = None

            api = get_discord_api()
            assert isinstance(api, DiscordAPI)
