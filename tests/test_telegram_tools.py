import pytest
from controlflow.flows.flow import Flow, get_flow

from pyramidpy_tools.settings import settings
from pyramidpy_tools.telegram.base import TelegramAPI
from pyramidpy_tools.telegram.schemas import (
    SendDocumentRequest,
    SendMessageRequest,
    SendPhotoRequest,
)

# Test constants
TEST_CHAT_ID = settings.tool_provider.telegram_test_chat_id
TEST_IMAGE_URL = "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png"
TEST_DOCUMENT_URL = (
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
)


def auth_callback(key, context):
    if key == "telegram_bot_token":
        return {"telegram_bot_token": settings.tool_provider.telegram_bot_token}
    return None


@pytest.fixture
def api_key():
    """Get API key from environment variable."""
    flow = get_flow() or Flow()
    flow.context["auth"] = auth_callback
    return flow


@pytest.fixture
def api() -> TelegramAPI:
    """Create an authenticated API client."""
    if not settings.tool_provider.telegram_bot_token:
        pytest.skip("TELEGRAM_BOT_TOKEN not set")
    if not settings.tool_provider.telegram_test_chat_id:
        pytest.skip("TELEGRAM_TEST_CHAT_ID not set")

    return TelegramAPI(token=settings.tool_provider.telegram_bot_token)


@pytest.mark.asyncio
async def test_send_message(api: TelegramAPI):
    """Test sending a message."""
    request = SendMessageRequest(
        chat_id=TEST_CHAT_ID,
        text="Test message from API test suite",
        parse_mode="HTML",
        disable_web_page_preview=True,
        disable_notification=True,
    )

    response = await api.send_message(request)
    assert response is not None
    assert response["ok"] is True
    assert "result" in response

    result = response["result"]
    assert result["text"] == request.text
    assert result["chat"]["id"] == int(TEST_CHAT_ID)


@pytest.mark.asyncio
async def test_send_photo(api: TelegramAPI):
    """Test sending a photo."""
    request = SendPhotoRequest(
        chat_id=TEST_CHAT_ID,
        photo=TEST_IMAGE_URL,
        caption="Test photo from API test suite",
        parse_mode="HTML",
        disable_notification=True,
    )

    response = await api.send_photo(request)
    assert response is not None
    assert response["ok"] is True
    assert "result" in response

    result = response["result"]
    assert result["caption"] == request.caption
    assert result["chat"]["id"] == int(TEST_CHAT_ID)
    assert "photo" in result
    assert len(result["photo"]) > 0


@pytest.mark.asyncio
async def test_send_document(api: TelegramAPI):
    """Test sending a document."""
    request = SendDocumentRequest(
        chat_id=TEST_CHAT_ID,
        document=TEST_DOCUMENT_URL,
        caption="Test document from API test suite",
        parse_mode="HTML",
        disable_notification=True,
    )

    response = await api.send_document(request)
    assert response is not None
    assert response["ok"] is True
    assert "result" in response

    result = response["result"]
    assert result["caption"] == request.caption
    assert result["chat"]["id"] == int(TEST_CHAT_ID)
    assert "document" in result
    assert result["document"]["file_id"] is not None


@pytest.mark.asyncio
async def test_get_webhook_info(api: TelegramAPI):
    """Test getting webhook information."""
    response = await api.get_webhook_info()
    assert response is not None
    assert "url" in response
    assert "has_custom_certificate" in response
    assert "pending_update_count" in response


@pytest.mark.asyncio
async def test_webhook_lifecycle(api: TelegramAPI):
    """Test setting and deleting a webhook."""
    # First delete any existing webhook
    delete_response = await api.delete_webhook(drop_pending_updates=True)
    assert delete_response is True

    # Set a new webhook
    webhook_url = "https://example.com/webhook"
    set_response = await api.set_webhook(
        url=webhook_url,
        max_connections=100,
        allowed_updates=["message", "edited_channel_post"],
        drop_pending_updates=True,
    )
    assert set_response is True

    # Verify webhook was set
    info = await api.get_webhook_info()
    assert info["url"] == webhook_url

    # Clean up by deleting webhook
    cleanup_response = await api.delete_webhook()
    assert cleanup_response is True

    # Verify webhook was deleted
    final_info = await api.get_webhook_info()
    assert final_info["url"] == ""
