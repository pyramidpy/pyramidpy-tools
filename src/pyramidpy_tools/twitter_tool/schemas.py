from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TwitterUserAuth(BaseModel):
    """Authentication settings for Twitter user API"""

    cto: str | None = None
    auth_token: str | None = None
    twid: str | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None


class TwitterWebAuth(BaseModel):
    cto: str | None = None
    auth_token: str | None = None
    twid: str | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None


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
