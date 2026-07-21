import json
from typing import Any

import redis.asyncio as aioredis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1

# 创建 Redis 异步客户端
redis_client = aioredis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)


async def get_json_cache(key: str):
    """读取 JSON 缓存，失败时返回 None。"""
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"[Redis] 获取缓存失败 key={key}: {e}")
        return None


async def set_json_cache(key: str, value: Any, expire: int = 300):
    """写入 JSON 缓存（自动序列化），失败时返回 False。"""
    try:
        serialized = json.dumps(value, ensure_ascii=False, default=str)
        await redis_client.setex(key, expire, serialized)
        return True
    except Exception as e:
        print(f"[Redis] 设置缓存失败 key={key}: {e}")
        return False
