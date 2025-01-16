from typing import Any, Dict, List, Optional
from datetime import timezone

from twitter.account import Account
from twitter.scraper import Scraper

from pyramidpy_tools.settings import settings

from .schemas import (
    QuoteRequest,
    ReplyRequest,
    ScheduleTweetRequest,
    TimelineRequest,
    TweetActionRequest,
    TweetRequest,
    TwitterUserAuth,
    TweepyAuth,
)


class TwitterUserAPI:
    """Client for interacting with Twitter using user authentication"""

    def __init__(self, auth: Optional[TwitterUserAuth] = None):
        self.auth = auth or TwitterUserAuth(
            cto=settings.tool_provider.twitter_cto,
            auth_token=settings.tool_provider.twitter_auth_token,
            twid=settings.tool_provider.twitter_twid,
            username=settings.tool_provider.twitter_username,
            password=settings.tool_provider.twitter_password,
            email=settings.tool_provider.twitter_email,
        )
        self.account = self._get_account()
        self.scraper = self._get_scraper()

    def _get_account(self) -> Account:
        """Get authenticated Twitter account instance"""
        if self.auth.cto and self.auth.auth_token and self.auth.twid:
            cookies_dict = {
                "ct0": self.auth.cto,
                "auth_token": self.auth.auth_token,
                "twid": self.auth.twid,
            }
            return Account(cookies=cookies_dict)

        if self.auth.username and self.auth.password:
            return Account(username=self.auth.username, password=self.auth.password)

        raise ValueError("Invalid Twitter credentials")

    def _get_scraper(self) -> Scraper:
        """Get authenticated Twitter scraper instance"""
        if self.auth.cto and self.auth.auth_token and self.auth.twid:
            cookies_dict = {
                "ct0": self.auth.cto,
                "auth_token": self.auth.auth_token,
                "twid": self.auth.twid,
            }
            return Scraper(cookies=cookies_dict)

        if self.auth.username and self.auth.password:
            return Scraper(username=self.auth.username, password=self.auth.password)

        raise ValueError("Invalid Twitter credentials")

    def get_latest_timeline(self, request: TimelineRequest) -> List[Dict[str, Any]]:
        """Get the latest timeline of the authenticated account"""
        return self.account.home_latest_timeline(limit=request.limit)

    def send_tweet(self, request: TweetRequest) -> Dict[str, Any]:
        """Post a new tweet"""
        return self.account.tweet(request.content)

    def reply_to_tweet(self, request: ReplyRequest) -> Dict[str, Any]:
        """Reply to an existing tweet"""
        return self.account.reply(request.text, request.tweet_id)

    def quote_tweet(self, request: QuoteRequest) -> Dict[str, Any]:
        """Quote an existing tweet"""
        return self.account.quote(request.text, request.tweet_id)

    def retweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Retweet an existing tweet"""
        return self.account.retweet(request.tweet_id)

    def unretweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Remove a retweet"""
        return self.account.unretweet(request.tweet_id)

    def schedule_tweet(self, request: ScheduleTweetRequest) -> Dict[str, Any]:
        """Schedule a tweet for later posting"""
        return self.account.schedule_tweet(request.text, request.scheduled_time)

    def unschedule_tweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Cancel a scheduled tweet"""
        return self.account.unschedule_tweet(request.tweet_id)


class TweepyTwitterApi:
    """Client for interacting with Twitter using Tweepy API v2"""

    def __init__(self, auth: Optional[TweepyAuth] = None):
        import tweepy
        
        if not auth:
            auth = TweepyAuth(
                bearer_token=settings.tool_provider.twitter_bearer_token,
                consumer_key=settings.tool_provider.twitter_consumer_key,
                consumer_secret=settings.tool_provider.twitter_consumer_secret,
                access_token=settings.tool_provider.twitter_access_token,
                access_token_secret=settings.tool_provider.twitter_access_token_secret,
            )
        
        self.client = tweepy.Client(
            bearer_token=auth.bearer_token,
            consumer_key=auth.consumer_key,
            consumer_secret=auth.consumer_secret,
            access_token=auth.access_token,
            access_token_secret=auth.access_token_secret,
            wait_on_rate_limit=True
        )

    def get_latest_timeline(self, request: TimelineRequest) -> List[Dict[str, Any]]:
        """Get the latest timeline of the authenticated account"""
        response = self.client.get_home_timeline(
            max_results=request.limit,
            user_auth=True
        )
        return [tweet.data for tweet in response.data] if response.data else []

    def send_tweet(self, request: TweetRequest) -> Dict[str, Any]:
        """Post a new tweet"""
        response = self.client.create_tweet(
            text=request.content
        )
        return response.data

    def reply_to_tweet(self, request: ReplyRequest) -> Dict[str, Any]:
        """Reply to an existing tweet"""
        response = self.client.create_tweet(
            text=request.text,
            in_reply_to_tweet_id=request.tweet_id
        )
        return response.data

    def quote_tweet(self, request: QuoteRequest) -> Dict[str, Any]:
        """Quote an existing tweet"""
        response = self.client.create_tweet(
            text=request.text,
            quote_tweet_id=request.tweet_id
        )
        return response.data

    def retweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Retweet an existing tweet"""
        response = self.client.retweet(
            tweet_id=request.tweet_id
        )
        return response.data

    def unretweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Remove a retweet"""
        response = self.client.unretweet(
            source_tweet_id=request.tweet_id
        )
        return response.data

    def schedule_tweet(self, request: ScheduleTweetRequest) -> Dict[str, Any]:
        """Schedule a tweet for later posting"""
        # Convert datetime to UTC if needed
        scheduled_time = request.scheduled_time.astimezone(timezone.utc)
        
        response = self.client.create_tweet(
            text=request.text,
            scheduled_time=scheduled_time
        )
        return response.data

    def unschedule_tweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Cancel a scheduled tweet"""
        response = self.client.delete_tweet(
            id=request.tweet_id
        )
        return response.data