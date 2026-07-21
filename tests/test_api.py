import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from config.db_conf import get_db
from models.news import News
from models.news_category import NewsCategory
from tests.conftest import TestSessionLocal, test_engine, Base
from datetime import datetime


@pytest_asyncio.fixture
async def client():
    """提供使用测试数据库的异步 HTTP 客户端。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _insert_news(session: AsyncSession, **kwargs):
    """辅助函数：插入一条新闻并立即提交。"""
    defaults = dict(
        title="测试新闻", content="正文", category_id=1,
        views=0, publish_time=datetime(2024, 1, 1),
        created_at=datetime.now(), updated_at=datetime.now(),
    )
    defaults.update(kwargs)
    session.add(News(**defaults))
    await session.commit()


# ---- 基础路由测试 ----

@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """测试根路由。"""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_say_hello(client: AsyncClient):
    """测试 hello 路由。"""
    resp = await client.get("/hello/FastAPI")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello FastAPI"}


# ---- 分类接口测试 ----

@pytest.mark.asyncio
async def test_get_categories_empty(client: AsyncClient):
    """测试无分类数据时返回空列表。"""
    resp = await client.get("/api/news/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"] == []


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    """测试返回分类列表。"""
    async with TestSessionLocal() as session:
        await session.execute(
            insert(NewsCategory),
            [
                {"name": "头条", "sort_order": 1},
                {"name": "体育", "sort_order": 2},
            ],
        )
        await session.commit()

    resp = await client.get("/api/news/categories")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert data[0]["name"] == "头条"


# ---- 新闻列表接口测试 ----

@pytest.mark.asyncio
async def test_list_news_empty(client: AsyncClient):
    """测试空数据时列表接口。"""
    resp = await client.get("/api/news/list")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["list"] == []
    assert data["data"]["total"] == 0


@pytest.mark.asyncio
async def test_list_news_with_data(client: AsyncClient):
    """测试带数据的列表接口。"""
    async with TestSessionLocal() as session:
        for i in range(5):
            await _insert_news(session, title=f"新闻{i}")

    resp = await client.get("/api/news/list?page=1&pageSize=3")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["list"]) == 3
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["pageSize"] == 3


@pytest.mark.asyncio
async def test_list_news_by_category(client: AsyncClient):
    """测试按分类过滤列表。"""
    async with TestSessionLocal() as session:
        await _insert_news(session, title="分类1", category_id=1)
        await _insert_news(session, title="分类2", category_id=2)

    resp = await client.get("/api/news/list?categoryId=1")
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["list"][0]["category_id"] == 1


# ---- 新闻详情接口测试 ----

@pytest.mark.asyncio
async def test_detail_not_found(client: AsyncClient):
    """测试获取不存在的新闻返回 404。"""
    resp = await client.get("/api/news/detail?id=9999")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 404
    assert data["message"] == "新闻不存在"


@pytest.mark.asyncio
async def test_detail_success(client: AsyncClient):
    """测试获取新闻详情成功，浏览量 +1。"""
    async with TestSessionLocal() as session:
        await _insert_news(session, title="详情测试", views=10)

    resp = await client.get("/api/news/detail?id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "详情测试"
    assert data["data"]["views"] == 11


@pytest.mark.asyncio
async def test_detail_increments_views(client: AsyncClient):
    """测试每次访问详情浏览量递增。"""
    async with TestSessionLocal() as session:
        await _insert_news(session, title="浏览量测试", views=0)

    resp1 = await client.get("/api/news/detail?id=1")
    assert resp1.status_code == 200
    assert resp1.json()["data"]["views"] == 1

    resp2 = await client.get("/api/news/detail?id=1")
    assert resp2.status_code == 200
    assert resp2.json()["data"]["views"] == 2
