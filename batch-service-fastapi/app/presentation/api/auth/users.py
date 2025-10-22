"""
사용자 관리 API - 사용자 CRUD 및 권한 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.infrastructure.database import get_db
from app.application.auth_service import AuthService, get_auth_service
from app.application.permission_service import get_permission_service
from app.domain.entities import User, UserRole, UserStatus, UserPosition
from app.presentation.dependencies import get_current_user
from app.presentation.permission_checker import check_permission_dependency

router = APIRouter(prefix="/api/users", tags=["users"])


# ===== Request/Response Models =====

class UserCreateRequest(BaseModel):
    """사용자 생성 요청"""
    username: str
    email: str
    password: str
    phone_number: Optional[str] = None
    role: str = "USER"
    position: str = "EMPLOYEE"
    status: str = "ACTIVE"


class UserUpdateRequest(BaseModel):
    """사용자 수정 요청"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # 비밀번호 필드 추가
    phone_number: Optional[str] = None
    role: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    """사용자 응답"""
    id: int
    username: str
    email: str
    phone_number: Optional[str]
    role: str
    position: str
    status: str
    created_at: str
    updated_at: Optional[str]


class UserListResponse(BaseModel):
    """사용자 목록 응답"""
    items: List[UserResponse]
    total_count: int
    skip: int
    limit: int
    has_more: bool


# ===== API Endpoints =====

@router.get("/", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="검색어 (사용자명 또는 이메일)"),
    role: Optional[str] = Query(None, description="역할 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission_dependency("user_management", "read"))
):
    """사용자 목록 조회 (검색 및 필터 지원)"""
    try:
        from app.infrastructure.orm_models import UserORM
        
        # 쿼리 빌드
        query = db.query(UserORM)
        
        # 검색 조건 추가
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (UserORM.username.like(search_term)) |
                (UserORM.email.like(search_term))
            )
        
        # 역할 필터 추가
        if role:
            query = query.filter(UserORM.role == role)
        
        # 상태 필터 추가
        if status:
            query = query.filter(UserORM.status == status)
        
        # 총 개수 조회
        total_count = query.count()
        
        # 페이지네이션 적용
        users = query.offset(skip).limit(limit).all()
        
        # 응답 데이터 구성
        user_items = []
        for user in users:
            user_items.append(UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                phone_number=user.phone_number,
                role=user.role,
                position=user.position,
                status=user.status,
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            ))
        
        return UserListResponse(
            items=user_items,
            total_count=total_count,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 목록 조회 실패: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission_dependency("user_management", "read"))
):
    """사용자 상세 조회"""
    try:
        from app.infrastructure.orm_models import UserORM
        
        # 권한 확인 - current_user는 이미 인증된 User 객체
        if not current_user or (current_user.role != UserRole.ADMIN and current_user.id != user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )
        
        user = db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            position=user.position.value if hasattr(user.position, 'value') else user.position,
            status=user.status.value if hasattr(user.status, 'value') else user.status,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 조회 실패: {str(e)}")


@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission_dependency("user_management", "write"))
):
    """새 사용자 생성"""
    try:
        # 사용자 생성
        created_user = auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            phone_number=user_data.phone_number,
            role=user_data.role
        )
        
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            phone_number=created_user.phone_number,
            role=created_user.role.value if hasattr(created_user.role, 'value') else created_user.role,
            position=created_user.position.value if hasattr(created_user.position, 'value') else created_user.position,
            status=created_user.status.value if hasattr(created_user.status, 'value') else created_user.status,
            created_at=created_user.created_at.isoformat() if created_user.created_at else None,
            updated_at=created_user.updated_at.isoformat() if created_user.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 생성 실패: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 정보 수정"""
    try:
        from app.infrastructure.orm_models import UserORM
        
        # 권한 확인 - current_user는 이미 인증된 사용자 정보
        if not current_user or (current_user.role != UserRole.ADMIN and current_user.id != user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )
        
        # 사용자 조회
        user = db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 정보 업데이트
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.password is not None:
            # 비밀번호 해시화
            user.password_hash = User.hash_password(user_data.password)
        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.position is not None:
            user.position = user_data.position
        if user_data.status is not None:
            user.status = user_data.status
        
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role,
            position=user.position,
            status=user.status,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"사용자 수정 실패: {str(e)}")


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 삭제"""
    try:
        from app.infrastructure.orm_models import UserORM
        
        # 권한 확인 - current_user는 User 객체
        if not current_user or current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="관리자 권한이 필요합니다"
            )
        
        # 자기 자신 삭제 방지
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자기 자신은 삭제할 수 없습니다"
            )
        
        # 사용자 조회
        user = db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 사용자 삭제
        db.delete(user)
        db.commit()
        
        return {
            "success": True,
            "message": "사용자가 성공적으로 삭제되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"사용자 삭제 실패: {str(e)}")


@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """내 프로필 조회"""
    try:
        # current_user는 이미 인증된 User 객체
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 정보를 찾을 수 없습니다"
            )
        
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            phone_number=current_user.phone_number,
            role=current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
            position=current_user.position.value if hasattr(current_user.position, 'value') else current_user.position,
            status=current_user.status.value if hasattr(current_user.status, 'value') else current_user.status,
            created_at=current_user.created_at.isoformat() if current_user.created_at else None,
            updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 실패: {str(e)}")
