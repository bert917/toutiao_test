from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.user import get_user_by_username, create_user, upsert_token, get_current_user, verify_password, update_user, change_password
from models.user import User
from schemas.user import UserRegister, UserLogin, RegisterResponse, UserInfoItem, UserInfoResponse, UserUpdate, PasswordUpdate
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", response_model=ResponseModel)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    用户注册接口。

    流程：
    1. 验证用户名是否已存在
    2. 创建用户（密码 bcrypt 加密）
    3. 生成 Token（7 天有效期）
    4. 查询数据库：有 Token 则更新，无 Token 则新增
    5. 返回用户信息及 Token
    """
    # 1. 验证用户是否已存在
    existing = await get_user_by_username(db, user_in.username)
    if existing:
        return ResponseModel(code=400, message="用户名已存在", data=None)

    # 2. 创建用户
    user = await create_user(db, user_in)

    # 3 & 4. 生成/更新 Token
    token_obj = await upsert_token(db, user.id)

    # 5. 返回结果
    data = RegisterResponse(
        token=token_obj.token,
        userInfo=UserInfoItem(
            id=user.id,
            username=user.username,
            bio=None,
            avatar=user.avatar,
        ),
    ).model_dump()

    return ResponseModel(code=200, message="注册成功", data=data)


@router.post("/login", response_model=ResponseModel)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录接口。

    流程：
    1. 根据用户名查询用户
    2. 校验密码
    3. 生成/更新 Token
    4. 返回用户信息及 Token
    """
    # 1. 查询用户
    user = await get_user_by_username(db, user_in.username)
    if not user:
        return ResponseModel(code=401, message="用户名或密码错误", data=None)

    # 2. 校验密码
    if not verify_password(user_in.password, user.password):
        return ResponseModel(code=401, message="用户名或密码错误", data=None)

    # 3. 生成/更新 Token
    token_obj = await upsert_token(db, user.id)

    # 4. 返回结果
    data = RegisterResponse(
        token=token_obj.token,
        userInfo=UserInfoItem(
            id=user.id,
            username=user.username,
            bio=None,
            avatar=user.avatar,
        ),
    ).model_dump()

    return ResponseModel(code=200, message="登录成功", data=data)


# 查Token查用户 → 封装crud → 功能整合成一个工具函数 → 路由导入使用: 依赖注入
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return ResponseModel(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(
    user_in: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新用户信息接口（需登录）。

    流程：
    1. 校验 Token 获取当前用户
    2. 更新用户信息（仅更新传入的字段）
    3. 返回更新后的用户信息
    """
    updated_user = await update_user(db, user, user_in)
    return ResponseModel(
        message="更新成功",
        data=UserInfoResponse.model_validate(updated_user),
    )


@router.put("/password")
async def update_password(
    password_in: PasswordUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    修改密码接口（需登录）。

    流程：
    1. 校验 Token 获取当前用户
    2. 验证旧密码
    3. 更新为新密码（bcrypt 加密）
    """
    success = await change_password(db, user, password_in)
    if not success:
        return ResponseModel(code=400, message="旧密码错误", data=None)
    return ResponseModel(code=200, message="密码修改成功", data=None)
