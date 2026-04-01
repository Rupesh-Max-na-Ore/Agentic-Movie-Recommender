import time
from collections import defaultdict

import redis

local_store = defaultdict(list)

# Connect to Redis (Docker service name = redis)
r = redis.Redis(host="redis", port=6379, decode_responses=True)


def get_redis():
    try:
        r.ping()
        return r
    except Exception:
        return None


def is_rate_limited(user_id: str, limit: int = 20, window: int = 90) -> bool:
    client = get_redis()
    current_time = int(time.time())

    # ✅ If Redis available → use it
    if client:
        key = f"rate:{user_id}"
        client.zremrangebyscore(key, 0, current_time - window)
        count = client.zcard(key)

        if count >= limit:
            return True

        client.zadd(key, {f"{current_time}-{time.time()}": current_time})
        client.expire(key, window)
        return False

    # FALLBACK: in-memory limiter
    timestamps = local_store[user_id]

    # remove old
    local_store[user_id] = [t for t in timestamps if t > current_time - window]

    if len(local_store[user_id]) >= limit:
        return True

    local_store[user_id].append(current_time)
    return False
