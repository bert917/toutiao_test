from sqlalchemy import Column, Integer, String, DateTime, func

from models.news import Base


class NewsCategory(Base):
    """新闻分类表 ORM 模型，映射数据库 news_category 表。"""

    __tablename__ = "news_category"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    sort_order = Column(Integer, nullable=False, default=0, comment="排序序号")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
