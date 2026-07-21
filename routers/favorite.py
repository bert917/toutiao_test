from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.user import get_current_user
from crud import favorite
from models.user import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """检查当前用户是否收藏了指定新闻。"""
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    return ResponseModel(
        message="检查收藏状态成功",
        data=FavoriteCheckResponse(isFavorite=is_favorited).model_dump(by_alias=True),
    )


@router.post("/add")
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加收藏。"""
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return ResponseModel(message="添加收藏成功", data={"favoriteId": result.id})


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏。"""
    removed = await favorite.remove_news_favorite(db, user.id, news_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return ResponseModel(message="取消收藏成功")


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取收藏列表（分页）。"""
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id,
        }
        for news, favorite_time, favorite_id in rows
    ]
    has_more = total > page * page_size

    data = FavoriteListResponse(
        list=favorite_list,
        total=total,
        hasMore=has_more,
    ).model_dump(by_alias=True)

    return ResponseModel(message="获取收藏列表成功", data=data)


@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清空所有收藏。"""
    count = await favorite.remove_all_favorites(db, user.id)
    return ResponseModel(message=f"清空了{count}条收藏记录")
