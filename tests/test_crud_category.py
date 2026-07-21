import pytest
from sqlalchemy import insert

from crud.news_category import get_categories
from models.news_category import NewsCategory


@pytest.mark.asyncio
async def test_get_categories_empty(db_session):
    """测试空表时返回空列表。"""
    result = await get_categories(db_session)
    assert result == []


@pytest.mark.asyncio
async def test_get_categories_ordered(db_session):
    """测试分类按 sort_order 升序返回。"""
    await db_session.execute(
        insert(NewsCategory),
        [
            {"name": "国际", "sort_order": 4},
            {"name": "头条", "sort_order": 1},
            {"name": "体育", "sort_order": 3},
            {"name": "社会", "sort_order": 2},
        ],
    )
    await db_session.flush()

    result = await get_categories(db_session)
    assert len(result) == 4
    assert [c.name for c in result] == ["头条", "社会", "体育", "国际"]
    assert [c.sort_order for c in result] == [1, 2, 3, 4]
