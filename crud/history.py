from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


# 添加历史记录
async def add_history(db: AsyncSession, user_id: int, news_id: int) -> History:
    """
    添加浏览历史记录。
    若已存在同一用户+新闻的记录，则更新浏览时间；否则新增。
    """
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # 已存在，更新浏览时间
        from sqlalchemy import func as sa_func
        existing.view_time = sa_func.now()
        await db.flush()
        await db.refresh(existing)
        return existing
    else:
        # 不存在，新增
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.flush()
        await db.refresh(history)
        return history


# 获取历史记录列表（分页）
async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    """
    获取当前用户的浏览历史列表，联表查询新闻详情。

    Returns:
        (rows, total): rows 为 (News, view_time, history_id) 元组列表，total 为总数。
    """
    # 总数
    count_query = select(func.count(History.id)).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 联表查询
    offset = (page - 1) * page_size
    query = (
        select(News, History.view_time.label("view_time"), History.id.label("history_id"))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 删除单条历史记录
async def delete_history(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """删除指定历史记录（按用户ID+新闻ID），返回是否删除成功。"""
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


# 清空历史记录
async def clear_history(db: AsyncSession, user_id: int) -> int:
    """清空当前用户的所有浏览历史，返回删除数量。"""
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount or 0
