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


class Tweet(BaseModel):
    """Tweet data model"""

    id: int
    text: str
    created_at: datetime
    author_id: str
    conversation_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    referenced_tweets: Optional[list] = None


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
