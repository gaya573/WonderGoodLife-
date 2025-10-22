"""
권한 관리 서비스 - 리소스 기반 권한 시스템
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.entities import User, Permission, Role, UserRole, RolePermission, ResourceType, ActionType
from ..infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyPermissionRepository,
    SQLAlchemyRoleRepository,
    SQLAlchemyUserRoleRepository,
    SQLAlchemyRolePermissionRepository,
    SQLAlchemyUserPermissionRepository
)


class PermissionService:
    """권한 관리 서비스"""
    
    def __init__(
        self,
        user_repo: SQLAlchemyUserRepository,
        permission_repo: SQLAlchemyPermissionRepository,
        role_repo: SQLAlchemyRoleRepository,
        user_role_repo: SQLAlchemyUserRoleRepository,
        role_permission_repo: SQLAlchemyRolePermissionRepository,
        user_permission_repo: SQLAlchemyUserPermissionRepository
    ):
        self.user_repo = user_repo
        self.permission_repo = permission_repo
        self.role_repo = role_repo
        self.user_role_repo = user_role_repo
        self.role_permission_repo = role_permission_repo
        self.user_permission_repo = user_permission_repo
    
    def has_permission(self, user: User, permission: str) -> bool:
        """사용자가 특정 권한을 가지고 있는지 확인"""
        # ADMIN 역할은 모든 권한
        if user.role == "ADMIN":
            return True
        
        # 사용자의 직접 권한 확인 (UserPermission 테이블에서)
        if self.user_permission_repo.has_permission(user.id, permission):
            return True
        
        # 사용자의 역할을 통한 권한 확인
        user_roles = self.user_role_repo.find_by_user_id(user.id)
        for user_role in user_roles:
            role_permissions = self.role_permission_repo.find_by_role_id(user_role.role_id)
            for role_permission in role_permissions:
                permission_entity = self.permission_repo.find_by_id(role_permission.permission_id)
                if permission_entity and permission_entity.get_permission_string() == permission:
                    return True
        
        return False
    
    def get_user_permissions(self, user: User) -> List[str]:
        """사용자의 모든 권한 목록 반환"""
        # ADMIN은 모든 권한
        if user.role == "ADMIN":
            return ["excel_upload", "excel_search", "user_search", "data_approval", "system_admin"]
        
        # 사용자의 실제 권한 조회 (UserPermission 테이블에서)
        return self.user_permission_repo.find_by_user_id(user.id)
    
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: int) -> bool:
        """사용자에게 역할 부여 (권한 확인 필요)"""
        # 권한 확인 - 시스템 관리 권한 필요
        assigner = self.user_repo.find_by_id(assigned_by)
        if not assigner or not self.has_permission(assigner, "system_admin"):
            return False
        
        # 중복 확인
        existing = self.user_role_repo.find_by_user_and_role(user_id, role_id)
        if existing:
            return False
        
        # 역할 부여
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by
        )
        
        return self.user_role_repo.save(user_role) is not None
    
    def revoke_role_from_user(self, user_id: int, role_id: int, revoked_by: int) -> bool:
        """사용자에서 역할 제거 (권한 확인 필요)"""
        # 권한 확인 - 시스템 관리 권한 필요
        revoker = self.user_repo.find_by_id(revoked_by)
        if not revoker or not self.has_permission(revoker, "system_admin"):
            return False
        
        # 역할 제거
        return self.user_role_repo.delete_by_user_and_role(user_id, role_id)
    
    def grant_permission_to_role(self, role_id: int, permission_id: int, granted_by: int) -> bool:
        """역할에 권한 부여 (권한 확인 필요)"""
        # 권한 확인 - 시스템 관리 권한 필요
        granter = self.user_repo.find_by_id(granted_by)
        if not granter or not self.has_permission(granter, "system_admin"):
            return False
        
        # 중복 확인
        existing = self.role_permission_repo.find_by_role_and_permission(role_id, permission_id)
        if existing:
            return False
        
        # 권한 부여
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
            granted_by=granted_by
        )
        
        return self.role_permission_repo.save(role_permission) is not None
    
    def revoke_permission_from_role(self, role_id: int, permission_id: int, revoked_by: int) -> bool:
        """역할에서 권한 제거 (권한 확인 필요)"""
        # 권한 확인 - 시스템 관리 권한 필요
        revoker = self.user_repo.find_by_id(revoked_by)
        if not revoker or not self.has_permission(revoker, "system_admin"):
            return False
        
        # 권한 제거
        return self.role_permission_repo.delete_by_role_and_permission(role_id, permission_id)
    
    def grant_user_permission(self, user_id: int, permission_name: str, granted_by: int) -> bool:
        """사용자에게 직접 권한 부여"""
        return self.user_permission_repo.grant_permission(user_id, permission_name, granted_by)
    
    def revoke_user_permission(self, user_id: int, permission_name: str) -> bool:
        """사용자에서 직접 권한 제거"""
        return self.user_permission_repo.revoke_permission(user_id, permission_name)
    
    def grant_all_permissions_to_user(self, user_id: int, granted_by: int) -> bool:
        """사용자에게 모든 권한 부여"""
        all_permissions = [
            "excel_upload",
            "excel_search", 
            "user_search",
            "data_approval",
            "system_admin"
        ]
        
        success = True
        for permission in all_permissions:
            if not self.user_permission_repo.grant_permission(user_id, permission, granted_by):
                success = False
        
        return success
    
    def create_default_permissions(self) -> None:
        """기본 권한들 생성"""
        default_permissions = [
            # 메인 자동차 시스템
            Permission(ResourceType.MAIN_CARSYSTEM.value, ActionType.READ.value, "메인 DB 조회"),
            Permission(ResourceType.MAIN_CARSYSTEM.value, ActionType.WRITE.value, "메인 DB 생성/수정"),
            Permission(ResourceType.MAIN_CARSYSTEM.value, ActionType.DELETE.value, "메인 DB 삭제"),
            Permission(ResourceType.MAIN_CARSYSTEM.value, ActionType.CDC.value, "메인 DB 마이그레이션"),
            
            # 데모 자동차 시스템
            Permission(ResourceType.DEMO_CARSYSTEM.value, ActionType.READ.value, "데모 DB 조회"),
            Permission(ResourceType.DEMO_CARSYSTEM.value, ActionType.WRITE.value, "데모 DB 생성/수정"),
            Permission(ResourceType.DEMO_CARSYSTEM.value, ActionType.DELETE.value, "데모 DB 삭제"),
            
            # Staging 데이터
            Permission(ResourceType.STAGING_DATA.value, ActionType.READ.value, "Staging 데이터 조회"),
            Permission(ResourceType.STAGING_DATA.value, ActionType.WRITE.value, "Staging 데이터 생성/수정"),
            Permission(ResourceType.STAGING_DATA.value, ActionType.DELETE.value, "Staging 데이터 삭제"),
            
            # 사용자 관리
            Permission(ResourceType.USER_MANAGEMENT.value, ActionType.READ.value, "사용자 조회"),
            Permission(ResourceType.USER_MANAGEMENT.value, ActionType.WRITE.value, "사용자 생성/수정"),
            Permission(ResourceType.USER_MANAGEMENT.value, ActionType.DELETE.value, "사용자 삭제"),
            
            # 사용자 권한 관리
            Permission(ResourceType.USER_ROLE.value, ActionType.READ.value, "사용자 권한 조회"),
            Permission(ResourceType.USER_ROLE.value, ActionType.WRITE.value, "사용자 권한 수정"),
            Permission(ResourceType.USER_ROLE.value, ActionType.ADMIN.value, "사용자 권한 관리"),
            
            # 시스템 관리
            Permission(ResourceType.SYSTEM_ADMIN.value, ActionType.READ.value, "시스템 조회"),
            Permission(ResourceType.SYSTEM_ADMIN.value, ActionType.ADMIN.value, "시스템 관리"),
            
            # 이벤트 관리
            Permission(ResourceType.EVENT_DATA.value, ActionType.READ.value, "이벤트 조회"),
            Permission(ResourceType.EVENT_DATA.value, ActionType.WRITE.value, "이벤트 생성/수정"),
            Permission(ResourceType.EVENT_DATA.value, ActionType.DELETE.value, "이벤트 삭제"),
        ]
        
        for permission in default_permissions:
            existing = self.permission_repo.find_by_resource_and_action(
                permission.resource, permission.action
            )
            if not existing:
                self.permission_repo.save(permission)
    
    def create_default_roles(self) -> None:
        """기본 역할들 생성"""
        # 대표관리 역할 (모든 권한)
        ceo_role = Role(
            name="대표관리",
            description="모든 권한을 가진 최고 관리자",
            is_system_role=True
        )
        ceo_role = self.role_repo.save(ceo_role)
        
        # 부장관리 역할
        manager_role = Role(
            name="부장관리",
            description="직원 관리 및 데이터 관리 권한",
            is_system_role=True
        )
        manager_role = self.role_repo.save(manager_role)
        
        # 사원(검색) 역할
        employee_search_role = Role(
            name="사원(검색)",
            description="데이터 조회만 가능한 사원",
            is_system_role=True
        )
        employee_search_role = self.role_repo.save(employee_search_role)
        
        # 사원(이벤트검색) 역할
        employee_event_search_role = Role(
            name="사원(이벤트검색)",
            description="이벤트 조회만 가능한 사원",
            is_system_role=True
        )
        employee_event_search_role = self.role_repo.save(employee_event_search_role)
        
        # 사원(이벤트입력) 역할
        employee_event_input_role = Role(
            name="사원(이벤트입력)",
            description="이벤트 입력 및 조회가 가능한 사원",
            is_system_role=True
        )
        employee_event_input_role = self.role_repo.save(employee_event_input_role)
        
        # 사원(입력) 역할
        employee_input_role = Role(
            name="사원(입력)",
            description="데이터 입력 및 조회가 가능한 사원",
            is_system_role=True
        )
        employee_input_role = self.role_repo.save(employee_input_role)
        
        # 사원(마이그레이션) 역할
        employee_migration_role = Role(
            name="사원(마이그레이션)",
            description="데이터 마이그레이션이 가능한 사원",
            is_system_role=True
        )
        employee_migration_role = self.role_repo.save(employee_migration_role)
        
        # 역할별 권한 부여 (대표관리는 모든 권한이므로 생략)
        self._assign_role_permissions(manager_role.id)
        self._assign_role_permissions(employee_search_role.id)
        self._assign_role_permissions(employee_event_search_role.id)
        self._assign_role_permissions(employee_event_input_role.id)
        self._assign_role_permissions(employee_input_role.id)
        self._assign_role_permissions(employee_migration_role.id)
    
    def _assign_role_permissions(self, role_id: int) -> None:
        """역할별 기본 권한 부여"""
        role_name = self.role_repo.find_by_id(role_id).name
        
        if role_name == "부장관리":
            # 부장관리 권한: 모든 데이터 관리 + 사용자 관리
            permissions = [
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.WRITE.value),
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.DELETE.value),
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.CDC.value),
                (ResourceType.DEMO_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.DEMO_CARSYSTEM.value, ActionType.WRITE.value),
                (ResourceType.STAGING_DATA.value, ActionType.READ.value),
                (ResourceType.STAGING_DATA.value, ActionType.WRITE.value),
                (ResourceType.STAGING_DATA.value, ActionType.DELETE.value),
                (ResourceType.USER_MANAGEMENT.value, ActionType.READ.value),
                (ResourceType.USER_MANAGEMENT.value, ActionType.WRITE.value),
            ]
        
        elif role_name == "사원(검색)":
            # 사원(검색) 권한: 조회만
            permissions = [
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.DEMO_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.STAGING_DATA.value, ActionType.READ.value),
            ]
        
        elif role_name == "사원(이벤트검색)":
            # 사원(이벤트검색) 권한: 이벤트 조회만
            permissions = [
                (ResourceType.EVENT_DATA.value, ActionType.READ.value),
            ]
        
        elif role_name == "사원(이벤트입력)":
            # 사원(이벤트입력) 권한: 이벤트 입력 + 조회
            permissions = [
                (ResourceType.EVENT_DATA.value, ActionType.READ.value),
                (ResourceType.EVENT_DATA.value, ActionType.WRITE.value),
            ]
        
        elif role_name == "사원(입력)":
            # 사원(입력) 권한: 입력 + 조회
            permissions = [
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.WRITE.value),
                (ResourceType.DEMO_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.STAGING_DATA.value, ActionType.READ.value),
                (ResourceType.STAGING_DATA.value, ActionType.WRITE.value),
            ]
        
        elif role_name == "사원(마이그레이션)":
            # 사원(마이그레이션) 권한: 조회 + 마이그레이션
            permissions = [
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.MAIN_CARSYSTEM.value, ActionType.CDC.value),
                (ResourceType.DEMO_CARSYSTEM.value, ActionType.READ.value),
                (ResourceType.STAGING_DATA.value, ActionType.READ.value),
            ]
        
        else:
            permissions = []
        
        # 권한 부여
        for resource, action in permissions:
            permission = self.permission_repo.find_by_resource_and_action(resource, action)
            if permission:
                self.role_permission_repo.save(RolePermission(
                    role_id=role_id,
                    permission_id=permission.id,
                    granted_by=1  # 시스템
                ))


def get_permission_service(db):
    """권한 서비스 의존성 주입"""
    user_repo = SQLAlchemyUserRepository(db)
    permission_repo = SQLAlchemyPermissionRepository(db)
    role_repo = SQLAlchemyRoleRepository(db)
    user_role_repo = SQLAlchemyUserRoleRepository(db)
    role_permission_repo = SQLAlchemyRolePermissionRepository(db)
    user_permission_repo = SQLAlchemyUserPermissionRepository(db)
    
    return PermissionService(
        user_repo=user_repo,
        permission_repo=permission_repo,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        role_permission_repo=role_permission_repo,
        user_permission_repo=user_permission_repo
    )
