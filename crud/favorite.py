from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# 检查收藏状态
async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """检查当前用户是否收藏了指定新闻。"""
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


# 添加收藏
async def add_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> Favorite:
    """为当前用户添加收藏记录。"""
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)
    return favorite


# 取消收藏
async def remove_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """删除当前用户对指定新闻的收藏记录，返回是否删除成功。"""
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


# 获取收藏列表（分页）
async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    """
    获取当前用户的收藏列表，联表查询新闻详情。

    Returns:
        (rows, total): rows 为 (News, favorite_time, favorite_id) 元组列表，total 为总数。
    """
    # 总数
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 联表查询
    offset = (page - 1) * page_size
    query = (
        select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 清空收藏
async def remove_all_favorites(db: AsyncSession, user_id: int) -> int:
    """清空当前用户的所有收藏记录，返回删除数量。"""
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount or 0
