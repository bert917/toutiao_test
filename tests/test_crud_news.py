import pytest
from datetime import datetime

from crud.news import (
    create_news,
    get_news,
    increment_views,
    get_news_list,
    get_news_count,
    update_news,
    delete_news,
)
from schemas.news import NewsCreate, NewsUpdate


# 构造测试数据
def _make_news_create(title: str = "测试新闻", category_id: int = 1) -> NewsCreate:
    return NewsCreate(
        title=title,
        description="测试摘要",
        content="测试正文内容",
        image="https://example.com/img.jpg",
        author="测试作者",
        category_id=category_id,
        views=0,
        publish_time=datetime(2024, 6, 1, 12, 0),
    )


@pytest.mark.asyncio
async def test_create_news(db_session):
    """测试创建新闻。"""
    news_in = _make_news_create()
    result = await create_news(db_session, news_in)
    assert result.id is not None
    assert result.title == "测试新闻"
    assert result.category_id == 1


@pytest.mark.asyncio
async def test_get_news_exists(db_session):
    """测试根据 ID 获取存在的新闻。"""
    news_in = _make_news_create()
    created = await create_news(db_session, news_in)
    result = await get_news(db_session, created.id)
    assert result is not None
    assert result.id == created.id
    assert result.title == "测试新闻"


@pytest.mark.asyncio
async def test_get_news_not_exists(db_session):
    """测试根据 ID 获取不存在的新闻返回 None。"""
    result = await get_news(db_session, 9999)
    assert result is None


@pytest.mark.asyncio
async def test_increment_views(db_session):
    """测试浏览量 +1。"""
    news_in = _make_news_create()
    created = await create_news(db_session, news_in)
    assert created.views == 0

    updated = await increment_views(db_session, created.id)
    assert updated is not None
    assert updated.views == 1

    updated2 = await increment_views(db_session, created.id)
    assert updated2.views == 2


@pytest.mark.asyncio
async def test_increment_views_not_exists(db_session):
    """测试不存在的新闻增加浏览量返回 None。"""
    result = await increment_views(db_session, 9999)
    assert result is None


@pytest.mark.asyncio
async def test_get_news_list_no_filter(db_session):
    """测试无过滤条件分页查询。"""
    for i in range(5):
        await create_news(db_session, _make_news_create(title=f"新闻{i}"))

    result = await get_news_list(db_session, skip=0, limit=3)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_news_list_by_category(db_session):
    """测试按分类过滤。"""
    await create_news(db_session, _make_news_create(title="分类1新闻", category_id=1))
    await create_news(db_session, _make_news_create(title="分类2新闻", category_id=2))
    await create_news(db_session, _make_news_create(title="分类1新闻2", category_id=1))

    result = await get_news_list(db_session, category_id=1)
    assert len(result) == 2
    assert all(n.category_id == 1 for n in result)


@pytest.mark.asyncio
async def test_get_news_list_by_keyword(db_session):
    """测试按关键词过滤。"""
    await create_news(db_session, _make_news_create(title="苹果发布会"))
    await create_news(db_session, _make_news_create(title="华为新品"))
    await create_news(db_session, _make_news_create(title="苹果股价"))

    result = await get_news_list(db_session, keyword="苹果")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_news_count(db_session):
    """测试获取新闻总数。"""
    for i in range(3):
        await create_news(db_session, _make_news_create(title=f"新闻{i}"))

    count = await get_news_count(db_session)
    assert count == 3


@pytest.mark.asyncio
async def test_get_news_count_by_category(db_session):
    """测试按分类获取新闻总数。"""
    await create_news(db_session, _make_news_create(category_id=1))
    await create_news(db_session, _make_news_create(category_id=2))
    await create_news(db_session, _make_news_create(category_id=1))

    count = await get_news_count(db_session, category_id=1)
    assert count == 2


@pytest.mark.asyncio
async def test_update_news(db_session):
    """测试更新新闻。"""
    created = await create_news(db_session, _make_news_create())
    update_in = NewsUpdate(title="更新后的标题", views=100)
    result = await update_news(db_session, created.id, update_in)
    assert result is not None
    assert result.title == "更新后的标题"
    assert result.views == 100


@pytest.mark.asyncio
async def test_update_news_not_exists(db_session):
    """测试更新不存在的新闻返回 None。"""
    update_in = NewsUpdate(title="不存在")
    result = await update_news(db_session, 9999, update_in)
    assert result is None


@pytest.mark.asyncio
async def test_delete_news(db_session):
    """测试删除新闻。"""
    created = await create_news(db_session, _make_news_create())
    result = await delete_news(db_session, created.id)
    assert result is True

    # 确认已删除
    fetched = await get_news(db_session, created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_news_not_exists(db_session):
    """测试删除不存在的新闻返回 False。"""
    result = await delete_news(db_session, 9999)
    assert result is False
