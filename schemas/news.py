from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# 新闻创建请求模型
class NewsCreate(BaseModel):
    title: str = Field(..., max_length=255, description="新闻标题")
    description: Optional[str] = Field(None, max_length=500, description="新闻摘要")
    content: str = Field(..., description="新闻正文")
    image: Optional[str] = Field(None, max_length=255, description="封面图片URL")
    author: Optional[str] = Field(None, max_length=50, description="作者")
    category_id: int = Field(..., description="分类ID")
    views: int = Field(0, ge=0, description="浏览量")
    publish_time: datetime = Field(..., description="发布时间")


# 新闻更新请求模型
class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="新闻标题")
    description: Optional[str] = Field(None, max_length=500, description="新闻摘要")
    content: Optional[str] = Field(None, description="新闻正文")
    image: Optional[str] = Field(None, max_length=255, description="封面图片URL")
    author: Optional[str] = Field(None, max_length=50, description="作者")
    category_id: Optional[int] = Field(None, description="分类ID")
    views: Optional[int] = Field(None, ge=0, description="浏览量")
    publish_time: Optional[datetime] = Field(None, description="发布时间")


# 新闻响应模型
class NewsResponse(BaseModel):
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    description: Optional[str] = Field(None, description="新闻摘要")
    content: str = Field(..., description="新闻正文")
    image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, description="作者")
    category_id: int = Field(..., description="分类ID")
    views: int = Field(..., description="浏览量")
    publish_time: datetime = Field(..., description="发布时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


# 相关推荐项（轻量字段）
class RelatedNewsItem(BaseModel):
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    description: Optional[str] = Field(None, description="新闻摘要")
    image: Optional[str] = Field(None, description="封面图片URL")
    views: int = Field(..., description="浏览量")
    publish_time: datetime = Field(..., description="发布时间")

    model_config = {"from_attributes": True}
