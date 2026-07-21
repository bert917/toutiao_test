from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import DeclarativeBase

from models.user import User
from models.news import News


class Base(DeclarativeBase):
    pass


class Favorite(Base):
    """收藏表 ORM 模型，映射数据库 favorite 表。"""

    __tablename__ = "favorite"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id = Column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="收藏时间")
