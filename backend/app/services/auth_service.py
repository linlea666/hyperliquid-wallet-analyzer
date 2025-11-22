"""
认证服务
处理用户认证、Token 生成、密码加密等
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from app.database import db
from app.models.user import User, UserRole, TokenData

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境需要更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    """认证服务"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """密码加密"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问 Token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """创建刷新 Token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """验证 Token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            if username is None:
                return None
            
            return TokenData(username=username, role=role)
        except JWTError as e:
            logger.error(f"Token 验证失败: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            user_data = db.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            
            if not user_data:
                return None
            
            return User(**user_data)
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = AuthService.get_user_by_username(username)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def create_user(username: str, password: str, role: UserRole = UserRole.VIEWER) -> Optional[User]:
        """创建用户"""
        try:
            # 检查用户名是否已存在
            existing = AuthService.get_user_by_username(username)
            if existing:
                logger.warning(f"用户名已存在: {username}")
                return None
            
            # 加密密码
            password_hash = AuthService.get_password_hash(password)
            
            # 插入数据库
            cursor = db.execute("""
                INSERT INTO users (username, password_hash, role, is_active, created_at, must_change_password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                password_hash,
                role.value,
                True,
                datetime.now().isoformat(),
                False
            ))
            
            user_id = cursor.lastrowid
            
            logger.info(f"创建用户成功: {username} (ID: {user_id})")
            
            return User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                role=role,
                is_active=True,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    @staticmethod
    def update_last_login(username: str):
        """更新最后登录时间"""
        try:
            db.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (datetime.now().isoformat(), username)
            )
        except Exception as e:
            logger.error(f"更新登录时间失败: {e}")
    
    @staticmethod
    def change_password(username: str, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            # 验证旧密码
            user = AuthService.authenticate_user(username, old_password)
            if not user:
                return False
            
            # 加密新密码
            new_password_hash = AuthService.get_password_hash(new_password)
            
            # 更新数据库
            db.execute("""
                UPDATE users 
                SET password_hash = ?, must_change_password = ?
                WHERE username = ?
            """, (new_password_hash, False, username))
            
            logger.info(f"用户修改密码成功: {username}")
            return True
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False
    
    @staticmethod
    def init_default_admin():
        """初始化默认管理员账户"""
        try:
            # 检查是否已存在 admin 用户
            admin = AuthService.get_user_by_username("admin")
            
            if not admin:
                # 创建默认管理员
                AuthService.create_user(
                    username="admin",
                    password="admin888",
                    role=UserRole.ADMIN
                )
                logger.info("✅ 默认管理员账户创建成功: admin / admin888")
            else:
                logger.info("ℹ️  管理员账户已存在")
        except Exception as e:
            logger.error(f"初始化管理员账户失败: {e}")


# 全局认证服务实例
auth_service = AuthService()

