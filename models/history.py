from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase

from models.user import User
from models.news import News


class Base(DeclarativeBase):
    pass


class History(Base):
    """浏览历史表 ORM 模型，映射数据库 history 表。"""

    __tablename__ = "history"

    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        Index("idx_view_time", "view_time"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="历史ID")
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id = Column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    view_time = Column(DateTime, nullable=False, server_default=func.now(), comment="浏览时间")
