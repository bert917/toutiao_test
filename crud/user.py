import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from config.db_conf import get_db
from models.user import User
from models.user_token import UserToken
from schemas.user import UserRegister, UserUpdate, PasswordUpdate

# Token 有效期（7 天）
TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配。"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_token() -> str:
    """生成 UUID4 Token。"""
    return str(uuid.uuid4())


def get_token_expire_time() -> datetime:
    """计算 Token 过期时间（当前时间 + TOKEN_EXPIRE_DAYS 天）。"""
    return datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)


# 根据用户名查询用户
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名查询用户是否存在。

    Args:
        db: 异步数据库会话。
        username: 用户名。

    Returns:
        User 或 None: 查到的用户对象，不存在则返回 None。
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_in: UserRegister) -> User:
    """
    创建新用户，密码加密存储。

    Args:
        db: 异步数据库会话。
        user_in: 用户注册请求数据。

    Returns:
        User: 新创建的用户对象。
    """
    db_obj = User(
        username=user_in.username,
        password=hash_password(user_in.password),
        nickname=user_in.nickname or "",
        avatar=user_in.avatar or "",
    )
    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj)
    return db_obj


# 查询用户的 Token
async def get_user_token(db: AsyncSession, user_id: int) -> Optional[UserToken]:
    """
    查询指定用户的 Token 记录。

    Args:
        db: 异步数据库会话。
        user_id: 用户 ID。

    Returns:
        UserToken 或 None: 查到的 Token 对象，不存在则返回 None。
    """
    result = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    return result.scalar_one_or_none()


# 创建或更新 Token
async def upsert_token(db: AsyncSession, user_id: int) -> UserToken:
    """
    为用户生成新 Token：若已有记录则更新，否则新增。

    Args:
        db: 异步数据库会话。
        user_id: 用户 ID。

    Returns:
        UserToken: 更新或新建的 Token 对象。
    """
    token = generate_token()
    expire_time = get_token_expire_time()

    existing = await get_user_token(db, user_id)

    if existing:
        # 已有 Token，更新
        existing.token = token
        existing.expires_at = expire_time
        await db.flush()
        await db.refresh(existing)
        return existing
    else:
        # 没有 Token，新增
        db_obj = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expire_time,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


# 根据 Token 查询用户（校验有效性 + 过期时间）
async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    """
    根据 Token 查询对应用户。
    校验 Token 是否存在且未过期，通过则返回用户对象，否则返回 None。
    """
    result = await db.execute(select(UserToken).where(UserToken.token == token))
    token_obj = result.scalar_one_or_none()
    if token_obj is None:
        return None
    # 检查是否过期（DB 存储的是 naive UTC 时间）
    expires = token_obj.expires_at.replace(tzinfo=timezone.utc) if token_obj.expires_at.tzinfo is None else token_obj.expires_at
    if expires < datetime.now(timezone.utc):
        return None
    # 查询用户
    user_result = await db.execute(select(User).where(User.id == token_obj.user_id))
    return user_result.scalar_one_or_none()


# 更新用户信息
async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    """
    更新用户信息（仅更新非 None 字段）。

    Args:
        db: 异步数据库会话。
        user: 当前用户对象。
        user_in: 用户更新请求数据。

    Returns:
        User: 更新后的用户对象。
    """
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


# 修改密码
async def change_password(db: AsyncSession, user: User, password_in: PasswordUpdate) -> bool:
    """
    修改用户密码。

    Args:
        db: 异步数据库会话。
        user: 当前用户对象。
        password_in: 修改密码请求数据。

    Returns:
        bool: 修改成功返回 True，旧密码验证失败返回 False。
    """
    # 验证旧密码
    if not verify_password(password_in.old_password, user.password):
        return False
    # 更新密码
    user.password = hash_password(password_in.new_password)
    await db.flush()
    await db.refresh(user)
    return True


# Token 认证依赖
async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    依赖注入：从请求头 Authorization: Bearer <token> 中提取 Token，
    校验有效性并返回当前用户。Token 无效或过期时抛出 401。
    """
    token = authorization.replace("Bearer ", "")
    user = await get_user_by_token(db, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    return user
