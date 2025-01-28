from unittest.mock import AsyncMock, patch

import pytest

from pyramidpy_tools.ayrshare.base import AyrshareAPI
from pyramidpy_tools.ayrshare.schemas import (
    AyrshareAuth,
    PostResponse,
)
from pyramidpy_tools.ayrshare.tools import AyrshareTools


@pytest.fixture
def mock_client():
    with patch("pyramidpy_tools.ayrshare.base.SocialPost") as mock:
        yield mock


@pytest.fixture
def api(mock_client):
    auth = AyrshareAuth(api_key="test_key")
    return AyrshareAPI(auth)


@pytest.fixture
def tools(api):
    return AyrshareTools(api)


@pytest.mark.asyncio
async def test_create_post(tools, mock_client):
    # Mock post response
    mock_post = {
        "id": "123",
        "status": "success",
        "posts": [{"platform": "twitter", "id": "tw123"}],
    }
    tools.api.post = AsyncMock(return_value=PostResponse(**mock_post))

    result = await tools.create_social_post(
        text="Test post", platforms=["twitter"], profile_key="test-profile"
    )

    assert result.id == "123"
    assert result.status == "success"
    assert len(result.posts) == 1
    assert result.posts[0]["platform"] == "twitter"


@pytest.mark.asyncio
async def test_delete_posts(tools, mock_client):
    mock_response = {"success": True, "message": "Post deleted"}
    tools.api.delete_post = AsyncMock(return_value=mock_response)

    result = await tools.delete_posts(post_ids=["123", "456"], platforms=["twitter"])

    assert len(result) == 2
    assert all(r["success"] for r in result)
    assert tools.api.delete_post.call_count == 2


@pytest.mark.asyncio
async def test_get_post_history(tools, mock_client):
    mock_history = [
        {"id": "123", "platform": "twitter", "status": "posted"},
        {"id": "456", "platform": "facebook", "status": "posted"},
    ]
    tools.api.history = AsyncMock(return_value=mock_history)

    result = await tools.get_post_history(last=2, platform="twitter")

    assert len(result) == 2
    assert result[0]["id"] == "123"
    assert result[1]["id"] == "456"


@pytest.mark.asyncio
async def test_upload_media_files(tools, mock_client):
    mock_response = {"id": "media123", "url": "https://example.com/media"}
    tools.api.upload_media = AsyncMock(return_value=mock_response)

    result = await tools.upload_media_files(
        file_urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
    )

    assert len(result) == 2
    assert all(r["id"] == "media123" for r in result)
    assert tools.api.upload_media.call_count == 2


@pytest.mark.asyncio
async def test_get_post_analytics(tools, mock_client):
    mock_analytics = {"id": "123", "analytics": {"likes": 10, "shares": 5}}
    tools.api.post_analytics = AsyncMock(return_value=mock_analytics)

    result = await tools.get_post_analytics(post_ids=["123", "456"])

    assert len(result) == 2
    assert all("analytics" in r for r in result)
    assert tools.api.post_analytics.call_count == 2


@pytest.mark.asyncio
async def test_auto_schedule_posts(tools, mock_client):
    mock_response = {"status": "success", "message": "Auto schedule created"}
    tools.api.set_auto_schedule = AsyncMock(return_value=mock_response)

    result = await tools.auto_schedule_posts(
        posts=[{"post": "Test post", "platforms": ["twitter"]}],
        schedule_days=["Monday", "Wednesday"],
        schedule_times=["09:00", "15:00"],
    )

    assert result["status"] == "success"
    tools.api.set_auto_schedule.assert_called_once()


@pytest.mark.asyncio
async def test_generate_hashtags(tools, mock_client):
    mock_response = {"hashtags": ["#test", "#example"], "status": "success"}
    tools.api.auto_hashtags = AsyncMock(return_value=mock_response)

    result = await tools.generate_hashtags(
        text="Test post", platforms=["twitter"], num_hashtags=2
    )

    assert result["status"] == "success"
    assert len(result["hashtags"]) == 2
    tools.api.auto_hashtags.assert_called_once()
