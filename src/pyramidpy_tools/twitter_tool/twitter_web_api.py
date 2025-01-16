# Use at your own risk.
# Twitter frowns upon scraping and web automation.
# Prefer creating api via twitter developer portal and using tweepy.

import datetime

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool
from twitter.account import Account
from twitter.scraper import Scraper

from pyramidpy_tools.toolkit import Toolkit
from pyramidpy_tools.settings import settings
from .schemas import TwitterWebAuth

default_auth = TwitterWebAuth(
    username=settings.tool_provider.twitter_username,
    password=settings.tool_provider.twitter_password,
)


def get_account(auth: TwitterWebAuth | None = None):
    """
    Get a twitter account
    Prefer cookies if available. Username and password are not stable.
    """
    if auth is None:
        auth = default_auth
    if auth.cto and auth.auth_token and auth.twid:
        cookies_dict = {
            "ct0": auth.cto,
            "auth_token": auth.auth_token,
            "twid": auth.twid,
        }
        return Account(cookies=cookies_dict)

    # try username and password
    if auth.username and auth.password:
        return Account(username=auth.username, password=auth.password)
    else:
        raise ValueError("Invalid Twitter credentials")


def get_scraper(auth: TwitterWebAuth | None = None):
    """
    Get a twitter scraper
    """
    if auth is None:
        auth = default_auth
    if auth.cto and auth.auth_token and auth.twid:
        cookies_dict = {
            "ct0": auth.cto,
            "auth_token": auth.auth_token,
            "twid": auth.twid,
        }
        return Scraper(cookies=cookies_dict)

    if auth.username and auth.password:
        return Scraper(username=auth.username, password=auth.password)
    else:
        raise ValueError("Invalid Twitter credentials")


def get_latest_timeline(account: Account, limit: int = 20):
    """
    Get the latest timeline of a twitter account
    """
    return account.home_latest_timeline(limit=limit)


def send_tweet(account: Account, content: str):
    """
    Tweet a text
    """
    return account.tweet(content)


def untweet(account: Account, tweet_id: int):
    """
    Untweet a tweet
    """
    return account.untweet(tweet_id)


def retweet(account: Account, tweet_id: int):
    """
    Retweet a tweet
    """
    return account.retweet(tweet_id)


def unretweet(account: Account, tweet_id: int):
    """
    Unretweet a tweet
    """
    return account.unretweet(tweet_id)


def reply(account: Account, text: str, tweet_id: int):
    """
    Reply to a tweet
    """
    return account.reply(text, tweet_id)


def quote(account: Account, text: str, tweet_id: int):
    """
    Quote a tweet
    """
    return account.quote(text, tweet_id)


def schedule_tweet(account: Account, text: str, datetime: datetime.datetime):
    """
    Schedule a tweet
    """
    return account.schedule_tweet(text, datetime)


def unschedule_tweet(account: Account, tweet_id: int):
    """
    Unschedule a tweet
    """
    return account.unschedule_tweet(tweet_id)


def get_auth():
    flow = get_flow()
    if flow:
        ctx = flow.context
        if ctx:
            return ctx.get("twitter_auth", default_auth)
    return default_auth


# tools
@tool(
    name="twitter_get_latest_timeline",
    description="Get the latest timeline of a twitter account",
    include_return_description=False,
)
def twitter_get_latest_timeline(limit: int = 5):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    latest_timeline = get_latest_timeline(account, limit=limit)
    print(latest_timeline)
    return latest_timeline


@tool(
    name="twitter_tweet",
    description="Tweet a text",
    include_return_description=False,
)
def twitter_tweet(content: str):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return send_tweet(account, content)


@tool(
    name="twitter_reply",
    description="Reply to a tweet",
    include_return_description=False,
)
def twitter_reply(text: str, tweet_id: int):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return reply(account, text, tweet_id)


@tool(
    name="twitter_quote",
    description="Quote a tweet",
    include_return_description=False,
)
def twitter_quote(text: str, tweet_id: int):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return quote(account, text, tweet_id)


@tool(
    name="twitter_retweet",
    description="Retweet a tweet",
    include_return_description=False,
)
def twitter_retweet(tweet_id: int):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return retweet(account, tweet_id)


@tool(
    name="twitter_unretweet",
    description="Unretweet a tweet",
    include_return_description=False,
)
def twitter_unretweet(tweet_id: int):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return unretweet(account, tweet_id)


@tool(
    name="twitter_schedule_tweet",
    description="Schedule a tweet",
    include_return_description=False,
)
def twitter_schedule_tweet(text: str, datetime: datetime.datetime):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return schedule_tweet(account, text, datetime)


@tool(
    name="twitter_unschedule_tweet",
    description="Unschedule a tweet",
    include_return_description=False,
)
def twitter_unschedule_tweet(tweet_id: int):
    twitter_auth = get_auth()
    account = get_account(twitter_auth)
    return unschedule_tweet(account, tweet_id)


twitter_toolkit = Toolkit.create_toolkit(
    id="twitter_toolkit",
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
    name="Twitter Toolkit",
    description="Tools for interacting with Twitter",
)
