from pyramidpy_tools.utilities.auth import get_auth_from_context

"""
Tests for the auth utilities.

Note on typing:
AuthCallback = Callable[[str, Dict[str, Any]], Dict[str, Any] | None]
This type hint is for documentation and static type checking.
At runtime, we simply check if the object is callable using callable()
rather than checking against the AuthCallback type.
"""


def test_get_auth_from_context_with_dict():
    # Test with hardcoded auth dict
    context = {
        "auth": {"twitter_auth": {"consumer_key": "123", "consumer_secret": "456"}}
    }

    auth = get_auth_from_context(context, "twitter_auth")
    assert auth == {"consumer_key": "123", "consumer_secret": "456"}

    # Test with non-existent key
    auth = get_auth_from_context(context, "non_existent")
    assert auth is None

    # Test with empty auth dict
    context = {"auth": {}}
    auth = get_auth_from_context(context, "twitter_auth")
    assert auth is None

    # Test with None auth
    context = {"auth": None}
    auth = get_auth_from_context(context, "twitter_auth")
    assert auth is None


def test_get_auth_from_context_with_callback():
    # Test with different types of callables

    # Test with regular function
    def auth_callback(key: str, ctx: dict):
        if key == "twitter_auth":
            return {"consumer_key": "789", "consumer_secret": "012"}
        return None

    context = {"auth": auth_callback}
    auth = get_auth_from_context(context, "twitter_auth")
    assert auth == {"consumer_key": "789", "consumer_secret": "012"}

    # Test with lambda function
    context = {"auth": lambda k, c: {"key": "value"} if k == "test" else None}
    auth = get_auth_from_context(context, "test")
    assert auth == {"key": "value"}

    # Test with invalid key
    auth = get_auth_from_context(context, "non_existent")
    assert auth is None


def test_get_auth_from_context_empty():
    # Test with empty context
    context = {}
    auth = get_auth_from_context(context, "twitter_auth")
    assert auth is None
