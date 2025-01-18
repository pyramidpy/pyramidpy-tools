import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .schemas import TimelineRequest, TweetRequest
from ..application.base import ApplicationStorage

logger = logging.getLogger(__name__)


def get_conversation_thread(
    tweet_id: int, api, max_depth: int = 10
) -> List[Dict[str, Any]]:
    """
    Build a conversation thread from a tweet by following reply chains up to max_depth.

    Args:
        tweet_id: The ID of the tweet to start building the thread from
        api: Twitter API instance
        max_depth: Maximum number of parent tweets to include in the thread

    Returns:
        List of tweets in chronological order (oldest first)
    """
    thread = []
    current_id = tweet_id
    depth = 0

    while current_id and depth < max_depth:
        timeline = api.get_latest_timeline(TimelineRequest(limit=1))
        if not timeline:
            break

        tweet = timeline[0]
        thread.insert(0, tweet)
        current_id = tweet.get("in_reply_to_status_id")
        depth += 1

    return thread


def handle_tweet_interaction(
    tweet_data: Dict[str, Any], api
) -> Optional[Dict[str, Any]]:
    """
    Process and handle a single tweet interaction, determining if and how to respond.

    Args:
        tweet_data: Dictionary containing tweet information including id, text, user etc.
        api: Twitter API instance

    Returns:
        Response tweet data if a response was sent, None otherwise
    """
    # Skip if tweet is from the bot itself
    if tweet_data.get("is_self", False):
        return None

    # Get conversation context
    thread = get_conversation_thread(tweet_data["id"], api)

    # Determine if we should respond based on tweet content
    should_respond = _should_respond_to_tweet(tweet_data, thread, api)
    if not should_respond:
        return None

    # Generate and send response
    response_text = _generate_response(tweet_data, thread, api)
    if response_text:
        response = api.send_tweet(
            TweetRequest(content=response_text, in_reply_to_status_id=tweet_data["id"])
        )
        return response

    return None


def _should_respond_to_tweet(
    tweet_data: Dict[str, Any], thread: List[Dict[str, Any]], api
) -> bool:
    """
    Determine if the bot should respond to a given tweet based on content and context.

    Args:
        tweet_data: Dictionary containing tweet information
        thread: List of tweets in the conversation thread
        api: Twitter API instance

    Returns:
        Boolean indicating whether to respond
    """
    # Always respond to mentions
    if "@" + api.username in tweet_data.get("text", ""):
        return True

    # Don't respond to retweets
    if tweet_data.get("is_retweet", False):
        return False

    # Add additional response criteria here
    return False


def _generate_response(
    tweet_data: Dict[str, Any], thread: List[Dict[str, Any]], api
) -> Optional[str]:
    """
    Generate an appropriate response text for a tweet based on its content and context.

    Args:
        tweet_data: Dictionary containing tweet information
        thread: List of tweets in the conversation thread
        api: Twitter API instance

    Returns:
        Response text if appropriate, None otherwise
    """
    try:
        # Prepare context from tweet and thread
        context = {
            "tweet": tweet_data.get("text", ""),
            "thread": [t.get("text", "") for t in thread],
            "user": tweet_data.get("user", {}).get("screen_name", ""),
        }

        # Use API's response generation
        return api.generate_response(context)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None


def process_twitter_interactions(api, check_interval: int = 120) -> None:
    """
    Main interaction loop that periodically checks for and processes new Twitter interactions.

    Args:
        api: Twitter API instance
        check_interval: Time in seconds between checks for new interactions
    """
    storage = ApplicationStorage()

    # Get latest mentions
    mentions = api.get_latest_timeline(TimelineRequest(limit=20))

    for tweet in mentions:
        # Skip if already processed
        if _is_tweet_processed(tweet["id"], storage):
            continue

        response = handle_tweet_interaction(tweet, api)
        if response:
            # Mark tweet as processed
            _mark_tweet_processed(tweet["id"], storage)


def _is_tweet_processed(tweet_id: int, storage: ApplicationStorage) -> bool:
    """Check if a tweet has already been processed to avoid duplicate responses."""
    results = storage.search_data("twitter_processed", filters={"tweet_id": tweet_id})
    return len(results) > 0


def _mark_tweet_processed(tweet_id: int, storage: ApplicationStorage) -> None:
    """Mark a tweet as processed after handling it."""
    storage.add_data(
        "twitter_processed",
        {"tweet_id": tweet_id, "processed_at": datetime.now().timestamp()},
    )
