import asyncio
from typing import Dict, List, Optional

from ayrshare import SocialPost

from .schemas import (
    AyrshareAuth,
    DeletePostOptions,
    HistoryOptions,
    PostOptions,
    PostResponse,
)


class AyrshareAPI:
    def __init__(self, auth: AyrshareAuth):
        self.auth = auth
        self.client = SocialPost(auth.api_key)
        self.loop = asyncio.get_event_loop()

    def set_profile_key(self, profile_key: str) -> "AyrshareAPI":
        """Set or update the Profile-Key in the headers."""
        if profile_key:
            self.client.setProfileKey(profile_key)
        return self

    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool."""
        return await self.loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def post(self, options: PostOptions) -> PostResponse:
        """Create a new social media post."""
        post_data = options.dict(exclude_none=True)
        result = await self._run_sync(self.client.post, post_data)
        return PostResponse(**result)

    async def delete_post(self, options: DeletePostOptions) -> Dict:
        """Delete a post."""
        delete_data = options.dict(exclude_none=True)
        return await self._run_sync(self.client.delete, delete_data)

    async def get_post(self, post_id: Optional[str] = None, **params) -> Dict:
        """Get a specific post or list of posts."""
        data = {"id": post_id} if post_id else params
        return await self._run_sync(self.client.getPost, data)

    async def retry_post(self, data: Dict) -> Dict:
        """Retry a failed post."""
        return await self._run_sync(self.client.retryPost, data)

    async def update_post(self, data: Dict) -> Dict:
        """Update an existing post."""
        return await self._run_sync(self.client.updatePost, data)

    async def history(self, options: Optional[HistoryOptions] = None) -> List[Dict]:
        """Get post history."""
        params = options.dict(exclude_none=True) if options else {}
        return await self._run_sync(self.client.history, params)

    async def media(self, params: Optional[Dict] = None) -> Dict:
        """Get media files."""
        return await self._run_sync(self.client.media, params)

    async def verify_media_exists(self, params: Dict) -> Dict:
        """Verify if media URL exists."""
        return await self._run_sync(self.client.verifyMediaExists, params)

    async def get_media_upload_url(self, params: Optional[Dict] = None) -> Dict:
        """Get URL for media upload."""
        return await self._run_sync(self.client.mediaUploadUrl, params)

    async def get_media_meta(self, params: Optional[Dict] = None) -> Dict:
        """Get media metadata."""
        return await self._run_sync(self.client.mediaMeta, params)

    async def resize_image(self, data: Dict) -> Dict:
        """Resize an image."""
        return await self._run_sync(self.client.resizeImage, data)

    async def post_analytics(self, data: Dict) -> Dict:
        """Get post analytics."""
        return await self._run_sync(self.client.analyticsPost, data)

    async def social_analytics(self, params: Dict) -> Dict:
        """Get social media analytics."""
        return await self._run_sync(self.client.analyticsSocial, params)

    async def get_user(self, params: Optional[Dict] = None) -> Dict:
        """Get user information."""
        return await self._run_sync(self.client.user, params)

    async def upload_media(self, data: Dict) -> Dict:
        """Upload media from a URL."""
        return await self._run_sync(self.client.upload, data)

    async def create_profile(self, data: Dict) -> Dict:
        """Create a new profile."""
        return await self._run_sync(self.client.createProfile, data)

    async def delete_profile(self, data: Dict) -> Dict:
        """Delete a profile."""
        return await self._run_sync(self.client.deleteProfile, data)

    async def update_profile(self, data: Dict) -> Dict:
        """Update a profile."""
        return await self._run_sync(self.client.updateProfile, data)

    async def get_profiles(self, params: Optional[Dict] = None) -> Dict:
        """Get profiles."""
        return await self._run_sync(self.client.getProfiles, params)

    async def generate_jwt(self, data: Dict) -> Dict:
        """Generate JWT token."""
        return await self._run_sync(self.client.generateJWT, data)

    async def unlink_social(self, data: Dict) -> Dict:
        """Unlink social media account."""
        return await self._run_sync(self.client.unlinkSocial, data)

    async def post_comment(self, data: Dict) -> Dict:
        """Post a comment."""
        return await self._run_sync(self.client.postComment, data)

    async def get_comments(self, params: Optional[Dict] = None) -> Dict:
        """Get comments."""
        return await self._run_sync(self.client.getComments, params)

    async def delete_comments(self, data: Dict) -> Dict:
        """Delete comments."""
        return await self._run_sync(self.client.deleteComments, data)

    async def reply_comment(self, data: Dict) -> Dict:
        """Reply to a comment."""
        return await self._run_sync(self.client.replyComment, data)

    async def set_auto_schedule(self, data: Dict) -> Dict:
        """Set auto schedule."""
        return await self._run_sync(self.client.setAutoSchedule, data)

    async def delete_auto_schedule(self, data: Dict) -> Dict:
        """Delete auto schedule."""
        return await self._run_sync(self.client.deleteAutoSchedule, data)

    async def list_auto_schedule(self, params: Optional[Dict] = None) -> Dict:
        """List auto schedules."""
        return await self._run_sync(self.client.listAutoSchedule, params)

    async def register_webhook(self, data: Dict) -> Dict:
        """Register a webhook."""
        return await self._run_sync(self.client.registerWebhook, data)

    async def unregister_webhook(self, data: Dict) -> Dict:
        """Unregister a webhook."""
        return await self._run_sync(self.client.unregisterWebhook, data)

    async def list_webhooks(self, params: Optional[Dict] = None) -> Dict:
        """List webhooks."""
        return await self._run_sync(self.client.listWebhooks, params)

    async def auto_hashtags(self, params: Dict) -> Dict:
        """Generate automatic hashtags."""
        return await self._run_sync(self.client.autoHashtags, params)

    async def recommend_hashtags(self, params: Optional[Dict] = None) -> Dict:
        """Get hashtag recommendations."""
        return await self._run_sync(self.client.recommendHashtags, params)

    async def check_banned_hashtags(self, params: Optional[Dict] = None) -> Dict:
        """Check for banned hashtags."""
        return await self._run_sync(self.client.checkBannedHashtags, params)

    async def short_link(self, params: Dict) -> Dict:
        """Create a short link."""
        return await self._run_sync(self.client.shortLink, params)

    async def short_link_analytics(self, params: Dict) -> Dict:
        """Get short link analytics."""
        return await self._run_sync(self.client.shortLinkAnalytics, params)

    async def get_reviews(self, params: Optional[Dict] = None) -> Dict:
        """Get reviews."""
        return await self._run_sync(self.client.reviews, params)

    async def get_review(self, params: Dict) -> Dict:
        """Get a specific review."""
        return await self._run_sync(self.client.review, params)

    async def review_reply(self, params: Dict) -> Dict:
        """Reply to a review."""
        return await self._run_sync(self.client.reviewReply, params)

    async def delete_review_reply(self, params: Dict) -> Dict:
        """Delete a review reply."""
        return await self._run_sync(self.client.deleteReviewReply, params)
