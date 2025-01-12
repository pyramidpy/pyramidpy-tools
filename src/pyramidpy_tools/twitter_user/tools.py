from datetime import datetime
from typing import Any, Dict, List

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit
from app.settings import settings

from .base import TwitterUserAPI
from .schemas import (
    QuoteRequest,
    ReplyRequest,
    ScheduleTweetRequest,
    TimelineRequest,
    TweetActionRequest,
    TweetRequest,
    TwitterUserAuth,
)


def get_twitter_api() -> TwitterUserAPI:
    """Get Twitter API instance with auth from context if available"""
    flow = get_flow()
    if flow and flow.context:
        auth_dict = flow.context.get("twitter_auth")
        if auth_dict:
            auth = TwitterUserAuth(**auth_dict)
            return TwitterUserAPI(auth=auth)
    return TwitterUserAPI()


@tool(
    name="twitter_get_latest_timeline",
    description="Get the latest timeline of a twitter account",
    include_return_description=False,
)
async def twitter_get_latest_timeline(limit: int = 5) -> List[Dict[str, Any]]:
    twitter = get_twitter_api()
    request = TimelineRequest(limit=limit)
    return twitter.get_latest_timeline(request)


@tool(
    name="twitter_tweet",
    description="Post a new tweet",
    include_return_description=False,
)
async def twitter_tweet(content: str) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = TweetRequest(content=content)
    return twitter.send_tweet(request)


@tool(
    name="twitter_reply",
    description="Reply to an existing tweet",
    include_return_description=False,
)
async def twitter_reply(text: str, tweet_id: int) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = ReplyRequest(text=text, tweet_id=tweet_id)
    return twitter.reply_to_tweet(request)


@tool(
    name="twitter_quote",
    description="Quote an existing tweet",
    include_return_description=False,
)
async def twitter_quote(text: str, tweet_id: int) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = QuoteRequest(text=text, tweet_id=tweet_id)
    return twitter.quote_tweet(request)


@tool(
    name="twitter_retweet",
    description="Retweet an existing tweet",
    include_return_description=False,
)
async def twitter_retweet(tweet_id: int) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = TweetActionRequest(tweet_id=tweet_id)
    return twitter.retweet(request)


@tool(
    name="twitter_unretweet",
    description="Remove a retweet",
    include_return_description=False,
)
async def twitter_unretweet(tweet_id: int) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = TweetActionRequest(tweet_id=tweet_id)
    return twitter.unretweet(request)


@tool(
    name="twitter_schedule_tweet",
    description="Schedule a tweet for later posting",
    include_return_description=False,
)
async def twitter_schedule_tweet(text: str, scheduled_time: datetime) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = ScheduleTweetRequest(text=text, scheduled_time=scheduled_time)
    return twitter.schedule_tweet(request)


@tool(
    name="twitter_unschedule_tweet",
    description="Cancel a scheduled tweet",
    include_return_description=False,
)
async def twitter_unschedule_tweet(tweet_id: int) -> Dict[str, Any]:
    twitter = get_twitter_api()
    request = TweetActionRequest(tweet_id=tweet_id)
    return twitter.unschedule_tweet(request)


twitter_toolkit = Toolkit.create_toolkit(
    id="twitter_user_toolkit",
    tools=[
        twitter_get_latest_timeline,
        twitter_tweet,
        twitter_reply,
        twitter_quote,
        twitter_retweet,
        twitter_unretweet,
        twitter_schedule_tweet,
        twitter_unschedule_tweet,
    ],
    auth_key="twitter_auth",
    auth_config_schema=TwitterUserAuth,
    requires_config=True,
    name="Twitter User Toolkit",
    description="Toolkit for interacting with twitter using user password authentication.",
)
