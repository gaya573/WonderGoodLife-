"""
인증 API - 로그인, 회원가입, 토큰 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.infrastructure.database import get_db
from app.application.auth_service import AuthService, get_auth_service
from app.domain.entities import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


# ===== Request/Response Models =====

class LoginRequest(BaseModel):
    """로그인 요청 - 이메일과 비밀번호로 로그인"""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """회원가입 요청"""
    username: str  # 실제 이름 (최대 50글자)
    email: str     # 로그인 ID로 사용
    password: str
    phone_number: Optional[str] = None  # 전화번호 (선택)
    role: str = "USER"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    status: str
    created_at: str


# ===== Helper Functions =====

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """현재 로그인한 사용자 정보 조회"""
    try:
        token = credentials.credentials
        user = auth_service.get_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ===== API Endpoints =====

@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """사용자 로그인"""
    try:
        user = auth_service.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # JWT 토큰 생성
        access_token = auth_service.create_access_token(user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": user.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/register", response_model=UserResponse)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """새 사용자 회원가입"""
    try:
        # 사용자 생성 (이메일 중복 확인은 register_user 내부에서 처리)
        user = auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            phone_number=request.phone_number,
            role=request.role
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 로그인한 사용자 정보 조회"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        status=current_user.status,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):
    """사용자 로그아웃 (클라이언트에서 토큰 삭제)"""
    return {"message": "로그아웃되었습니다"}


@router.post("/refresh")
def refresh_token(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """토큰 갱신"""
    try:
        new_token = auth_service.create_access_token(current_user)
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            user={
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role,
                "status": current_user.status
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 갱신 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
def health_check():
    """인증 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "auth",
        "message": "인증 서비스가 정상 작동 중입니다"
    }