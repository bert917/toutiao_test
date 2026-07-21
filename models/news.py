from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class News(Base):
    """新闻表 ORM 模型，映射数据库 news 表。"""

    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title = Column(String(255), nullable=False, comment="新闻标题")
    description = Column(String(500), nullable=True, comment="新闻摘要")
    content = Column(Text, nullable=False, comment="新闻正文")
    image = Column(String(255), nullable=True, comment="封面图片URL")
    author = Column(String(50), nullable=True, comment="作者")
    category_id = Column(Integer, nullable=False, comment="分类ID")
    views = Column(Integer, nullable=False, default=0, comment="浏览量")
    publish_time = Column(DateTime, nullable=False, comment="发布时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
