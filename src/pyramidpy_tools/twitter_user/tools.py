from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool
from pydantic import BaseModel

from pyramidpy_tools.toolkit import Toolkit

from .base import TwitterUserAPI, TweepyTwitterApi
from .schemas import (
    QuoteRequest,
    ReplyRequest,
    ScheduleTweetRequest,
    TimelineRequest,
    TweetActionRequest,
    TweetRequest,
    TwitterUserAuth,
    TweepyAuth,
    TwitterAuthConfig,
)


AUTH_PREFIX = "twitter_auth"

def get_twitter_api() -> Union[TwitterUserAPI, TweepyTwitterApi]:
    """Get Twitter API instance with auth from context if available"""
    flow = get_flow()
    if flow and flow.context:
        auth_dict = flow.context.get("auth", {}).get(AUTH_PREFIX)
        if auth_dict:
            # Try to parse as TweepyAuth first
            use_tweepy = auth_dict.get("use_tweepy", False)
            try:
                auth = TweepyAuth(**auth_dict)
                return TweepyTwitterApi(auth=auth)
            except (ValueError, TypeError):
                # If TweepyAuth fails, try TwitterUserAuth
                try:
                    auth = TwitterUserAuth(**auth_dict)
                    return TwitterUserAPI(auth=auth)
                except (ValueError, TypeError):
                    raise ValueError("Invalid Twitter authentication configuration")
    
    # Default to TwitterUserAPI with settings-based auth
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
    auth_key=AUTH_PREFIX,
    auth_config_schema=TwitterAuthConfig,
    requires_config=True,
    name="Twitter User Toolkit",
    description="Toolkit for interacting with twitter using either OAuth or user authentication.",
)
