from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# 用户注册请求模型
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名（3~50字符）")
    password: str = Field(..., min_length=6, max_length=50, description="密码（6~50字符）")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")


# 用户登录请求模型
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# 用户基本信息
class UserInfoItem(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")

    model_config = {"from_attributes": True}


# 注册成功响应
class RegisterResponse(BaseModel):
    token: str = Field(..., description="访问令牌")
    userInfo: UserInfoItem = Field(..., description="用户信息")


# 用户信息响应模型
class UserInfoResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")
    created_at: datetime = Field(..., description="注册时间")

    model_config = {"from_attributes": True}


# 用户更新请求模型
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, max_length=255, description="个人简介")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")


# 修改密码请求模型
class PasswordUpdate(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=50, alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, alias="newPassword", description="新密码")

    model_config = {"populate_by_name": True}
