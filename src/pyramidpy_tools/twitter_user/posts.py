from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import logging
from .tools import get_twitter_api
from .schemas import (
    TimelineRequest,
    TweetRequest,
    ReplyRequest,
    QuoteRequest,
    TweetActionRequest,
    ScheduleTweetRequest
)

logger = logging.getLogger(__name__)

# Templates
TWITTER_POST_TEMPLATE = """
# Areas of Expertise
{{knowledge}}

# About {{agentName}} (@{{twitterUserName}}):
{{bio}}
{{lore}}
{{topics}}

{{providers}}

{{characterPostExamples}}

{{postDirections}}

# Task: Generate a post in the voice and style and perspective of {{agentName}} @{{twitterUserName}}.
Write a post that is {{adjective}} about {{topic}} (without mentioning {{topic}} directly), from the perspective of {{agentName}}. Do not add commentary or acknowledge this request, just write the post.
Your response should be 1, 2, or 3 sentences (choose the length at random).
Your response should not contain any questions. Brief, concise statements only. The total character count MUST be less than {{maxTweetLength}}. No emojis. Use \\n\\n (double spaces) between statements if there are multiple statements in your response."""

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
            content = parsed.get('text') or parsed.get('content') or parsed.get('message') or parsed.get('response', '')
        elif isinstance(parsed, str):
            content = parsed
    except json.JSONDecodeError:
        # If not JSON, clean the raw content
        content = (content
            .replace(/^\s*{?\s*"text":\s*"|"\s*}?\s*$/g, "")  # Remove JSON-like wrapper
            .replace(/^['"](.*)['"]$/g, "$1")  # Remove quotes
            .replace(/\\"/g, '"')  # Unescape quotes
            .replace(/\\n/g, "\n\n")  # Unescape newlines, ensures double spaces
            .strip())
    
    # Truncate to last sentence if needed
    if len(content) > max_length:
        last_sentence = content.rfind('.', 0, max_length-3)
        if last_sentence > 0:
            content = content[:last_sentence+1].strip()
        else:
            last_space = content.rfind(' ', 0, max_length-3)
            content = content[:last_space].strip() + "..."
            
    return content

def generate_tweet_content(
    state: Dict[str, Any],
    template: Optional[str] = None,
    context: Optional[str] = None,
    max_length: int = 280
) -> Optional[str]:
    """
    Generate tweet content using provided state and templates.
    
    Args:
        state: State dictionary containing agent info, topics etc
        template: Optional custom template to use
        context: Optional custom context
        max_length: Maximum tweet length
        
    Returns:
        Generated and cleaned tweet content
    """
    twitter = get_twitter_api()
    
    # Compose context from state and template
    if not context:
        context = compose_context(state, template or TWITTER_POST_TEMPLATE)
        
    # Generate content
    content = generate_text(context)
    if not content:
        logger.error("Failed to generate tweet content")
        return None
        
    # Clean and format content
    return clean_tweet_content(content, max_length)

def post_tweet(
    content: str,
    room_id: str,
    agent_id: str,
    dry_run: bool = False,
    requires_approval: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Post a new tweet with proper caching and memory management.
    
    Args:
        content: Tweet content to post
        room_id: Room ID for memory storage
        agent_id: Agent ID for memory storage
        dry_run: If True, only simulate posting
        requires_approval: If True, send for approval instead of posting
        
    Returns:
        Posted tweet data if successful
    """
    twitter = get_twitter_api()
    
    try:
        if dry_run:
            logger.info(f"Dry run - would tweet: {content}")
            return None
            
        if requires_approval:
            return send_for_approval(content, room_id)
            
        # Post the tweet
        if len(content) > 280:
            result = handle_note_tweet(content)
        else:
            result = send_standard_tweet(content)
            
        if not result:
            return None
            
        # Create tweet object
        tweet = create_tweet_object(result)
        
        # Cache and process tweet
        process_and_cache_tweet(tweet, room_id, content, agent_id)
        
        return tweet
        
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return None

def handle_note_tweet(content: str, tweet_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Handle posting longer tweets as note tweets"""
    twitter = get_twitter_api()
    
    try:
        result = twitter.send_note_tweet(content, tweet_id)
        
        if result.get('errors'):
            # Fallback to standard tweet
            content = clean_tweet_content(content)
            return send_standard_tweet(content, tweet_id)
            
        return result['data']['notetweet_create']['tweet_results']['result']
        
    except Exception as e:
        logger.error(f"Note tweet failed: {e}")
        return None

def send_standard_tweet(content: str, tweet_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Send a standard tweet"""
    twitter = get_twitter_api()
    
    try:
        result = twitter.send_tweet(content, tweet_id)
        
        if not result.get('data', {}).get('create_tweet', {}).get('tweet_results', {}).get('result'):
            logger.error("Error sending tweet; Bad response")
            return None
            
        return result['data']['create_tweet']['tweet_results']['result']
        
    except Exception as e:
        logger.error(f"Error sending standard tweet: {e}")
        return None

def create_tweet_object(tweet_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standardized tweet object from API result"""
    twitter = get_twitter_api()
    
    return {
        'id': tweet_result['rest_id'],
        'name': twitter.profile.screen_name,
        'username': twitter.profile.username,
        'text': tweet_result['legacy']['full_text'],
        'conversation_id': tweet_result['legacy']['conversation_id_str'],
        'created_at': tweet_result['legacy']['created_at'],
        'timestamp': datetime.strptime(tweet_result['legacy']['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp(),
        'user_id': twitter.profile.id,
        'in_reply_to_status_id': tweet_result['legacy'].get('in_reply_to_status_id_str'),
        'permanent_url': f"https://twitter.com/{twitter.profile.username}/status/{tweet_result['rest_id']}",
        'hashtags': [],
        'mentions': [],
        'photos': [],
        'thread': [],
        'urls': [],
        'videos': []
    }

def process_and_cache_tweet(tweet: Dict[str, Any], room_id: str, content: str, agent_id: str):
    """Process and cache a posted tweet"""
    twitter = get_twitter_api()
    
    # Cache last post details
    twitter.cache_manager.set(
        f"twitter/{twitter.profile.username}/lastPost",
        {
            'id': tweet['id'],
            'timestamp': datetime.now().timestamp()
        }
    )
    
    # Cache the tweet
    twitter.cache_tweet(tweet)
    
    logger.info(f"Tweet posted: {tweet['permanent_url']}")
    
    # Create memory
    twitter.message_manager.create_memory({
        'id': f"{tweet['id']}-{agent_id}",
        'user_id': agent_id,
        'agent_id': agent_id,
        'content': {
            'text': content.strip(),
            'url': tweet['permanent_url'],
            'source': 'twitter'
        },
        'room_id': room_id,
        'created_at': tweet['timestamp']
    })

def schedule_tweet(content: str, scheduled_time: datetime) -> Optional[Dict[str, Any]]:
    """
    Schedule a tweet for later posting.
    
    Args:
        content: Tweet content
        scheduled_time: When to post the tweet
        
    Returns:
        Scheduled tweet data if successful, None otherwise
    """
    twitter = get_twitter_api()
    
    try:
        request = ScheduleTweetRequest(
            text=content,
            scheduled_time=scheduled_time
        )
        return twitter.schedule_tweet(request)
        
    except Exception as e:
        print(f"Error scheduling tweet: {e}")
        return None

def unschedule_tweet(tweet_id: int) -> Optional[Dict[str, Any]]:
    """
    Cancel a scheduled tweet.
    
    Args:
        tweet_id: ID of scheduled tweet to cancel
        
    Returns:
        Response data if successful, None otherwise
    """
    twitter = get_twitter_api()
    
    try:
        request = TweetActionRequest(tweet_id=tweet_id)
        return twitter.unschedule_tweet(request)
        
    except Exception as e:
        print(f"Error unscheduling tweet: {e}")
        return None

def get_recent_tweets(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent tweets from the timeline.
    
    Args:
        limit: Maximum number of tweets to fetch
        
    Returns:
        List of recent tweets
    """
    twitter = get_twitter_api()
    request = TimelineRequest(limit=limit)
    return twitter.get_latest_timeline(request)

def process_pending_tweets() -> None:
    """Process any pending scheduled tweets"""
    twitter = get_twitter_api()
    # Add pending tweet processing logic here
    pass 