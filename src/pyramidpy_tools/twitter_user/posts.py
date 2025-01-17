from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import logging
from ..application.base import ApplicationStorage
from .schemas import (
    TimelineRequest,
    TweetActionRequest,
    ScheduleTweetRequest,
)

logger = logging.getLogger(__name__)

# Default template for tweet generation
TWITTER_POST_TEMPLATE = """
Write a tweet about {topic} that is engaging and informative.
Keep it under {max_length} characters.
Include relevant hashtags if appropriate.
"""

def compose_context(state: Dict[str, Any], template: str) -> str:
    """
    Compose context for tweet generation from state and template.
    
    Args:
        state: State dictionary containing agent info, topics etc
        template: Template string to use
        
    Returns:
        Composed context string
    """
    # Extract relevant info from state
    topic = state.get("topic", "")
    max_length = state.get("max_length", 280)
    
    # Format template with state values
    return template.format(
        topic=topic,
        max_length=max_length
    )

def generate_text(context: str, api) -> Optional[str]:
    """
    Generate text content using the API's text generation capabilities.
    
    Args:
        context: Context string for generation
        api: Twitter API instance
        
    Returns:
        Generated text or None if generation failed
    """
    try:
        # Use API's text generation method
        return api.generate_text(context)
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return None

def clean_tweet_content(content: str, max_length: int = 280) -> str:
    """
    Clean and format tweet content, handling JSON responses and ensuring proper formatting.

    Args:
        content: Raw tweet content
        max_length: Maximum tweet length

    Returns:
        Cleaned and formatted content
    """
    # First try parsing as JSON
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            content = (
                parsed.get("text")
                or parsed.get("content")
                or parsed.get("message")
                or parsed.get("response", "")
            )
        elif isinstance(parsed, str):
            content = parsed
    except json.JSONDecodeError:
        # If not JSON, clean the raw content
        content = (
            content.replace(
                r"^\s*{?\s*\"text\":\s*\"|\"\s*}?\s*$", ""
            )  # Remove JSON-like wrapper
            .replace(r"^['\"](.*)['\"]$", r"$1")  # Remove quotes
            .replace(r"\\\"", r'"')  # Unescape quotes
            .replace(r"\\n", r"\n\n")  # Unescape newlines, ensures double spaces
            .strip()
        )

    # Truncate to last sentence if needed
    if len(content) > max_length:
        last_sentence = content.rfind(".", 0, max_length - 3)
        if last_sentence > 0:
            content = content[: last_sentence + 1].strip()
        else:
            last_space = content.rfind(" ", 0, max_length - 3)
            content = content[:last_space].strip() + "..."

    return content

def generate_tweet_content(
    state: Dict[str, Any],
    api,
    template: Optional[str] = None,
    context: Optional[str] = None,
    max_length: int = 280,
) -> Optional[str]:
    """
    Generate tweet content using provided state and templates.

    Args:
        state: State dictionary containing agent info, topics etc
        api: Twitter API instance
        template: Optional custom template to use
        context: Optional custom context
        max_length: Maximum tweet length

    Returns:
        Generated and cleaned tweet content
    """
    # Compose context from state and template
    if not context:
        context = compose_context(state, template or TWITTER_POST_TEMPLATE)

    # Generate content
    content = generate_text(context, api)
    if not content:
        logger.error("Failed to generate tweet content")
        return None

    # Clean and format content
    return clean_tweet_content(content, max_length)


