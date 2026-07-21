from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# 添加历史记录请求
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 历史记录列表中的新闻项
class HistoryNewsItemResponse(BaseModel):
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    description: Optional[str] = Field(None, description="新闻摘要")
    image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, description="作者")
    category_id: int = Field(..., alias="categoryId", description="分类ID")
    views: int = Field(..., description="浏览量")
    publish_time: Optional[datetime] = Field(None, alias="publishTime", description="发布时间")
    history_id: int = Field(..., alias="historyId", description="历史记录ID")
    view_time: datetime = Field(..., alias="viewTime", description="浏览时间")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# 历史记录列表响应
class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
