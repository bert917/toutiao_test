from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from models.user import Base


class UserToken(Base):
    """用户 Token 表 ORM 模型，映射数据库 user_token 表。"""

    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Token记录ID")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True, comment="用户ID")
    token = Column(String(255), nullable=False, unique=True, comment="访问令牌")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
