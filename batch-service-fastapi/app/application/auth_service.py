"""
인증 서비스 - JWT 토큰 관리
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status
from ..domain.entities import User
from ..infrastructure.repositories import SQLAlchemyUserRepository
from ..infrastructure.database import SessionLocal
from ..config import settings


class AuthService:
    """인증 서비스"""
    
    def __init__(self, user_repo: SQLAlchemyUserRepository):
        self.user_repo = user_repo
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 1440  # 24시간 (하루)
    
    def create_access_token(self, user: User) -> str:
        """액세스 토큰 생성"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[User]:
        """토큰 검증 및 사용자 반환"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            user_id = int(payload.get("sub"))
            if user_id is None:
                return None
            
            user = self.user_repo.find_by_id(user_id)
            if user is None:
                return None
            
            # 사용자 활성화 상태 확인
            if not user.is_active():
                return None
            
            return user
        except jwt.PyJWTError:
            return None
        except Exception:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """토큰에서 현재 사용자 반환"""
        return self.verify_token(token)
    
    def get_current_active_user(self, token: str) -> Optional[User]:
        """토큰에서 활성 사용자 반환"""
        user = self.verify_token(token)
        if user and user.is_active():
            return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """사용자 인증 (이메일 기반)"""
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        if not user.verify_password(password):
            return None
        if not user.is_active():
            return None
        return user
    
    def register_user(self, username: str, email: str, password: str, phone_number: Optional[str] = None, role: str = "USER") -> User:
        """사용자 회원가입 - 이메일로 로그인, username은 실제 이름 (중복 가능)"""
        # 이메일 중복 확인 (로그인 ID - 중복 불가)
        if self.user_repo.find_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다"
            )
        

        # 사용자 생성
        from ..domain.entities import UserRole
        password_hash = User.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            phone_number=phone_number,
            role=UserRole(role)
        )
        user.validate()
        
        return self.user_repo.save(user)


def get_auth_service():
    """인증 서비스 의존성 주입"""
    db = SessionLocal()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        return AuthService(user_repo)
    finally:
        db.close()
