from typing import Literal

import redis
from diskcache import Cache as DiskCache
from fakeredis import FakeRedis

from pyramidpy_tools.settings import settings


def get_redis_client():
    try:
        if settings.storage.redis.use_fake_redis:
            return FakeRedis()
        return redis.Redis.from_url(settings.storage.redis.url)
    except Exception:
        return FakeRedis()


class Cache:
    storage_type: Literal["redis", "disk"] = "disk"
    client: redis.Redis | FakeRedis | DiskCache

    def __init__(self, storage_type: Literal["redis", "disk"] | None = "disk"):
        self.storage_type = storage_type or "disk"

        if self.storage_type == "redis":
            self.client = get_redis_client()
        else:
            self.client = DiskCache("./cache")

    def get(self, key: str) -> str | None:
        return self.client.get(key)

    def set(self, key: str, value: str) -> None:
        self.client.set(key, value)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def clear(self) -> None:
        self.client.clear()


def get_cache() -> Cache:
    return Cache()


redis_client = get_redis_client()
