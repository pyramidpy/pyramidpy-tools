from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.telegram.tools import (
    get_telegram_api,
    telegram_toolkit,
)


@pytest.fixture
def mock_api():
    with patch("pyramidpy_tools.tools.telegram.tools.get_telegram_api") as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


def test_tools_are_properly_configured():
    """Test that all tools are properly configured in the toolkit"""
    assert isinstance(telegram_toolkit.tools[0], Tool)
    for tool in telegram_toolkit.tools:
        assert isinstance(tool, Tool)
        assert tool.name.startswith("telegram_")
        assert tool.description
        assert callable(tool.fn)


def test_get_telegram_api_with_token():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_flow = MagicMock()
        mock_flow.context = {"telegram_bot_token": "test-token"}
        mock_get_flow.return_value = mock_flow

        api = get_telegram_api()
        assert api.token == "test-token"


def test_get_telegram_api_without_token():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_get_flow.return_value = None

        api = get_telegram_api()
        assert api.token is None


async def test_telegram_send_message(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": {
            "message_id": 123,
            "text": "Test message",
            "chat": {"id": "12345", "type": "private"},
        },
    }

    send_message_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_send_message"
    )
    result = await send_message_tool.run_async(
        {"chat_id": "12345", "text": "Test message", "parse_mode": "HTML"}
    )

    assert result["ok"] is True
    assert result["result"]["text"] == "Test message"
    assert result["result"]["message_id"] == 123
    mock_api._make_request.assert_called_once()


async def test_telegram_send_photo(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": {
            "message_id": 124,
            "photo": [{"file_id": "test-photo-id"}],
            "chat": {"id": "12345", "type": "private"},
        },
    }

    send_photo_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_send_photo"
    )
    result = await send_photo_tool.run_async(
        {"chat_id": "12345", "photo": "photo_url", "caption": "Test photo"}
    )

    assert result["ok"] is True
    assert "photo" in result["result"]
    assert result["result"]["message_id"] == 124
    mock_api._make_request.assert_called_once()


async def test_telegram_send_document(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": {
            "message_id": 125,
            "document": {"file_id": "test-doc-id"},
            "chat": {"id": "12345", "type": "private"},
        },
    }

    send_document_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_send_document"
    )
    result = await send_document_tool.run_async(
        {"chat_id": "12345", "document": "document_url", "caption": "Test document"}
    )

    assert result["ok"] is True
    assert "document" in result["result"]
    assert result["result"]["message_id"] == 125
    mock_api._make_request.assert_called_once()


async def test_telegram_get_webhook_info(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": {
            "url": "https://example.com/webhook",
            "has_custom_certificate": False,
            "pending_update_count": 0,
        },
    }

    get_webhook_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_get_webhook_info"
    )
    result = await get_webhook_tool.run_async({})

    assert result["ok"] is True
    assert result["result"]["url"] == "https://example.com/webhook"
    mock_api._make_request.assert_called_once()


async def test_telegram_set_webhook(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": True,
        "description": "Webhook was set",
    }

    set_webhook_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_set_webhook"
    )
    result = await set_webhook_tool.run_async(
        {
            "url": "https://example.com/webhook",
            "max_connections": 100,
            "allowed_updates": ["message", "callback_query"],
        }
    )

    assert result is True
    mock_api._make_request.assert_called_once()


async def test_telegram_delete_webhook(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": True,
        "description": "Webhook was deleted",
    }

    delete_webhook_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_delete_webhook"
    )
    result = await delete_webhook_tool.run_async({"drop_pending_updates": True})

    assert result is True
    mock_api._make_request.assert_called_once()


async def test_telegram_send_message_with_reply(mock_api):
    mock_api._make_request.return_value = {
        "ok": True,
        "result": {
            "message_id": 126,
            "text": "Reply message",
            "chat": {"id": "12345", "type": "private"},
            "reply_to_message": {"message_id": 125},
        },
    }

    send_message_tool = next(
        t for t in telegram_toolkit.tools if t.name == "telegram_send_message"
    )
    result = await send_message_tool.run_async(
        {"chat_id": "12345", "text": "Reply message", "reply_to_message_id": 125}
    )

    assert result["ok"] is True
    assert result["result"]["text"] == "Reply message"
    assert result["result"]["reply_to_message"]["message_id"] == 125
    mock_api._make_request.assert_called_once()
