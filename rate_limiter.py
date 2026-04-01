import time

import redis

# Connect to Redis (Docker service name = redis)
r = redis.Redis(host="redis", port=6379, decode_responses=True)


def get_redis():
    try:
        r.ping()
        return r
    except Exception:
        return None


def is_rate_limited(user_id: str, limit: int = 20, window: int = 90) -> bool:
    """
    Sliding window rate limiter.

    Args:
        user_id: unique identifier
        limit: max requests allowed
        window: time window in seconds
    """

    client = get_redis()

    # Fail-open (important for demo)
    if client is None:
        return False

    current_time = int(time.time())
    key = f"rate:{user_id}"

    client.zremrangebyscore(key, 0, current_time - window)
    request_count = client.zcard(key)

    if request_count >= limit:
        return True

    # Add request with unique member
    client.zadd(key, {f"{current_time}-{time.time()}": current_time})

    client.expire(key, window)

    return False
