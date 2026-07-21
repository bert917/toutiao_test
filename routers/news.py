from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from config.db_conf import get_db
from crud.news_category import get_categories as fetch_categories
from crud.news import get_news_list, get_news_count, get_news, increment_views, get_related_news
from schemas.news_category import NewsCategoryResponse
from schemas.news import NewsResponse
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories", response_model=ResponseModel)
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有新闻分类列表，按排序序号升序返回。"""
    categories = await fetch_categories(db)
    data = [NewsCategoryResponse.model_validate(c).model_dump() for c in categories]
    return ResponseModel(code=200, message="success", data=data)


@router.get("/list", response_model=ResponseModel)
async def list_news(
    categoryId: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询新闻列表，支持按分类过滤。"""
    skip = (page - 1) * pageSize
    news_list = await get_news_list(db, skip=skip, limit=pageSize, category_id=categoryId)
    total = await get_news_count(db, category_id=categoryId)
    data = {
        "list": [NewsResponse.model_validate(n).model_dump() for n in news_list],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }
    return ResponseModel(code=200, message="success", data=data)


@router.get("/detail", response_model=ResponseModel)
async def news_detail(
    id: int = Query(..., description="新闻ID"),
    db: AsyncSession = Depends(get_db),
):
    """根据 ID 获取新闻详情，同时浏览量 +1，并返回同分类相关推荐。"""
    news = await increment_views(db, id)
    if news is None:
        return ResponseModel(code=404, message="新闻不存在", data=None)
    related = await get_related_news(db, category_id=news.category_id, exclude_id=news.id)
    data = NewsResponse.model_validate(news).model_dump()
    data["relatedNews"] = related
    return ResponseModel(code=200, message="success", data=data)
