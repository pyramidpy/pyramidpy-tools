from typing import Callable, Dict, Any


AuthCallback = Callable[[str, Dict[str, Any]], Dict[str, Any] | None]


def get_auth_from_context(context: Dict[str, Any], key: str) -> Dict[str, Any] | None:
    """
    Get auth from flow context
    :param context: Flow context
    :param key: Key to get auth from
    :return: Auth dict or None

    Auth dict can be injected into the flow context by hard coding it as a dict at the start of the flow.
    For example:
    flow  = Flow(context={"auth": {"twitter_auth": {"consumer_key": "123", "consumer_secret": "456"}}})

    For security reasons, you may also want to only fetch auth details at runtime via a callback.
     - For instance when you don't want every agent to have access to sensitive auth details.
     - The auth callback should be a callable that takes a key and context and returns a dict or None.

    Example:
    flow  = Flow(context={"auth": auth_callback})
    """
    callback_or_dict = context.get("auth", {})
    if callback_or_dict is None:
        return None
    if callable(callback_or_dict):
        return callback_or_dict(key, context)
    return callback_or_dict.get(key, None)


def get_tool_streaming_handler(context: Dict[str, Any]) -> Callable[[Any], None]:
    """
    Get a streaming handler for a tool
    """
    return context.get("tool_streaming_handler", None)
