from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news_category import NewsCategory


async def get_categories(db: AsyncSession) -> list[NewsCategory]:
    """
    获取所有新闻分类，按 sort_order 升序排列。

    Args:
        db: 异步数据库会话。

    Returns:
        list[NewsCategory]: 分类列表。
    """
    result = await db.execute(
        select(NewsCategory).order_by(NewsCategory.sort_order)
    )
    return list(result.scalars().all())
