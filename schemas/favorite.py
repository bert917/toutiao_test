from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# 收藏状态响应
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")


# 添加收藏请求
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 收藏列表中的新闻项
class FavoriteNewsItemResponse(BaseModel):
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    description: Optional[str] = Field(None, description="新闻摘要")
    image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, description="作者")
    category_id: int = Field(..., alias="categoryId", description="分类ID")
    views: int = Field(..., description="浏览量")
    publish_time: Optional[datetime] = Field(None, alias="publishTime", description="发布时间")
    favorite_id: int = Field(..., alias="favoriteId", description="收藏记录ID")
    favorite_time: datetime = Field(..., alias="favoriteTime", description="收藏时间")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# 收藏列表响应
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
