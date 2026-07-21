from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.user import get_current_user
from crud import history
from models.user import User
from schemas.history import HistoryAddRequest, HistoryNewsItemResponse, HistoryListResponse
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加浏览历史记录。"""
    result = await history.add_history(db, user.id, data.news_id)
    return ResponseModel(message="添加成功", data={"historyId": result.id})


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取浏览历史列表（分页）。"""
    rows, total = await history.get_history_list(db, user.id, page, page_size)

    has_more = total > page * page_size

    history_list = [
        HistoryNewsItemResponse.model_validate(
            {
                **news.__dict__,
                "view_time": view_time,
                "history_id": history_id,
            }
        )
        for news, view_time, history_id in rows
    ]

    data = HistoryListResponse(
        list=history_list,
        total=total,
        hasMore=has_more,
    ).model_dump(by_alias=True)

    return ResponseModel(message="获取历史列表成功", data=data)


@router.delete("/delete/{news_id}")
async def delete_history(
    news_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除单条浏览历史（按新闻ID）。"""
    deleted = await history.delete_history(db, user.id, news_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return ResponseModel(message="删除成功")


@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清空所有浏览历史。"""
    count = await history.clear_history(db, user.id)
    return ResponseModel(message=f"清空了{count}条历史记录")
