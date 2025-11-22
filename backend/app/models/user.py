"""
用户模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"          # 管理员
    OPERATOR = "operator"    # 操作员
    VIEWER = "viewer"        # 访客


class User(BaseModel):
    """用户模型"""
    id: Optional[int] = None
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    must_change_password: bool = False  # 首次登录强制修改密码
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """更新用户请求"""
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class ChangePassword(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class TokenData(BaseModel):
    """Token 数据"""
    username: Optional[str] = None
    role: Optional[str] = None

