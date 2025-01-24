from typing import Any, Dict, List, Optional
from datetime import timezone

from twitter.account import Account
from twitter.search import Search
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
            cto=settings.tool_provider.twitter_cto or "",
            auth_token=settings.tool_provider.twitter_auth_token or "",
            twid=settings.tool_provider.twitter_twid or "",
            username=settings.tool_provider.twitter_username or "",
            password=settings.tool_provider.twitter_password or "",
            email=settings.tool_provider.twitter_email or "",
        )
        self.account = self._get_account()
        self.scraper = self._get_scraper()
        self.search = self._get_search()

    def _get_account(self) -> Account:
        """Get authenticated Twitter account instance"""
        print(self.auth.model_dump())
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

    def _get_search(self) -> Search:
        """Get authenticated Twitter search instance"""
        return Search(
            email=self.auth.email,
            username=self.auth.username,
            password=self.auth.password,
            session=self.account.session,
        )

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

    def search_tweets(
        self, queries: List[Dict[str, Any]], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for tweets"""
        return self.search.run(limit=limit, queries=queries)


class TweepyTwitterApi:
    """Client for interacting with Twitter using Tweepy API v2"""

    def __init__(self, auth: Optional[TweepyAuth] = None):
        try:
            import tweepy
        except ImportError:
            raise ImportError(
                "Tweepy is not installed. Please install it to use the TweepyTwitterApi."
            )

        self.auth = auth or TweepyAuth(
            bearer_token=settings.tool_provider.twitter_bearer_token,
            consumer_key=settings.tool_provider.twitter_consumer_key,
            consumer_secret=settings.tool_provider.twitter_consumer_secret,
            access_token=settings.tool_provider.twitter_access_token,
            access_token_secret=settings.tool_provider.twitter_access_token_secret,
        )

        self.client = tweepy.Client(
            bearer_token=self.auth.bearer_token,
            consumer_key=self.auth.consumer_key,
            consumer_secret=self.auth.consumer_secret,
            access_token=self.auth.access_token,
            access_token_secret=self.auth.access_token_secret,
            wait_on_rate_limit=True,
        )

    def get_latest_timeline(self, request: TimelineRequest) -> List[Dict[str, Any]]:
        """Get the latest timeline of the authenticated account"""
        response = self.client.get_home_timeline(
            max_results=request.limit, user_auth=True
        )
        return [tweet.data for tweet in response.data] if response.data else []

    def send_tweet(self, request: TweetRequest) -> Dict[str, Any]:
        """Post a new tweet"""
        response = self.client.create_tweet(text=request.content)
        return response.data

    def reply_to_tweet(self, request: ReplyRequest) -> Dict[str, Any]:
        """Reply to an existing tweet"""
        response = self.client.create_tweet(
            text=request.text, in_reply_to_tweet_id=request.tweet_id
        )
        return response.data

    def quote_tweet(self, request: QuoteRequest) -> Dict[str, Any]:
        """Quote an existing tweet"""
        response = self.client.create_tweet(
            text=request.text, quote_tweet_id=request.tweet_id
        )
        return response.data

    def retweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Retweet an existing tweet"""
        response = self.client.retweet(tweet_id=request.tweet_id)
        return response.data

    def unretweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Remove a retweet"""
        response = self.client.unretweet(source_tweet_id=request.tweet_id)
        return response.data

    def schedule_tweet(self, request: ScheduleTweetRequest) -> Dict[str, Any]:
        """Schedule a tweet for later posting"""
        # Convert datetime to UTC if needed
        scheduled_time = request.scheduled_time.astimezone(timezone.utc)

        response = self.client.create_tweet(
            text=request.text, scheduled_time=scheduled_time
        )
        return response.data

    def unschedule_tweet(self, request: TweetActionRequest) -> Dict[str, Any]:
        """Cancel a scheduled tweet"""
        response = self.client.delete_tweet(id=request.tweet_id)
        return response.data
