"""
认证 API
处理登录、登出、Token 刷新、密码修改等
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from loguru import logger

from app.models.user import UserLogin, Token, ChangePassword, User, TokenData
from app.services.auth_service import (
    auth_service,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    token_data = auth_service.verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_username(token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


@router.post("/login", response_model=dict)
async def login(user_login: UserLogin):
    """
    用户登录
    
    - 验证用户名密码
    - 生成 Access Token 和 Refresh Token
    - 更新最后登录时间
    """
    try:
        # 认证用户
        user = auth_service.authenticate_user(user_login.username, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成 Token
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = auth_service.create_refresh_token(
            data={"sub": user.username, "role": user.role.value}
        )
        
        # 更新最后登录时间
        auth_service.update_last_login(user.username)
        
        logger.info(f"用户登录成功: {user.username}")
        
        return {
            "success": True,
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "must_change_password": user.must_change_password
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    - 前端需要清除本地存储的 Token
    - 后端记录登出日志
    """
    try:
        logger.info(f"用户登出: {current_user.username}")
        
        return {
            "success": True,
            "message": "登出成功"
        }
        
    except Exception as e:
        logger.error(f"登出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    刷新 Token
    
    - 使用 Refresh Token 获取新的 Access Token
    """
    try:
        token = credentials.credentials
        token_data = auth_service.verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Refresh Token",
            )
        
        # 生成新的 Access Token
        new_access_token = auth_service.create_access_token(
            data={"sub": token_data.username, "role": token_data.role},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "success": True,
            "message": "Token 刷新成功",
            "data": {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新 Token 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新 Token 失败: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    - 返回当前登录用户的详细信息
    """
    try:
        return {
            "success": True,
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value,
                "is_active": current_user.is_active,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
                "must_change_password": current_user.must_change_password
            }
        }
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user)
):
    """
    修改密码
    
    - 验证旧密码
    - 设置新密码
    """
    try:
        success = auth_service.change_password(
            current_user.username,
            password_data.old_password,
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        
        logger.info(f"用户修改密码成功: {current_user.username}")
        
        return {
            "success": True,
            "message": "密码修改成功，请重新登录"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )


# 导出依赖
__all__ = ["router", "get_current_user"]

