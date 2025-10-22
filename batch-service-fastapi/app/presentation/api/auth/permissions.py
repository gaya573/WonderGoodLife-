"""
권한 관리 API - 역할, 권한, 사용자-역할 연결 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import (
    UserORM, RoleORM, PermissionORM, UserRoleORM, RolePermissionORM
)
from app.domain.entities import User, UserRole, UserStatus, UserPosition
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/permissions", tags=["permissions"])

# ===== Request/Response Models =====

class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False

class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_system_role: bool
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PermissionCreateRequest(BaseModel):
    resource: str
    action: str
    description: Optional[str] = None

class PermissionUpdateRequest(BaseModel):
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    id: int
    resource: str
    action: str
    description: Optional[str] = None

class UserRoleAssignmentRequest(BaseModel):
    user_id: int
    role_id: int

class RolePermissionAssignmentRequest(BaseModel):
    role_id: int
    permission_id: int

class PermissionMatrixResponse(BaseModel):
    roles: List[RoleResponse]
    permissions: List[PermissionResponse]
    matrix: dict  # {role_id: {permission_id: bool}}

# ===== 역할 관리 API =====

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="역할명 검색"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """역할 목록 조회"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    query = db.query(RoleORM)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(RoleORM.name.like(search_term))
    
    roles = query.offset(skip).limit(limit).all()
    
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            created_by=role.created_by,
            created_at=role.created_at,
            updated_at=role.updated_at
        ) for role in roles
    ]


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 역할 생성"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 역할명 중복 확인
    existing_role = db.query(RoleORM).filter(RoleORM.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 역할명입니다"
        )
    
    new_role = RoleORM(
        name=role_data.name,
        description=role_data.description,
        is_system_role=role_data.is_system_role,
        created_by=current_user.id
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleResponse(
        id=new_role.id,
        name=new_role.name,
        description=new_role.description,
        is_system_role=new_role.is_system_role,
        created_by=new_role.created_by,
        created_at=new_role.created_at,
        updated_at=new_role.updated_at
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 역할 조회"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        created_by=role.created_by,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """역할 수정"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    
    # 시스템 역할은 수정 불가
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시스템 역할은 수정할 수 없습니다"
        )
    
    # 역할명 중복 확인 (자기 자신 제외)
    if role_data.name and role_data.name != role.name:
        existing_role = db.query(RoleORM).filter(
            RoleORM.name == role_data.name,
            RoleORM.id != role_id
        ).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 역할명입니다"
            )
    
    # 업데이트
    if role_data.name:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    
    db.commit()
    db.refresh(role)
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        created_by=role.created_by,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """역할 삭제"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    
    # 시스템 역할은 삭제 불가
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시스템 역할은 삭제할 수 없습니다"
        )
    
    # 사용자에게 할당된 역할이 있는지 확인
    user_roles = db.query(UserRoleORM).filter(UserRoleORM.role_id == role_id).count()
    if user_roles > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자에게 할당된 역할은 삭제할 수 없습니다"
        )
    
    db.delete(role)
    db.commit()
    
    return {"message": "역할이 성공적으로 삭제되었습니다"}


# ===== 권한 관리 API =====

@router.get("/permissions", response_model=List[PermissionResponse])
def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource: Optional[str] = Query(None, description="리소스 필터"),
    action: Optional[str] = Query(None, description="액션 필터"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """권한 목록 조회"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    query = db.query(PermissionORM)
    
    if resource:
        query = query.filter(PermissionORM.resource == resource)
    if action:
        query = query.filter(PermissionORM.action == action)
    
    permissions = query.offset(skip).limit(limit).all()
    
    return [
        PermissionResponse(
            id=permission.id,
            resource=permission.resource,
            action=permission.action,
            description=permission.description
        ) for permission in permissions
    ]


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 권한 생성"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 권한 중복 확인 (리소스 + 액션)
    existing_permission = db.query(PermissionORM).filter(
        PermissionORM.resource == permission_data.resource,
        PermissionORM.action == permission_data.action
    ).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 권한입니다"
        )
    
    new_permission = PermissionORM(
        resource=permission_data.resource,
        action=permission_data.action,
        description=permission_data.description
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return PermissionResponse(
        id=new_permission.id,
        resource=new_permission.resource,
        action=new_permission.action,
        description=new_permission.description
    )


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """권한 수정"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="권한을 찾을 수 없습니다")
    
    # 권한 중복 확인 (자기 자신 제외)
    if permission_data.resource and permission_data.action:
        existing_permission = db.query(PermissionORM).filter(
            PermissionORM.resource == permission_data.resource,
            PermissionORM.action == permission_data.action,
            PermissionORM.id != permission_id
        ).first()
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 권한입니다"
            )
    
    # 업데이트
    if permission_data.resource:
        permission.resource = permission_data.resource
    if permission_data.action:
        permission.action = permission_data.action
    if permission_data.description is not None:
        permission.description = permission_data.description
    
    db.commit()
    db.refresh(permission)
    
    return PermissionResponse(
        id=permission.id,
        resource=permission.resource,
        action=permission.action,
        description=permission.description
    )


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """권한 삭제"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="권한을 찾을 수 없습니다")
    
    # 역할에 할당된 권한이 있는지 확인
    role_permissions = db.query(RolePermissionORM).filter(RolePermissionORM.permission_id == permission_id).count()
    if role_permissions > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="역할에 할당된 권한은 삭제할 수 없습니다"
        )
    
    db.delete(permission)
    db.commit()
    
    return {"message": "권한이 성공적으로 삭제되었습니다"}


