from typing import List, Optional

from pydantic import BaseModel


class TweetMedia(BaseModel):
    """Media information from a tweet"""

    type: str
    url: str
    media_url: str
    display_url: str


class ParsedTweet(BaseModel):
    """Simplified tweet information"""

    text: str
    media: List[TweetMedia] = []
    created_at: str
    id: str


def extract_media(entities: dict) -> List[TweetMedia]:
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


def parse_tweet(tweet_data: dict) -> Optional[ParsedTweet]:
    """Parse a tweet object to extract relevant information"""
    try:
        # Navigate to the legacy data which contains the main tweet information
        if "legacy" not in tweet_data:
            return None

        legacy = tweet_data["legacy"]

        return ParsedTweet(
            text=legacy.get("full_text", ""),
            media=extract_media(legacy.get("entities", {})),
            created_at=legacy.get("created_at", ""),
            id=legacy.get("id_str", ""),
        )
    except Exception:
        return None


def parse_timeline(timeline_data: dict) -> List[ParsedTweet]:
    """Parse Twitter timeline data to extract text and media URLs.
    Args:
        timeline_data: Raw timeline data from Twitter API
    Returns:
        List of parsed tweets containing text and media URLs
    """
    parsed_tweets = []

    # Handle entries in timeline
    entries = timeline_data.get("entries", [])
    for entry in entries:
        content = entry.get("content", {})
        if "itemContent" not in content:
            continue

        item_content = content["itemContent"]
        if "tweet_results" not in item_content:
            continue

        tweet_data = item_content["tweet_results"].get("result", {})
        parsed_tweet = parse_tweet(tweet_data)
        if parsed_tweet:
            parsed_tweets.append(parsed_tweet)

    return parsed_tweets
