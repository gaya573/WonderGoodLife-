"""
권한 체크 데코레이터 및 서비스
"""
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import UserORM, RoleORM, PermissionORM, UserRoleORM, RolePermissionORM
from app.domain.entities import User, UserRole
from app.presentation.dependencies import get_current_user


def require_permission(resource: str, action: str):
    """
    권한 체크 데코레이터
    
    Args:
        resource: 리소스명 (예: 'user_management', 'staging_data')
        action: 액션명 (예: 'read', 'write', 'delete')
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # current_user와 db를 kwargs에서 찾기
            current_user = None
            db = None
            
            # 함수 시그니처에서 current_user와 db 찾기
            for key, value in kwargs.items():
                if key == 'current_user' and isinstance(value, User):
                    current_user = value
                elif key == 'db' and isinstance(value, Session):
                    db = value
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="인증이 필요합니다"
                )
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="데이터베이스 연결이 필요합니다"
                )
            
            # 권한 체크
            has_permission = check_user_permission(db, current_user, resource, action)
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"{resource}_{action} 권한이 필요합니다"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_user_permission(db: Session, user: User, resource: str, action: str) -> bool:
    """
    사용자의 특정 권한 체크
    
    Args:
        db: 데이터베이스 세션
        user: 사용자 객체
        resource: 리소스명
        action: 액션명
    
    Returns:
        bool: 권한 여부
    """
    try:
        # ADMIN은 모든 권한을 가짐
        if user.role == UserRole.ADMIN:
            return True
        
        # MANAGER, CEO 직급은 모든 권한을 가짐
        if user.position in ["MANAGER", "CEO"]:
            return True
        
        # 일반 사용자(USER)는 사용자 관리 권한을 가질 수 없음
        if user.role == UserRole.USER and resource == "user_management":
            return False
        
        # 사용자의 역할들 조회
        user_roles = db.query(UserRoleORM).filter(UserRoleORM.user_id == user.id).all()
        
        if not user_roles:
            return False
        
        # 각 역할의 권한 확인
        for user_role in user_roles:
            # 해당 리소스-액션 권한 조회
            permission = db.query(PermissionORM).filter(
                PermissionORM.resource == resource,
                PermissionORM.action == action
            ).first()
            
            if not permission:
                continue
            
            # 역할에 권한이 할당되어 있는지 확인
            role_permission = db.query(RolePermissionORM).filter(
                RolePermissionORM.role_id == user_role.role_id,
                RolePermissionORM.permission_id == permission.id
            ).first()
            
            if role_permission:
                return True
        
        return False
        
    except Exception as e:
        print(f"권한 체크 오류: {str(e)}")
        return False


def get_user_permissions(db: Session, user: User) -> list:
    """
    사용자의 모든 권한 조회
    
    Args:
        db: 데이터베이스 세션
        user: 사용자 객체
    
    Returns:
        list: 권한 리스트 [{"resource": "user_management", "action": "read"}, ...]
    """
    try:
        permissions = []
        
        # ADMIN은 모든 권한을 가짐
        if user.role == UserRole.ADMIN:
            all_permissions = db.query(PermissionORM).all()
            return [{"resource": p.resource, "action": p.action} for p in all_permissions]
        
        # MANAGER, CEO 직급은 모든 권한을 가짐
        if user.position in ["MANAGER", "CEO"]:
            all_permissions = db.query(PermissionORM).all()
            return [{"resource": p.resource, "action": p.action} for p in all_permissions]
        
        # 일반 사용자(USER)는 사용자 관리 권한 제외
        if user.role == UserRole.USER:
            all_permissions = db.query(PermissionORM).filter(
                PermissionORM.resource != "user_management"
            ).all()
            return [{"resource": p.resource, "action": p.action} for p in all_permissions]
        
        # 사용자의 역할들 조회
        user_roles = db.query(UserRoleORM).filter(UserRoleORM.user_id == user.id).all()
        
        for user_role in user_roles:
            # 역할별 권한 조회
            role_permissions = db.query(RolePermissionORM).filter(
                RolePermissionORM.role_id == user_role.role_id
            ).all()
            
            for role_permission in role_permissions:
                permission = db.query(PermissionORM).filter(
                    PermissionORM.id == role_permission.permission_id
                ).first()
                
                if permission:
                    permissions.append({
                        "resource": permission.resource,
                        "action": permission.action,
                        "description": permission.description
                    })
        
        return permissions
        
    except Exception as e:
        print(f"사용자 권한 조회 오류: {str(e)}")
        return []


# 권한 체크를 위한 의존성 함수
def check_permission_dependency(resource: str, action: str):
    """
    FastAPI 의존성으로 사용할 권한 체크 함수
    """
    def permission_checker(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        has_permission = check_user_permission(db, current_user, resource, action)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{resource}_{action} 권한이 필요합니다"
            )
        
        return current_user
    
    return permission_checker
