from typing import List
from .schemas import Tweet


def parse_timeline_to_tweets(timeline_data: List[dict]) -> List[Tweet]:
    """Parse Twitter timeline data to extract Tweet objects.
    Args:
        timeline_data: Raw timeline data from Twitter API
    Returns:
        List of Tweet objects containing tweet information
    """
    tweets = []

    for timeline_item in timeline_data:
        # Get the entries directly from the first instruction
        entries = (
            timeline_item.get("data", {})
            .get("home", {})
            .get("home_timeline_urt", {})
            .get("instructions", [])[0]
            .get("entries", [])
        )
        for entry in entries:
            if "content" not in entry:
                continue

            content = entry["content"]
            if content.get("entryType") != "TimelineTimelineItem":
                continue

            item_content = content.get("itemContent", {})
            if item_content.get("itemType") != "TimelineTweet":
                continue

            tweet = Tweet.parse_tweet(entry)
            if tweet:
                tweets.append(tweet)

    return tweets
