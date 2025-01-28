from typing import Dict, List, Optional

from .base import AyrshareAPI
from .schemas import (
    DeletePostOptions,
    HistoryOptions,
    PostOptions,
)


class AyrshareTools:
    """High-level tools for interacting with Ayrshare API."""

    def __init__(self, api: AyrshareAPI):
        self.api = api

    async def create_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        title: Optional[str] = None,
        scheduled_time: Optional[str] = None,
        shorten_links: bool = False,
        profile_key: Optional[str] = None,
    ):
        """Create a new social media post across multiple platforms.

        Args:
            text: The text content of the post
            platforms: List of platforms to post to (e.g. ["twitter", "facebook"])
            media_urls: Optional list of media URLs to attach
            title: Optional title for the post
            scheduled_time: Optional ISO 8601 timestamp for scheduling
            shorten_links: Whether to shorten URLs in the post
            profile_key: Optional profile key for multi-profile posting
        """
        # Set profile key if provided
        if profile_key:
            self.api.set_profile_key(profile_key)

        post_data = {
            "post": text,
            "platforms": platforms,
        }

        if media_urls:
            post_data["mediaUrls"] = media_urls
        if title:
            post_data["title"] = title
        if scheduled_time:
            post_data["scheduledTime"] = scheduled_time
        if shorten_links:
            post_data["shortenLinks"] = shorten_links

        return await self.api.post(PostOptions(**post_data))

    async def delete_posts(
        self,
        post_ids: List[str],
        platforms: Optional[List[str]] = None,
    ):
        """Delete multiple posts from specified platforms.

        Args:
            post_ids: List of post IDs to delete
            platforms: Optional list of specific platforms to delete from
        """
        results = []
        for post_id in post_ids:
            delete_data = {"id": post_id}
            if platforms:
                delete_data["platforms"] = platforms
            result = await self.api.delete_post(DeletePostOptions(**delete_data))
            results.append(result)
        return results

    async def get_post_history(
        self,
        last: Optional[int] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
    ):
        """Get post history with optional filters.

        Args:
            last: Number of posts to return
            platform: Filter by platform
            status: Filter by post status
        """
        options = HistoryOptions(
            last=last,
            platform=platform,
            status=status,
        )
        return await self.api.history(options)

    async def upload_media_files(self, file_urls: List[str]):
        """Upload multiple media files from URLs.

        Args:
            file_urls: List of URLs to upload
        """
        results = []
        for url in file_urls:
            result = await self.api.upload_media({"file": url})
            results.append(result)
        return results

    async def get_post_analytics(self, post_ids: List[str]):
        """Get analytics for multiple posts.

        Args:
            post_ids: List of post IDs to get analytics for
        """
        results = []
        for post_id in post_ids:
            result = await self.api.post_analytics({"id": post_id})
            results.append(result)
        return results

    async def auto_schedule_posts(
        self,
        posts: List[Dict],
        schedule_days: List[str],
        schedule_times: List[str],
        timezone: str = "America/New_York",
    ):
        """Set up auto-scheduling for multiple posts.

        Args:
            posts: List of post data dictionaries
            schedule_days: List of days (e.g. ["Monday", "Wednesday", "Friday"])
            schedule_times: List of times in 24h format (e.g. ["09:00", "15:00"])
            timezone: Timezone for scheduling (default: America/New_York)
        """
        schedule_data = {
            "posts": posts,
            "scheduleDays": schedule_days,
            "scheduleTimes": schedule_times,
            "timezone": timezone,
        }
        return await self.api.set_auto_schedule(schedule_data)

    async def generate_hashtags(
        self,
        text: str,
        platforms: Optional[List[str]] = None,
        num_hashtags: Optional[int] = None,
    ):
        """Generate hashtags for a post.

        Args:
            text: The post text to generate hashtags for
            platforms: Optional list of platforms to target
            num_hashtags: Optional number of hashtags to generate
        """
        hashtag_data = {"text": text}
        if platforms:
            hashtag_data["platforms"] = platforms
        if num_hashtags:
            hashtag_data["numHashtags"] = num_hashtags
        return await self.api.auto_hashtags(hashtag_data)
