from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TweepyAuth(BaseModel):
    """Authentication settings for Tweepy API v2"""

    bearer_token: Optional[str] = Field(None, description="Twitter API OAuth 2.0 Bearer Token")
    consumer_key: Optional[str] = Field(None, description="Twitter API OAuth 1.0a Consumer Key")
    consumer_secret: Optional[str] = Field(None, description="Twitter API OAuth 1.0a Consumer Secret")
    access_token: Optional[str] = Field(None, description="Twitter API OAuth 1.0a Access Token")
    access_token_secret: Optional[str] = Field(None, description="Twitter API OAuth 1.0a Access Token Secret")

    class Config:
        """Pydantic model configuration"""
        frozen = True  # Make the model immutable


class TwitterUserAuth(BaseModel):
    """Authentication settings for Twitter user API"""

    cto: str = Field("", description="The consumer token, prefered over username/password/email")
    auth_token: str = Field("", description="The authentication token, prefered over username/password/email")
    twid: str = Field("", description="The Twitter ID, prefered over username/password/email")
    username: str = Field("", description="The username, not as reliable as (cto,token,twid)")
    password: str = Field("", description="The password, not as reliable as (cto,token,twid)")
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


class TwitterAuthConfig(BaseModel):
    """Combined authentication configuration for Twitter"""
    tweepy: Optional[TweepyAuth] = Field(None, description="Tweepy authentication settings")
    user: Optional[TwitterUserAuth] = Field(None, description="Twitter user authentication settings. To be marked as deprecated for compliance with X Policies.")
    use_tweepy: bool = Field(True, description="Whether to use Tweepy API v2 (recommended). We recommend using Tweepy API v2 for compliance with X Policies.")
    # pyramid ui definition beta, subject to change
    _ui_display: dict = {
        "block_switch": {
            "type": "block_switch",
            "description": "Tweepy authentication settings",
            "default": None,
            "fields": {
                "tweepy": {
                    "type": "block",
                    "description": "Tweepy authentication settings",
                    "default": None,
                    "visible": "use_tweepy",
                },
                "user": {
                    "type": "block",
                    "description": "Twitter user authentication settings",
                    "default": None,
                    "visible": "not use_tweepy",
                },
            }
        },
       
    }

    @model_validator(mode="after")
    def validate_auth(self):
        if self.use_tweepy and not self.tweepy:
            raise ValueError("TweepyAuth is required when use_tweepy is True")
        elif not self.use_tweepy and not self.user:
            raise ValueError("TwitterUserAuth is required when use_tweepy is False")
        return self
