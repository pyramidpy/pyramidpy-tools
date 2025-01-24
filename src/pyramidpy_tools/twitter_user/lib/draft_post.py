"""
Simple strategy flow example that integrates large language model (LLM) generation.
1. Fetches the latest timeline tweets (limited).
2. Analyzes performance simply, checking if "topic X" tweets are successful.
3. Dynamically creates a prompt and uses a LLM to generate tweet content.
4. Posts the tweet with the TwitterUserAPI (or TweepyTwitterApi).
"""

from typing import List, Dict, Any
import controlflow as cf
from pyramidpy_tools.twitter_user.base import (
    TwitterUserAPI,
    TweetRequest,
    TimelineRequest,
)
from pyramidpy_tools.core.llm import get_llm
from pyramidpy_tools.settings import settings
from pyramidpy_tools.prompt.base import render_template

###############################################################################
# Simple analysis function
###############################################################################


def simple_analyze_performance(recent_tweets: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Examines a small list of recent tweets and tallies likes or retweets
    for tweets containing "Topic X" in their text.

    Returns a dictionary with a count of likes associated specifically with "Topic X".
    """
    topic_x_likes = 0

    for tweet_data in recent_tweets:
        tweet_text = tweet_data.get("text", "").lower()
        tweet_likes = tweet_data.get("likes", 0)

        # Check if "topic x" is mentioned in the tweet text
        if "topic x" in tweet_text:
            topic_x_likes += tweet_likes

    return {"topicX_likes": topic_x_likes}


###############################################################################
# Prompt Generation Helpers
###############################################################################


def create_dynamic_prompt(template: str, placeholders: Dict[str, Any]) -> str:
    """
    Substitutes placeholders into the provided template.
    Simple approach: for each placeholder key in 'placeholders',
    replace '{{key}}' in the template with the str(placeholders[key]).
    Supports both Jinja2 and Python f-strings.
    """

    prompt = template
    for key, value in placeholders.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
    return prompt


def generate_tweet_content(
    prompt_template: str | None = None,
    placeholders: Dict[str, Any] | None = None,
    model: str | None = None,
    agent: cf.Agent | None = None,
) -> str:
    """
    Dynamically generates tweet content by:
      - Filling the prompt template with placeholders.
      - Invoking the chosen LLM to produce the final text.
    """
    model = model or settings.llm.default_model
    prepared_prompt = render_template(prompt_template, **placeholders)
    llm = get_llm(model)
    generated_text = llm.invoke(prepared_prompt)
    return generated_text


###############################################################################
# Main function: Draft and post tweet using a simple logic + LLM generation
###############################################################################


def draft_and_post_simple_tweet(
    api: TwitterUserAPI,
    strategy_parameters: Dict[str, Any],
    llm_model: str = "openai/gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Implements a simple logic:
    1. Retrieves a few of the latest tweets.
    2. Uses 'simple_analyze_performance' to see if "Topic X" tweets do well.
    3. Uses a dynamic LLM prompt to generate the final tweet text.
    4. Posts the tweet with `api.send_tweet`.

    :param api: An instance of TwitterUserAPI (or TweepyTwitterApi).
    :param strategy_parameters: A dict representing any needed parameters for the strategy.
    :return: The response from Twitter after posting the tweet.
    """

    # 1. Retrieve recent tweets (small window: limit=5)
    recent_tweets = api.get_latest_timeline(TimelineRequest(limit=5))

    # 2. Analyze the performance of those recent tweets
    performance_data = simple_analyze_performance(recent_tweets)

    # Decide on a "topic" or "message" to pass to the prompt based on performance
    if performance_data["topicX_likes"] > 10:
        topic_message = "Topic X is trending!"
    else:
        topic_message = "Topic X might be quieter, try a new angle."

    # 3. Prepare a dynamic prompt template
    #    This template includes placeholders for e.g. 'topic_message' and 'hashtags'.
    prompt_template = (
        "Draft a short, engaging tweet talking about: {{topic_message}}. "
        "Include these hashtags if applicable: {{hashtags}}. "
        "Keep it under 280 characters."
    )

    # Pull hashtags or default to empty
    hashtags = strategy_parameters.get("hashtags", [])

    placeholders = {
        "topic_message": topic_message,
        "hashtags": " ".join([f"#{tag}" for tag in hashtags]) if hashtags else "",
    }

    # 4. Generate tweet content using the chosen model
    llm_model = strategy_parameters.get("llm_model", "placeholder-model")
    drafted_content = generate_tweet_content(prompt_template, llm_model, placeholders)

    # 5. Post the tweet
    response = api.send_tweet(TweetRequest(content=drafted_content))

    return response


###############################################################################
# Example usage
###############################################################################

if __name__ == "__main__":
    """
    Quick demonstration of how this might be called.
    Assumes valid credentials are set in environment or passed through `TwitterUserAuth`.
    """
    # Instantiate the TwitterUserAPI (auto-loads credentials from settings, if used).
    twitter_api = TwitterUserAPI()

    # Example strategy parameters
    strategy_params = {
        "hashtags": ["TopicXPerforming"],  # Example optional param
        "llm_model": "gpt-4o-mini",  # Example LLM model name
    }

    post_response = draft_and_post_simple_tweet(twitter_api, strategy_params)
    print("Posted tweet response:", post_response)
