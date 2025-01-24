from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TweepyAuth(BaseModel):
    """Authentication settings for Tweepy API v2"""

    bearer_token: Optional[str] = Field(
        None, description="Twitter API OAuth 2.0 Bearer Token"
    )
    consumer_key: Optional[str] = Field(
        None, description="Twitter API OAuth 1.0a Consumer Key"
    )
    consumer_secret: Optional[str] = Field(
        None, description="Twitter API OAuth 1.0a Consumer Secret"
    )
    access_token: Optional[str] = Field(
        None, description="Twitter API OAuth 1.0a Access Token"
    )
    access_token_secret: Optional[str] = Field(
        None, description="Twitter API OAuth 1.0a Access Token Secret"
    )

    class Config:
        """Pydantic model configuration"""

        frozen = True  # Make the model immutable


class TwitterUserAuth(BaseModel):
    """Authentication settings for Twitter user API"""

    cto: str = Field(
        "", description="The consumer token, prefered over username/password/email"
    )
    auth_token: str = Field(
        "",
        description="The authentication token, prefered over username/password/email",
    )
    twid: str = Field(
        "", description="The Twitter ID, prefered over username/password/email"
    )
    username: str = Field(
        "", description="The username, not as reliable as (cto,token,twid)"
    )
    password: str = Field(
        "", description="The password, not as reliable as (cto,token,twid)"
    )
    email: str = Field("", description="The email, not as reliable as (cto,token,twid)")




class TimelineRequest(BaseModel):
    """Request parameters for getting timeline"""

    limit: int = 20


class TweetRequest(BaseModel):
    """Request parameters for posting a tweet"""

    content: str


class ReplyRequest(BaseModel):
    """Request parameters for replying to a tweet"""

    text: str
    tweet_id: int


class QuoteRequest(BaseModel):
    """Request parameters for quoting a tweet"""

    text: str
    tweet_id: int


class TweetActionRequest(BaseModel):
    """Request parameters for tweet actions (retweet, unretweet, etc)"""

    tweet_id: int


class ScheduleTweetRequest(BaseModel):
    """Request parameters for scheduling a tweet"""

    text: str
    scheduled_time: datetime


class Tweet(BaseModel):
    """Tweet data model responses"""

    url: str
    twitter_url: str
    id: str
    text: str
    retweet_count: int = 0
    reply_count: int = 0
    like_count: int = 0
    quote_count: int = 0
    created_at: str
    bookmark_count: int = 0
    is_retweet: bool = False
    is_quote: bool = False
    possibly_sensitive: bool = False
    followers_count: Optional[int] = None
    author_id: str
    conversation_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None

    @classmethod
    def parse_tweet(cls, entry: dict) -> Optional["Tweet"]:
        """Parse tweet data from Twitter API entry format"""
        try:
            content = entry.get("content", {})
            item_content = content.get("itemContent", {})

            if item_content.get("itemType") != "TimelineTweet":
                return None

            tweet_data = item_content.get("tweet_results", {}).get("result", {})
            legacy = tweet_data.get("legacy", {})
            user_data = (
                tweet_data.get("core", {})
                .get("user_results", {})
                .get("result", {})
                .get("legacy", {})
            )

            if not legacy:
                return None

            tweet_id = legacy.get("id_str", "")
            screen_name = user_data.get("screen_name", "user")

            return cls(
                url=f"https://x.com/{screen_name}/status/{tweet_id}",
                twitter_url=f"https://twitter.com/{screen_name}/status/{tweet_id}",
                id=tweet_id,
                text=legacy.get("full_text", ""),
                retweet_count=legacy.get("retweet_count", 0),
                reply_count=legacy.get("reply_count", 0),
                like_count=legacy.get("favorite_count", 0),
                quote_count=legacy.get("quote_count", 0),
                created_at=legacy.get("created_at", ""),
                bookmark_count=legacy.get("bookmark_count", 0),
                is_retweet=legacy.get("retweeted", False),
                is_quote=bool(legacy.get("is_quote_status", False)),
                possibly_sensitive=legacy.get("possibly_sensitive", False),
                followers_count=user_data.get("followers_count"),
            )
        except Exception:
            return None
