from datetime import datetime
from typing import Any, Dict, List, Optional

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