# ===== 권한 매트릭스 관리 API =====

@router.get("/matrix", response_model=PermissionMatrixResponse)
def get_permission_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """권한 매트릭스 조회"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 모든 역할과 권한 조회
    roles = db.query(RoleORM).all()
    permissions = db.query(PermissionORM).all()
    
    # 권한 매트릭스 구성
    matrix = {}
    for role in roles:
        matrix[role.id] = {}
        for permission in permissions:
            # 해당 역할에 권한이 할당되어 있는지 확인
            role_permission = db.query(RolePermissionORM).filter(
                RolePermissionORM.role_id == role.id,
                RolePermissionORM.permission_id == permission.id
            ).first()
            matrix[role.id][permission.id] = role_permission is not None
    
    return PermissionMatrixResponse(
        roles=[
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                is_system_role=role.is_system_role,
                created_by=role.created_by,
                created_at=None,
                updated_at=None
            ) for role in roles
        ],
        permissions=[
            PermissionResponse(
                id=permission.id,
                resource=permission.resource,
                action=permission.action,
                description=permission.description
            ) for permission in permissions
        ],
        matrix=matrix
    )


@router.post("/matrix/assign", status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(
    assignment: RolePermissionAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """역할에 권한 할당"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 역할과 권한 존재 확인
    role = db.query(RoleORM).filter(RoleORM.id == assignment.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    
    permission = db.query(PermissionORM).filter(PermissionORM.id == assignment.permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="권한을 찾을 수 없습니다")
    
    # 이미 할당되어 있는지 확인
    existing_assignment = db.query(RolePermissionORM).filter(
        RolePermissionORM.role_id == assignment.role_id,
        RolePermissionORM.permission_id == assignment.permission_id
    ).first()
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 할당된 권한입니다"
        )
    
    # 권한 할당
    new_assignment = RolePermissionORM(
        role_id=assignment.role_id,
        permission_id=assignment.permission_id,
        granted_by=current_user.id
    )
    
    db.add(new_assignment)
    db.commit()
    
    return {"message": "권한이 성공적으로 할당되었습니다"}


@router.delete("/matrix/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_permission_from_role(
    assignment: RolePermissionAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """역할에서 권한 제거"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 권한 할당 찾기
    assignment_record = db.query(RolePermissionORM).filter(
        RolePermissionORM.role_id == assignment.role_id,
        RolePermissionORM.permission_id == assignment.permission_id
    ).first()
    
    if not assignment_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할당된 권한을 찾을 수 없습니다")
    
    db.delete(assignment_record)
    db.commit()
    
    return {"message": "권한이 성공적으로 제거되었습니다"}


@router.delete("/permissions/demo-carsystem", status_code=status.HTTP_200_OK)
def delete_demo_carsystem_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """데모 자동차 시스템 관련 권한 모두 삭제"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    try:
        # 데모 자동차 시스템 관련 권한 조회
        demo_permissions = db.query(PermissionORM).filter(
            PermissionORM.resource == "demo_carsystem"
        ).all()
        
        deleted_count = 0
        
        for permission in demo_permissions:
            # 역할에 할당된 권한 먼저 삭제
            db.query(RolePermissionORM).filter(
                RolePermissionORM.permission_id == permission.id
            ).delete()
            
            # 권한 삭제
            db.delete(permission)
            deleted_count += 1
        
        db.commit()
        
        return {
            "message": f"데모 자동차 시스템 관련 권한 {deleted_count}개가 성공적으로 삭제되었습니다",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데모 자동차 시스템 권한 삭제 실패: {str(e)}"
        )


# ===== 사용자-역할 관리 API =====

@router.post("/user-roles/assign", status_code=status.HTTP_201_CREATED)
def assign_role_to_user(
    assignment: UserRoleAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자에게 역할 할당"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 사용자와 역할 존재 확인
    user = db.query(UserORM).filter(UserORM.id == assignment.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")
    
    role = db.query(RoleORM).filter(RoleORM.id == assignment.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    
    # 이미 할당되어 있는지 확인
    existing_assignment = db.query(UserRoleORM).filter(
        UserRoleORM.user_id == assignment.user_id,
        UserRoleORM.role_id == assignment.role_id
    ).first()
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 할당된 역할입니다"
        )
    
    # 역할 할당
    new_assignment = UserRoleORM(
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        assigned_by=current_user.id
    )
    
    db.add(new_assignment)
    db.commit()
    
    return {"message": "역할이 성공적으로 할당되었습니다"}


@router.delete("/user-roles/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_role_from_user(
    assignment: UserRoleAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자에서 역할 제거"""
    # 권한 확인
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    # 역할 할당 찾기
    assignment_record = db.query(UserRoleORM).filter(
        UserRoleORM.user_id == assignment.user_id,
        UserRoleORM.role_id == assignment.role_id
    ).first()
    
    if not assignment_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할당된 역할을 찾을 수 없습니다")
    
    db.delete(assignment_record)
    db.commit()
    
    return {"message": "역할이 성공적으로 제거되었습니다"}