def post_tweet(
    content: str,
    room_id: str,
    agent_id: str,
    api,
    dry_run: bool = False,
    requires_approval: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Post a new tweet with proper caching and memory management.

    Args:
        content: Tweet content to post
        room_id: Room ID for memory storage
        agent_id: Agent ID for memory storage
        api: Twitter API instance
        dry_run: If True, only simulate posting
        requires_approval: If True, send for approval instead of posting

    Returns:
        Posted tweet data if successful
    """
    try:
        if dry_run:
            logger.info(f"Dry run - would tweet: {content}")
            return None

        # if requires_approval:
        #     return send_for_approval(content, room_id)

        # Post the tweet
        if len(content) > 280:
            result = handle_note_tweet(content, api=api)
        else:
            result = send_standard_tweet(content, api=api)

        if not result:
            return None

        # Create tweet object
        tweet = create_tweet_object(result, api)

        # Cache and process tweet
        process_and_cache_tweet(tweet, room_id, content, agent_id, api)

        return tweet

    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return None


def handle_note_tweet(
    content: str, api, tweet_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Handle posting longer tweets as note tweets"""
    try:
        result = api.send_note_tweet(content, tweet_id)

        if result.get("errors"):
            # Fallback to standard tweet
            content = clean_tweet_content(content)
            return send_standard_tweet(content, api, tweet_id)

        return result["data"]["notetweet_create"]["tweet_results"]["result"]

    except Exception as e:
        logger.error(f"Note tweet failed: {e}")
        return None


def send_standard_tweet(
    content: str, api, tweet_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Send a standard tweet"""
    try:
        result = api.send_tweet(content, tweet_id)

        if (
            not result.get("data", {})
            .get("create_tweet", {})
            .get("tweet_results", {})
            .get("result")
        ):
            logger.error("Error sending tweet; Bad response")
            return None

        return result["data"]["create_tweet"]["tweet_results"]["result"]

    except Exception as e:
        logger.error(f"Error sending standard tweet: {e}")
        return None


def create_tweet_object(tweet_result: Dict[str, Any], api) -> Dict[str, Any]:
    """Create a standardized tweet object from API result"""
    return {
        "id": tweet_result["rest_id"],
        "name": api.profile.screen_name,
        "username": api.profile.username,
        "text": tweet_result["legacy"]["full_text"],
        "conversation_id": tweet_result["legacy"]["conversation_id_str"],
        "created_at": tweet_result["legacy"]["created_at"],
        "timestamp": datetime.strptime(
            tweet_result["legacy"]["created_at"], "%a %b %d %H:%M:%S %z %Y"
        ).timestamp(),
        "user_id": api.profile.id,
        "in_reply_to_status_id": tweet_result["legacy"].get(
            "in_reply_to_status_id_str"
        ),
        "permanent_url": f"https://twitter.com/{api.profile.username}/status/{tweet_result['rest_id']}",
        "hashtags": [],
        "mentions": [],
        "photos": [],
        "thread": [],
        "urls": [],
        "videos": [],
    }


def process_and_cache_tweet(
    tweet: Dict[str, Any], room_id: str, content: str, agent_id: str, api
):
    """Process and cache a posted tweet"""
    # Create storage instance
    storage = ApplicationStorage()

    # Cache tweet data
    tweet_data = {
        "id": tweet["id"],
        "timestamp": datetime.now().timestamp(),
        "content": content.strip(),
        "url": tweet["permanent_url"],
        "source": "twitter",
        "user_id": agent_id,
        "agent_id": agent_id,
        "room_id": room_id,
    }

    # Store in vector store
    storage.add_data(
        "twitter_tweets",
        tweet_data
    )

    logger.info(f"Tweet posted: {tweet['permanent_url']}")


def schedule_tweet(content: str, scheduled_time: datetime, api) -> Optional[Dict[str, Any]]:
    """
    Schedule a tweet for later posting.

    Args:
        content: Tweet content
        scheduled_time: When to post the tweet
        api: Twitter API instance

    Returns:
        Scheduled tweet data if successful, None otherwise
    """
    try:
        request = ScheduleTweetRequest(text=content, scheduled_time=scheduled_time)
        return api.schedule_tweet(request)

    except Exception as e:
        print(f"Error scheduling tweet: {e}")
        return None


def unschedule_tweet(tweet_id: int, api) -> Optional[Dict[str, Any]]:
    """
    Cancel a scheduled tweet.

    Args:
        tweet_id: ID of scheduled tweet to cancel
        api: Twitter API instance

    Returns:
        Response data if successful, None otherwise
    """
    try:
        request = TweetActionRequest(tweet_id=tweet_id)
        return api.unschedule_tweet(request)

    except Exception as e:
        print(f"Error unscheduling tweet: {e}")
        return None


def get_recent_tweets(api, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent tweets from the timeline.

    Args:
        api: Twitter API instance
        limit: Maximum number of tweets to fetch

    Returns:
        List of recent tweets
    """
    request = TimelineRequest(limit=limit)
    return api.get_latest_timeline(request)


def process_pending_tweets(api) -> None:
    """Process any pending scheduled tweets"""
    # Add pending tweet processing logic here
    pass
