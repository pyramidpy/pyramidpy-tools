from datetime import datetime
from typing import List, Optional
from loguru import logger
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
    # not required.
    # twid: str = Field(
    #     "", description="The Twitter ID, prefered over username/password/email"
    # )
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


class MediaRequest(BaseModel):
    """Request parameters for posting a tweet"""

    media: str = Field(
        ..., description="The media to post, can be a url or a file path"
    )
    alt: str = Field(
        "media", description="The alt text for the media, if the media is an image"
    )
    tagged_users: List[str] = Field(
        [], description="The users to tag in the media, if the media is an image"
    )


class TweetRequest(BaseModel):
    """Request parameters for posting a tweet"""

    content: str
    media: List[MediaRequest] = []


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


class TweetMedia(BaseModel):
    """Media information from a tweet"""

    type: str
    url: str
    media_url: str
    display_url: str

    @classmethod
    def extract_media(cls, entities: dict) -> Optional["TweetMedia"]:
        """Parse media information from Twitter API entry format"""

        """Extract media information from tweet entities"""
        media_list = []

        if "media" in entities:
            for media in entities["media"]:
                media_list.append(
                    TweetMedia(
                        type=media["type"],
                        url=media["url"],
                        media_url=media["media_url_https"],
                        display_url=media["display_url"],
                    )
                )

        return media_list


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
    created_at: str | None = None
    bookmark_count: int = 0
    is_retweet: bool = False
    is_quote: bool = False
    possibly_sensitive: bool = False
    followers_count: int | None = None
    author_id: str | None = None
    conversation_id: str | None = None
    in_reply_to_user_id: str | None = None
    media: List[TweetMedia] = []

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
                media=TweetMedia.extract_media(legacy.get("extended_entities", {})),
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
        except Exception as e:
            logger.error(f"Error parsing tweet: {e}")
            return None

    @classmethod
    def parse_apify_tweet(cls, entry: dict) -> Optional["Tweet"]:
        """Parse tweet data from Apify format"""
        try:
            if entry.get("type") != "tweet":
                return None

            return cls(
                url=entry.get("url", ""),
                twitter_url=entry.get("twitterUrl", ""),
                id=entry.get("id", ""),
                text=entry.get("text", ""),
                retweet_count=entry.get("retweetCount", 0),
                reply_count=entry.get("replyCount", 0),
                like_count=entry.get("likeCount", 0),
                quote_count=entry.get("quoteCount", 0),
                created_at=entry.get("createdAt", ""),
                bookmark_count=entry.get("bookmarkCount", 0),
                is_retweet=entry.get("isRetweet", False),
                is_quote=entry.get("isQuote", False),
                possibly_sensitive=entry.get("possiblySensitive", False),
                followers_count=entry.get("author", {}).get("followers"),
                author_id=entry.get("author", {}).get("id", ""),
                conversation_id=entry.get("conversationId"),
                in_reply_to_user_id=None,  # Not provided in Apify format
            )
        except Exception:
            return None
