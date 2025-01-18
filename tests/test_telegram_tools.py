from unittest.mock import AsyncMock, patch
import pytest

from pyramidpy_tools.telegram.base import TelegramAPI
from pyramidpy_tools.telegram.schemas import (
    SendMessageRequest,
    SendPhotoRequest,
    SendDocumentRequest,
    WebhookInfo,
)
from pyramidpy_tools.telegram.tools import (
    telegram_send_message,
    telegram_send_photo,
    telegram_send_document,
    telegram_get_webhook_info,
    telegram_set_webhook,
    telegram_delete_webhook,
)


@pytest.fixture
def mock_message_response():
    return {
        "message_id": 123,
        "text": "Test message",
        "chat": {"id": 456, "type": "private"},
    }


@pytest.fixture
def mock_photo_response():
    return {
        "message_id": 123,
        "photo": [{"file_id": "test_photo"}],
        "chat": {"id": 456, "type": "private"},
    }


@pytest.fixture
def mock_document_response():
    return {
        "message_id": 123,
        "document": {"file_id": "test_doc"},
        "chat": {"id": 456, "type": "private"},
    }


@pytest.fixture
def mock_webhook_info():
    return {
        "url": "https://test.com/webhook",
        "has_custom_certificate": False,
        "pending_update_count": 0,
    }


@pytest.mark.asyncio
async def test_get_telegram_api_with_token():
    with patch("pyramidpy_tools.telegram.tools.get_flow") as mock_get_flow:
        mock_get_flow.return_value.context = {
            "auth": {
                "telegram_bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"
            }
        }
        api = TelegramAPI(token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789")
        assert api.token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"


@pytest.mark.asyncio
async def test_get_telegram_api_without_token():
    with patch("pyramidpy_tools.telegram.tools.get_flow") as mock_get_flow:
        mock_get_flow.return_value.context = {}
        api = TelegramAPI(token="987654321:ZYXwvuTSRqpONMlkjIHgfeDCBA987654321")
        assert api.token == "987654321:ZYXwvuTSRqpONMlkjIHgfeDCBA987654321"


@pytest.mark.asyncio
async def test_telegram_send_message(mock_message_response):
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.send_message.return_value = mock_message_response
        mock_get_api.return_value = mock_api

        response = await telegram_send_message.fn(
            chat_id="123",
            text="Test message",
            parse_mode="HTML",
            disable_web_page_preview=True,
            disable_notification=True,
            reply_to_message_id=456,
        )

        expected_request = SendMessageRequest(
            chat_id="123",
            text="Test message",
            parse_mode="HTML",
            disable_web_page_preview=True,
            disable_notification=True,
            reply_to_message_id=456,
        )
        mock_api.send_message.assert_awaited_once_with(expected_request)
        assert response == mock_message_response


@pytest.mark.asyncio
async def test_telegram_send_photo(mock_photo_response):
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.send_photo.return_value = mock_photo_response
        mock_get_api.return_value = mock_api

        response = await telegram_send_photo.fn(
            chat_id="123",
            photo="test.jpg",
            caption="Test photo",
            parse_mode="HTML",
            disable_notification=True,
            reply_to_message_id=456,
        )

        expected_request = SendPhotoRequest(
            chat_id="123",
            photo="test.jpg",
            caption="Test photo",
            parse_mode="HTML",
            disable_notification=True,
            reply_to_message_id=456,
        )
        mock_api.send_photo.assert_awaited_once_with(expected_request)
        assert response == mock_photo_response


@pytest.mark.asyncio
async def test_telegram_send_document(mock_document_response):
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.send_document.return_value = mock_document_response
        mock_get_api.return_value = mock_api

        response = await telegram_send_document.fn(
            chat_id="123",
            document="test.pdf",
            caption="Test document",
            parse_mode="HTML",
            disable_notification=True,
            reply_to_message_id=456,
        )

        expected_request = SendDocumentRequest(
            chat_id="123",
            document="test.pdf",
            caption="Test document",
            parse_mode="HTML",
            disable_notification=True,
            reply_to_message_id=456,
        )
        mock_api.send_document.assert_awaited_once_with(expected_request)
        assert response == mock_document_response


@pytest.mark.asyncio
async def test_telegram_get_webhook_info(mock_webhook_info):
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.get_webhook_info.return_value = WebhookInfo(**mock_webhook_info)
        mock_get_api.return_value = mock_api

        response = await telegram_get_webhook_info.fn()
        mock_api.get_webhook_info.assert_awaited_once()
        assert response.url == mock_webhook_info["url"]
        assert (
            response.has_custom_certificate
            == mock_webhook_info["has_custom_certificate"]
        )
        assert (
            response.pending_update_count == mock_webhook_info["pending_update_count"]
        )


@pytest.mark.asyncio
async def test_telegram_set_webhook():
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.set_webhook.return_value = True
        mock_get_api.return_value = mock_api

        response = await telegram_set_webhook.fn(
            url="https://test.com/webhook",
            certificate="cert.pem",
            ip_address="1.2.3.4",
            max_connections=100,
            allowed_updates=["message"],
            drop_pending_updates=True,
            secret_token="secret",
        )

        mock_api.set_webhook.assert_awaited_once_with(
            url="https://test.com/webhook",
            certificate="cert.pem",
            ip_address="1.2.3.4",
            max_connections=100,
            allowed_updates=["message"],
            drop_pending_updates=True,
            secret_token="secret",
        )
        assert response is True


@pytest.mark.asyncio
async def test_telegram_delete_webhook():
    with patch("pyramidpy_tools.telegram.tools.get_telegram_api") as mock_get_api:
        mock_api = AsyncMock()
        mock_api.delete_webhook.return_value = True
        mock_get_api.return_value = mock_api

        response = await telegram_delete_webhook.fn(drop_pending_updates=True)
        mock_api.delete_webhook.assert_awaited_once_with(drop_pending_updates=True)
        assert response is True
