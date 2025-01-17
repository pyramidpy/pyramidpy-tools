from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from pyramidpy_tools.twitter_user.schemas import TwitterUserAuth, TweepyAuth
from pyramidpy_tools.twitter_user.base import TwitterUserAPI, TweepyTwitterApi, Account
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


@pytest.fixture
def mock_twitter_user_api():
    with patch("pyramidpy_tools.twitter_user.tools.TwitterUserAPI") as mock_api_class:
        mock_api = MagicMock(spec=TwitterUserAPI)
        mock_api_class.return_value = mock_api
        # Mock the auth property
        mock_api.auth = TwitterUserAuth(
            api_key="test-key",
            api_secret="test-secret",
            access_token="test-token",
            access_token_secret="test-token-secret",
        )
        # Mock the account property
        mock_api.account = MagicMock(spec=Account)
        yield mock_api


@pytest.fixture
def mock_tweepy_api():
    with patch("pyramidpy_tools.twitter_user.tools.TweepyTwitterApi") as mock_api_class:
        mock_api = MagicMock(spec=TweepyTwitterApi)
        mock_api_class.return_value = mock_api
        # Mock the auth property
        mock_api.auth = TweepyAuth(
            bearer_token="test-bearer",
            consumer_key="test-consumer-key",
            consumer_secret="test-consumer-secret",
            access_token="test-access-token",
            access_token_secret="test-access-secret",
        )
        yield mock_api


@pytest.fixture
def mock_account():
    return MagicMock(spec=Account)


def test_get_twitter_api_with_twitter_user_auth(mock_account):
    auth_data = {
        "cto": "test-key",
        "auth_token": "test-token",
        "twid": "test-twid",
        "username": "test-username",
        "password": "test-password",
        "email": "test@email.com",
    }

    with patch("pyramidpy_tools.twitter_user.tools.get_flow") as mock_get_flow:
        # Setup mock flow with proper context structure
        mock_flow = MagicMock()
        mock_flow.context = {"auth": {"twitter_auth": auth_data}}
        mock_get_flow.return_value = mock_flow

        api = get_twitter_api()

        assert isinstance(api, TwitterUserAPI)
        assert isinstance(api.auth, TwitterUserAuth)
        assert api.auth.cto == "test-key"
        assert api.auth.auth_token == "test-token"
        assert api.auth.twid == "test-twid"
        assert api.auth.username == "test-username"
        assert api.auth.password == "test-password"
        assert api.auth.email == "test@email.com"


def test_get_twitter_api_with_tweepy_auth():
    auth_data = {
        "bearer_token": "test-bearer",
        "consumer_key": "test-consumer-key",
        "consumer_secret": "test-consumer-secret",
        "access_token": "test-access-token",
        "access_token_secret": "test-access-secret",
    }

    with patch("pyramidpy_tools.twitter_user.tools.get_flow") as mock_get_flow:
        # Setup mock flow with proper context structure
        mock_flow = MagicMock()
        mock_flow.context = {"auth": {"twitter_auth": auth_data}}
        mock_get_flow.return_value = mock_flow

        api = get_twitter_api()

        assert isinstance(api, TweepyTwitterApi)
        assert isinstance(api.auth, TweepyAuth)
        assert api.auth.bearer_token == "test-bearer"
        assert api.auth.consumer_key == "test-consumer-key"
        assert api.auth.consumer_secret == "test-consumer-secret"
        assert api.auth.access_token == "test-access-token"
        assert api.auth.access_token_secret == "test-access-secret"


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_get_latest_timeline(request, api_fixture):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.get_latest_timeline.return_value = [
            {"id": 123456789, "text": "Tweet 1", "created_at": "2024-01-04T12:00:00Z"},
            {"id": 123456790, "text": "Tweet 2", "created_at": "2024-01-04T12:01:00Z"},
        ]

        result = await twitter_get_latest_timeline.fn(limit=2)

        assert len(result) == 2
        assert result[0]["text"] == "Tweet 1"
        assert result[1]["text"] == "Tweet 2"
        assert mock_api.get_latest_timeline.call_count == 1
        call_args = mock_api.get_latest_timeline.call_args[0][0]
        assert call_args.limit == 2


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_tweet(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.send_tweet.return_value = mock_tweet_response

        result = await twitter_tweet.fn(content="Test tweet")

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        assert mock_api.send_tweet.call_count == 1
        call_args = mock_api.send_tweet.call_args[0][0]
        assert call_args.content == "Test tweet"


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_reply(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.reply_to_tweet.return_value = mock_tweet_response

        result = await twitter_reply.fn(text="Test reply", tweet_id=123456789)

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        assert mock_api.reply_to_tweet.call_count == 1
        call_args = mock_api.reply_to_tweet.call_args[0][0]
        assert call_args.text == "Test reply"
        assert call_args.tweet_id == 123456789


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_quote(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.quote_tweet.return_value = mock_tweet_response

        result = await twitter_quote.fn(text="Test quote", tweet_id=123456789)

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        assert mock_api.quote_tweet.call_count == 1
        call_args = mock_api.quote_tweet.call_args[0][0]
        assert call_args.text == "Test quote"
        assert call_args.tweet_id == 123456789


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_retweet(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.retweet.return_value = mock_tweet_response

        result = await twitter_retweet.fn(tweet_id=123456789)

        assert result["id"] == 123456789
        assert mock_api.retweet.call_count == 1
        call_args = mock_api.retweet.call_args[0][0]
        assert call_args.tweet_id == 123456789


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_unretweet(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.unretweet.return_value = mock_tweet_response

        result = await twitter_unretweet.fn(tweet_id=123456789)

        assert result["id"] == 123456789
        assert mock_api.unretweet.call_count == 1
        call_args = mock_api.unretweet.call_args[0][0]
        assert call_args.tweet_id == 123456789


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_schedule_tweet(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.schedule_tweet.return_value = mock_tweet_response
        scheduled_time = datetime(2024, 1, 5, 12, 0, tzinfo=timezone.utc)

        result = await twitter_schedule_tweet.fn(
            text="Scheduled tweet", scheduled_time=scheduled_time
        )

        assert result["id"] == 123456789
        assert result["text"] == "Test tweet"
        assert mock_api.schedule_tweet.call_count == 1
        call_args = mock_api.schedule_tweet.call_args[0][0]
        assert call_args.text == "Scheduled tweet"
        assert call_args.scheduled_time == scheduled_time


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_unschedule_tweet(request, api_fixture, mock_tweet_response):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.unschedule_tweet.return_value = mock_tweet_response

        result = await twitter_unschedule_tweet.fn(tweet_id=123456789)

        assert result["id"] == 123456789
        assert mock_api.unschedule_tweet.call_count == 1
        call_args = mock_api.unschedule_tweet.call_args[0][0]
        assert call_args.tweet_id == 123456789


@pytest.mark.parametrize("api_fixture", ["mock_twitter_user_api", "mock_tweepy_api"])
async def test_twitter_api_error(request, api_fixture):
    mock_api = request.getfixturevalue(api_fixture)
    with patch(
        "pyramidpy_tools.twitter_user.tools.get_twitter_api", return_value=mock_api
    ):
        mock_api.send_tweet.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            await twitter_tweet.fn("Test tweet")

        assert str(exc_info.value) == "API Error"
