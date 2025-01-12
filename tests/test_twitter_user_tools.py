from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from pyramidpy_tools.twitter_user.schemas import TwitterUserAuth
from pyramidpy_tools.twitter_user.tools import (
    get_twitter_api,
    twitter_get_latest_timeline,
    twitter_quote,
    twitter_reply,
    twitter_retweet,
    twitter_schedule_tweet,
    twitter_tweet,
    twitter_unretweet,
    twitter_unschedule_tweet,
)


@pytest.fixture
def mock_tweet_response():
    return {"id": 123456789, "text": "Test tweet", "created_at": "2024-01-04T12:00:00Z"}


def test_get_twitter_api_with_auth():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_flow = MagicMock()
        mock_flow.context = {
            "twitter_auth": {
                "api_key": "test-key",
                "api_secret": "test-secret",
                "access_token": "test-token",
                "access_token_secret": "test-token-secret",
            }
        }
        mock_get_flow.return_value = mock_flow

        api = get_twitter_api()
        assert isinstance(api.auth, TwitterUserAuth)
        assert api.auth.api_key == "test-key"
        assert api.auth.api_secret == "test-secret"


def test_get_twitter_api_without_auth():
    with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
        mock_get_flow.return_value = None

        api = get_twitter_api()
        assert api.auth is None


@pytest.mark.asyncio
async def test_twitter_get_latest_timeline():
    with patch(
        "pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.get_latest_timeline"
    ) as mock_timeline:
        mock_timeline.return_value = [
            {"id": 123456789, "text": "Tweet 1", "created_at": "2024-01-04T12:00:00Z"},
            {"id": 123456790, "text": "Tweet 2", "created_at": "2024-01-04T12:01:00Z"},
        ]

        result = await twitter_get_latest_timeline(limit=2)

        assert len(result) == 2
        assert result[0]["text"] == "Tweet 1"
        assert result[1]["text"] == "Tweet 2"
        mock_timeline.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_tweet(mock_tweet_response):
    with patch("pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.send_tweet") as mock_tweet:
        mock_tweet.return_value = mock_tweet_response

        result = await twitter_tweet(content="Test tweet")

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        mock_tweet.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_reply(mock_tweet_response):
    with patch(
        "pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.reply_to_tweet"
    ) as mock_reply:
        mock_reply.return_value = mock_tweet_response

        result = await twitter_reply(text="Test reply", tweet_id=123456789)

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        mock_reply.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_quote(mock_tweet_response):
    with patch("pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.quote_tweet") as mock_quote:
        mock_quote.return_value = mock_tweet_response

        result = await twitter_quote(text="Test quote", tweet_id=123456789)

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        mock_quote.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_retweet(mock_tweet_response):
    with patch("pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.retweet") as mock_retweet:
        mock_retweet.return_value = mock_tweet_response

        result = await twitter_retweet(tweet_id=123456789)

        assert result["id"] == 123456789
        mock_retweet.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_unretweet(mock_tweet_response):
    with patch(
        "pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.unretweet"
    ) as mock_unretweet:
        mock_unretweet.return_value = mock_tweet_response

        result = await twitter_unretweet(tweet_id=123456789)

        assert result["id"] == 123456789
        mock_unretweet.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_schedule_tweet(mock_tweet_response):
    with patch(
        "pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.schedule_tweet"
    ) as mock_schedule:
        mock_schedule.return_value = mock_tweet_response
        scheduled_time = datetime(2024, 1, 5, 12, 0, tzinfo=timezone.utc)

        result = await twitter_schedule_tweet(
            text="Scheduled tweet", scheduled_time=scheduled_time
        )

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        mock_schedule.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_unschedule_tweet(mock_tweet_response):
    with patch(
        "pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.unschedule_tweet"
    ) as mock_unschedule:
        mock_unschedule.return_value = mock_tweet_response

        result = await twitter_unschedule_tweet(tweet_id=123456789)

        assert result["id"] == 123456789
        mock_unschedule.assert_called_once()


@pytest.mark.asyncio
async def test_twitter_api_error():
    with patch("pyramidpy_tools.tools.twitter_user.base.TwitterUserAPI.send_tweet") as mock_tweet:
        mock_tweet.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            await twitter_tweet("Test tweet")

        assert str(exc_info.value) == "API Error"
