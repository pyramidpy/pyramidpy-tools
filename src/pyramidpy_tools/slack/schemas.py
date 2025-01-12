from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SlackChannel(BaseModel):
    id: str
    name: str
    is_channel: bool
    created: int
    creator: str
    is_archived: bool
    is_general: bool
    members: Optional[List[str]] = None
    topic: Dict[str, Any]
    purpose: Dict[str, Any]
    is_member: bool
    last_read: Optional[str] = None
    unread_count: Optional[int] = None


class SlackMessage(BaseModel):
    type: str
    user: str
    text: str
    ts: str
    thread_ts: Optional[str] = None
    reply_count: Optional[int] = None
    replies: Optional[List[Dict[str, Any]]] = None


class SlackUser(BaseModel):
    id: str
    team_id: str
    name: str
    deleted: bool
    real_name: str
    profile: Dict[str, Any]
    is_admin: Optional[bool] = None
    is_owner: Optional[bool] = None
    is_bot: Optional[bool] = None


class SlackUserProfile(BaseModel):
    title: Optional[str] = None
    phone: Optional[str] = None
    skype: Optional[str] = None
    real_name: Optional[str] = None
    real_name_normalized: Optional[str] = None
    display_name: Optional[str] = None
    display_name_normalized: Optional[str] = None
    status_text: Optional[str] = None
    status_emoji: Optional[str] = None
    email: Optional[str] = None


# Request Models
class ListChannelsRequest(BaseModel):
    limit: Optional[int] = Field(
        100, description="Maximum number of channels to return (default 100, max 200)"
    )
    cursor: Optional[str] = Field(
        None, description="Pagination cursor for next page of results"
    )


class PostMessageRequest(BaseModel):
    channel_id: str = Field(..., description="The ID of the channel to post to")
    text: str = Field(..., description="The message text to post")


class ReplyToThreadRequest(BaseModel):
    channel_id: str = Field(
        ..., description="The ID of the channel containing the thread"
    )
    thread_ts: str = Field(..., description="The timestamp of the parent message")
    text: str = Field(..., description="The reply text")


class AddReactionRequest(BaseModel):
    channel_id: str = Field(
        ..., description="The ID of the channel containing the message"
    )
    timestamp: str = Field(..., description="The timestamp of the message to react to")
    reaction: str = Field(
        ..., description="The name of the emoji reaction (without ::)"
    )


class GetChannelHistoryRequest(BaseModel):
    channel_id: str = Field(..., description="The ID of the channel")
    limit: Optional[int] = Field(
        10, description="Number of messages to retrieve (default 10)"
    )


class GetThreadRepliesRequest(BaseModel):
    channel_id: str = Field(
        ..., description="The ID of the channel containing the thread"
    )
    thread_ts: str = Field(..., description="The timestamp of the parent message")


class GetUsersRequest(BaseModel):
    cursor: Optional[str] = Field(
        None, description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        100, description="Maximum number of users to return (default 100, max 200)"
    )


class GetUserProfileRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user")


# Response Models
class SlackResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class ListChannelsResponse(SlackResponse):
    channels: Optional[List[SlackChannel]] = None
    response_metadata: Optional[Dict[str, Any]] = None


class PostMessageResponse(SlackResponse):
    channel: str
    ts: str
    message: SlackMessage


class AddReactionResponse(SlackResponse):
    pass


class GetChannelHistoryResponse(SlackResponse):
    messages: List[SlackMessage]
    has_more: bool
    response_metadata: Optional[Dict[str, Any]] = None


class GetThreadRepliesResponse(SlackResponse):
    messages: List[SlackMessage]
    has_more: bool
    response_metadata: Optional[Dict[str, Any]] = None


class GetUsersResponse(SlackResponse):
    members: List[SlackUser]
    response_metadata: Optional[Dict[str, Any]] = None


class GetUserProfileResponse(SlackResponse):
    profile: SlackUserProfile
