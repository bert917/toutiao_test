import random
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.news import News
from schemas.news import NewsCreate, NewsUpdate


# 创建新闻
async def create_news(db: AsyncSession, news_in: NewsCreate) -> News:
    """
    创建一条新闻记录。

    Args:
        db: 异步数据库会话。
        news_in: 新闻创建请求数据。

    Returns:
        News: 新创建的新闻 ORM 对象。
    """
    db_obj = News(**news_in.model_dump())
    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj)
    return db_obj


# 根据 ID 获取单条新闻
async def get_news(db: AsyncSession, news_id: int) -> Optional[News]:
    """
    根据 ID 查询单条新闻。

    Args:
        db: 异步数据库会话。
        news_id: 新闻 ID。

    Returns:
        News 或 None: 查到的新闻对象，不存在则返回 None。
    """
    result = await db.execute(select(News).where(News.id == news_id))
    return result.scalar_one_or_none()


# 增加浏览量
async def increment_views(db: AsyncSession, news_id: int) -> Optional[News]:
    """
    将指定新闻的浏览量 +1 并返回更新后的对象。

    Args:
        db: 异步数据库会话。
        news_id: 新闻 ID。

    Returns:
        News 或 None: 更新后的新闻对象，不存在则返回 None。
    """
    db_obj = await get_news(db, news_id)
    if db_obj is None:
        return None
    db_obj.views += 1
    await db.flush()
    await db.refresh(db_obj)
    return db_obj


# 随机推荐（同分类，排除当前新闻，随机返回 3~5 条）
async def get_related_news(
    db: AsyncSession,
    category_id: int,
    exclude_id: int,
) -> list[News]:
    """
    根据分类 ID 随机推荐 3~5 条新闻，排除当前新闻。

    Args:
        db: 异步数据库会话。
        category_id: 当前新闻的分类 ID。
        exclude_id: 需要排除的新闻 ID（当前新闻自身）。

    Returns:
        list[News]: 随机推荐新闻列表（3~5 条）。
    """
    query = (
        select(News)
        .where(News.category_id == category_id, News.id != exclude_id)
    )
    result = await db.execute(query)
    candidates = list(result.scalars().all())

    if not candidates:
        return []

    count = random.randint(3, min(5, len(candidates)))
    return random.sample(candidates, count)


# 分页查询新闻列表
async def get_news_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
) -> list[News]:
    """
    分页查询新闻列表，支持按分类和关键词过滤。

    Args:
        db: 异步数据库会话。
        skip: 跳过的记录数（偏移量）。
        limit: 每页返回的记录数。
        category_id: 按分类 ID 过滤。
        keyword: 按标题关键词过滤（模糊匹配）。

    Returns:
        list[News]: 新闻列表。
    """
    query = select(News)

    if category_id is not None:
        query = query.where(News.category_id == category_id)
    if keyword is not None:
        query = query.where(News.title.contains(keyword))

    query = query.order_by(News.publish_time.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# 获取新闻总数
async def get_news_count(
    db: AsyncSession,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
) -> int:
    """
    获取新闻总数，支持按分类和关键词过滤。

    Args:
        db: 异步数据库会话。
        category_id: 按分类 ID 过滤。
        keyword: 按标题关键词过滤。

    Returns:
        int: 符合条件的新闻总数。
    """
    query = select(func.count(News.id))

    if category_id is not None:
        query = query.where(News.category_id == category_id)
    if keyword is not None:
        query = query.where(News.title.contains(keyword))

    result = await db.execute(query)
    return result.scalar_one()


# 更新新闻
async def update_news(db: AsyncSession, news_id: int, news_in: NewsUpdate) -> Optional[News]:
    """
    更新指定 ID 的新闻，仅更新传入的非 None 字段。

    Args:
        db: 异步数据库会话。
        news_id: 要更新的新闻 ID。
        news_in: 新闻更新请求数据。

    Returns:
        News 或 None: 更新后的新闻对象，不存在则返回 None。
    """
    db_obj = await get_news(db, news_id)
    if db_obj is None:
        return None

    update_data = news_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    await db.flush()
    await db.refresh(db_obj)
    return db_obj


# 删除新闻
async def delete_news(db: AsyncSession, news_id: int) -> bool:
    """
    删除指定 ID 的新闻。

    Args:
        db: 异步数据库会话。
        news_id: 要删除的新闻 ID。

    Returns:
        bool: 删除成功返回 True，不存在返回 False。
    """
    db_obj = await get_news(db, news_id)
    if db_obj is None:
        return False

    await db.delete(db_obj)
    await db.flush()
    return True
