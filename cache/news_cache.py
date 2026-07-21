"""新闻相关缓存工具函数。"""

from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_json_cache

RELATED_NEWS_PREFIX = "news:related:"


async def get_cached_related_news(category_id: int, exclude_id: int) -> Optional[List[Dict[str, Any]]]:
    """
    获取缓存的相关新闻列表。

    Args:
        category_id: 分类 ID。
        exclude_id: 排除的新闻 ID。

    Returns:
        缓存的相关新闻列表，不存在则返回 None。
    """
    key = f"{RELATED_NEWS_PREFIX}{category_id}:{exclude_id}"
    return await get_json_cache(key)


async def cache_related_news(
    category_id: int,
    exclude_id: int,
    related_list: List[Dict[str, Any]],
    expire: int = 300,
) -> bool:
    """
    缓存相关新闻列表（5 分钟有效期）。

    Args:
        category_id: 分类 ID。
        exclude_id: 排除的新闻 ID。
        related_list: 相关新闻列表数据。
        expire: 过期时间（秒），默认 5 分钟。

    Returns:
        缓存成功返回 True。
    """
    key = f"{RELATED_NEWS_PREFIX}{category_id}:{exclude_id}"
    return await set_json_cache(key, related_list, expire)
