from aiocache import caches

def init_cache(redis_dsn: str or None) -> None:
    """
    Переключает aiocache на Redis, если dsn указан.
    Если dsn = '', используем встроенный MemoryCache (как было до сих пор).
    """
    if redis_dsn:
        host, port = redis_dsn.split(":")
        caches.set_config({
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": host,
                "port": int(port),
                "serializer": {"class": "aiocache.serializers.PickleSerializer"},
                "namespace": "mal",
                "ttl": 86_400,
                "timeout": 1
            }
        })
    else:
        caches.set_config({
            "default": {
                "cache": "aiocache.SimpleMemoryCache",
                "ttl": 86_400
            }
        })
