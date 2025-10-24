"""
Repository 구현체 - SQLAlchemy를 사용한 데이터 영속성
새로운 테이블 구조에 맞게 재작성
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime
from ..application.ports import (
    BrandRepository, ModelRepository, TrimRepository,
    ColorRepository, OptionRepository, StagingOptionRepository,
    DiscountPolicyRepository, BrandCardBenefitRepository,
    BrandPromoRepository, BrandInventoryDiscountRepository,
    BrandPrePurchaseRepository
)
from ..domain.entities import (
    Brand, Model, Trim, TrimCarColor, OptionTitle, OptionPrice,
    VehicleLine,  # 새로 추가
    StagingBrand, StagingModel, StagingTrim, StagingVehicleLine,  # 새로 추가
    StagingVersion,  # 단순화된 버전 관리
    StagingOption, StagingOptionTitle, StagingOptionPrice,  # 새로 추가
    User, UserRole, UserStatus, UserPosition,
    Permission, Role, UserRoleAssignment, RolePermission,
    Event, EventRegistration, EventType, EventStatus,  # 이벤트 관련
    DiscountPolicy, BrandCardBenefit, BrandPromo, BrandInventoryDiscount, BrandPrePurchase, PolicyType  # 할인 정책 관련
)
from .orm_models import (
    BrandORM, ModelORM, TrimORM, TrimCarColorORM, VehicleLineORM,  # 새로 추가
    OptionTitleORM, OptionPriceORM,
    StagingBrandORM, StagingModelORM, StagingTrimORM, StagingVehicleLineORM,  # 새로 추가
    StagingVersionORM,  # 단순화된 버전 관리
    StagingOptionORM, StagingOptionTitleORM, StagingOptionPriceORM,  # 새로 추가
    UserORM, PermissionORM, RoleORM, UserRoleORM, RolePermissionORM, UserPermissionORM,
    EventORM, EventRegistrationORM,  # 이벤트 관련
    DiscountPolicyORM, BrandCardBenefitORM, BrandPromoORM, BrandInventoryDiscountORM, BrandPrePurchaseORM  # 할인 정책 관련
)


# ===== 사용자 Repository =====

class SQLAlchemyUserRepository:
    """SQLAlchemy 기반 사용자 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        return self._to_entity(db_user) if db_user else None
    
    def find_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserORM).filter(UserORM.username == username).first()
        return self._to_entity(db_user) if db_user else None
    
    def find_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserORM).filter(UserORM.email == email).first()
        return self._to_entity(db_user) if db_user else None
    
    def find_all(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
        query = self.db.query(UserORM)
        if role:
            query = query.filter(UserORM.role == role)
        db_users = query.offset(skip).limit(limit).all()
        return [self._to_entity(u) for u in db_users]
    
    def save(self, user: User) -> User:
        db_user = UserORM(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            phone_number=user.phone_number,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            position=user.position.value if hasattr(user.position, 'value') else user.position,
            status=user.status.value if hasattr(user.status, 'value') else user.status
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    def update(self, user_id: int, user: User) -> Optional[User]:
        db_user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not db_user:
            return None
        
        db_user.username = user.username
        db_user.email = user.email
        db_user.password_hash = user.password_hash
        db_user.phone_number = user.phone_number
        db_user.role = user.role.value if hasattr(user.role, 'value') else user.role
        db_user.position = user.position.value if hasattr(user.position, 'value') else user.position
        db_user.status = user.status.value if hasattr(user.status, 'value') else user.status
        db_user.updated_at = user.updated_at
        
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: UserORM) -> User:
        return User(
            id=orm.id,
            username=orm.username,
            email=orm.email,
            password_hash=orm.password_hash,
            phone_number=orm.phone_number,
            role=orm.role,
            position=orm.position,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )


# ===== 권한 Repository =====

class SQLAlchemyPermissionRepository:
    """SQLAlchemy 기반 권한 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, permission_id: int) -> Optional[Permission]:
        db_permission = self.db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
        return self._to_entity(db_permission) if db_permission else None
    
    def find_by_resource_and_action(self, resource: str, action: str) -> Optional[Permission]:
        db_permission = self.db.query(PermissionORM).filter(
            PermissionORM.resource == resource,
            PermissionORM.action == action
        ).first()
        return self._to_entity(db_permission) if db_permission else None
    
    def find_all(self) -> List[Permission]:
        db_permissions = self.db.query(PermissionORM).all()
        return [self._to_entity(p) for p in db_permissions]
    
    def save(self, permission: Permission) -> Permission:
        db_permission = PermissionORM(
            resource=permission.resource,
            action=permission.action,
            description=permission.description
        )
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        return self._to_entity(db_permission)
    
    @staticmethod
    def _to_entity(orm: PermissionORM) -> Permission:
        return Permission(
            id=orm.id,
            resource=orm.resource,
            action=orm.action,
            description=orm.description
        )


# ===== 역할 Repository =====

class SQLAlchemyRoleRepository:
    """SQLAlchemy 기반 역할 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, role_id: int) -> Optional[Role]:
        db_role = self.db.query(RoleORM).filter(RoleORM.id == role_id).first()
        return self._to_entity(db_role) if db_role else None
    
    def find_by_name(self, name: str) -> Optional[Role]:
        db_role = self.db.query(RoleORM).filter(RoleORM.name == name).first()
        return self._to_entity(db_role) if db_role else None
    
    def find_all(self) -> List[Role]:
        db_roles = self.db.query(RoleORM).all()
        return [self._to_entity(r) for r in db_roles]
    
    def save(self, role: Role) -> Role:
        db_role = RoleORM(
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            created_by=role.created_by
        )
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return self._to_entity(db_role)
    
    @staticmethod
    def _to_entity(orm: RoleORM) -> Role:
        return Role(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            is_system_role=orm.is_system_role,
            created_by=orm.created_by
        )


# ===== 사용자-역할 Repository =====

class SQLAlchemyUserRoleRepository:
    """SQLAlchemy 기반 사용자-역할 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_user_id(self, user_id: int) -> List[UserRoleAssignment]:
        db_user_roles = self.db.query(UserRoleORM).filter(UserRoleORM.user_id == user_id).all()
        return [self._to_entity(ur) for ur in db_user_roles]
    
    def find_by_user_and_role(self, user_id: int, role_id: int) -> Optional[UserRoleAssignment]:
        db_user_role = self.db.query(UserRoleORM).filter(
            UserRoleORM.user_id == user_id,
            UserRoleORM.role_id == role_id
        ).first()
        return self._to_entity(db_user_role) if db_user_role else None
    
    def save(self, user_role: UserRoleAssignment) -> UserRoleAssignment:
        db_user_role = UserRoleORM(
            user_id=user_role.user_id,
            role_id=user_role.role_id,
            assigned_by=user_role.assigned_by,
            assigned_at=user_role.assigned_at
        )
        self.db.add(db_user_role)
        self.db.commit()
        self.db.refresh(db_user_role)
        return self._to_entity(db_user_role)
    
    def delete_by_user_and_role(self, user_id: int, role_id: int) -> bool:
        db_user_role = self.db.query(UserRoleORM).filter(
            UserRoleORM.user_id == user_id,
            UserRoleORM.role_id == role_id
        ).first()
        if not db_user_role:
            return False
        
        self.db.delete(db_user_role)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: UserRoleORM) -> UserRoleAssignment:
        return UserRoleAssignment(
            id=orm.id,
            user_id=orm.user_id,
            role_id=orm.role_id,
            assigned_by=orm.assigned_by,
            assigned_at=orm.assigned_at
        )


# ===== 역할-권한 Repository =====

class SQLAlchemyRolePermissionRepository:
    """SQLAlchemy 기반 역할-권한 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_role_id(self, role_id: int) -> List[RolePermission]:
        db_role_permissions = self.db.query(RolePermissionORM).filter(RolePermissionORM.role_id == role_id).all()
        return [self._to_entity(rp) for rp in db_role_permissions]
    
    def find_by_role_and_permission(self, role_id: int, permission_id: int) -> Optional[RolePermission]:
        db_role_permission = self.db.query(RolePermissionORM).filter(
            RolePermissionORM.role_id == role_id,
            RolePermissionORM.permission_id == permission_id
        ).first()
        return self._to_entity(db_role_permission) if db_role_permission else None
    
    def save(self, role_permission: RolePermission) -> RolePermission:
        db_role_permission = RolePermissionORM(
            role_id=role_permission.role_id,
            permission_id=role_permission.permission_id,
            granted_by=role_permission.granted_by,
            granted_at=role_permission.granted_at
        )
        self.db.add(db_role_permission)
        self.db.commit()
        self.db.refresh(db_role_permission)
        return self._to_entity(db_role_permission)
    
    def delete_by_role_and_permission(self, role_id: int, permission_id: int) -> bool:
        db_role_permission = self.db.query(RolePermissionORM).filter(
            RolePermissionORM.role_id == role_id,
            RolePermissionORM.permission_id == permission_id
        ).first()
        if not db_role_permission:
            return False
        
        self.db.delete(db_role_permission)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: RolePermissionORM) -> RolePermission:
        return RolePermission(
            id=orm.id,
            role_id=orm.role_id,
            permission_id=orm.permission_id,
            granted_by=orm.granted_by,
            granted_at=orm.granted_at
        )


# ===== UserPermission Repository =====

class SQLAlchemyUserPermissionRepository:
    """사용자 권한 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_user_id(self, user_id: int) -> List[str]:
        """사용자의 모든 권한 조회"""
        permissions = self.db.query(UserPermissionORM).filter(
            UserPermissionORM.user_id == user_id
        ).all()
        return [p.permission_name for p in permissions]
    
    def grant_permission(self, user_id: int, permission_name: str, granted_by: int) -> bool:
        """사용자에게 권한 부여"""
        # 중복 확인
        existing = self.db.query(UserPermissionORM).filter(
            UserPermissionORM.user_id == user_id,
            UserPermissionORM.permission_name == permission_name
        ).first()
        
        if existing:
            return False
        
        # 권한 부여
        user_permission = UserPermissionORM(
            user_id=user_id,
            permission_name=permission_name,
            granted_by=granted_by
        )
        self.db.add(user_permission)
        self.db.commit()
        return True
    
    def revoke_permission(self, user_id: int, permission_name: str) -> bool:
        """사용자에서 권한 제거"""
        permission = self.db.query(UserPermissionORM).filter(
            UserPermissionORM.user_id == user_id,
            UserPermissionORM.permission_name == permission_name
        ).first()
        
        if not permission:
            return False
        
        self.db.delete(permission)
        self.db.commit()
        return True
    
    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """사용자가 특정 권한을 가지고 있는지 확인"""
        permission = self.db.query(UserPermissionORM).filter(
            UserPermissionORM.user_id == user_id,
            UserPermissionORM.permission_name == permission_name
        ).first()
        
        return permission is not None


# ===== Main Production Layer Repositories =====

class SQLAlchemyBrandRepository(BrandRepository):
    """SQLAlchemy 기반 브랜드 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, brand_id: int) -> Optional[Brand]:
        db_brand = self.db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        return self._to_entity(db_brand) if db_brand else None
    
    def find_by_name(self, name: str) -> Optional[Brand]:
        db_brand = self.db.query(BrandORM).filter(BrandORM.name == name).first()
        return self._to_entity(db_brand) if db_brand else None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Brand]:
        db_brands = self.db.query(BrandORM).offset(skip).limit(limit).all()
        return [self._to_entity(b) for b in db_brands]
    
    def save(self, brand: Brand) -> Brand:
        db_brand = BrandORM(
            name=brand.name,
            country=brand.country,
            logo_url=brand.logo_url,
            manager=brand.manager
        )
        self.db.add(db_brand)
        self.db.commit()
        self.db.refresh(db_brand)
        return self._to_entity(db_brand)
    
    def update(self, brand_id: int, brand: Brand) -> Optional[Brand]:
        db_brand = self.db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not db_brand:
            return None
        
        db_brand.name = brand.name
        db_brand.country = brand.country
        db_brand.logo_url = brand.logo_url
        db_brand.manager = brand.manager
        
        self.db.commit()
        self.db.refresh(db_brand)
        return self._to_entity(db_brand)
    
    def delete(self, brand_id: int) -> bool:
        db_brand = self.db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not db_brand:
            return False
        
        self.db.delete(db_brand)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: BrandORM) -> Brand:
        return Brand(
            id=orm.id,
            name=orm.name,
            country=orm.country,
            logo_url=orm.logo_url,
            manager=orm.manager
        )


class SQLAlchemyVehicleLineRepository:
    """SQLAlchemy 기반 차량 라인 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, vehicle_line_id: int) -> Optional[VehicleLine]:
        db_vehicle_line = self.db.query(VehicleLineORM).filter(VehicleLineORM.id == vehicle_line_id).first()
        return self._to_entity(db_vehicle_line) if db_vehicle_line else None
    
    def find_by_brand_and_name(self, brand_id: int, name: str) -> Optional[VehicleLine]:
        db_vehicle_line = self.db.query(VehicleLineORM).filter(
            VehicleLineORM.brand_id == brand_id,
            VehicleLineORM.name == name
        ).first()
        return self._to_entity(db_vehicle_line) if db_vehicle_line else None
    
    def find_all_by_brand(self, brand_id: int) -> List[VehicleLine]:
        db_vehicle_lines = self.db.query(VehicleLineORM).filter(VehicleLineORM.brand_id == brand_id).all()
        return [self._to_entity(vl) for vl in db_vehicle_lines]
    
    def save(self, vehicle_line: VehicleLine) -> VehicleLine:
        db_vehicle_line = VehicleLineORM(
            name=vehicle_line.name,
            description=vehicle_line.description,
            brand_id=vehicle_line.brand_id
        )
        self.db.add(db_vehicle_line)
        self.db.commit()
        self.db.refresh(db_vehicle_line)
        return self._to_entity(db_vehicle_line)
    
    @staticmethod
    def _to_entity(orm: VehicleLineORM) -> VehicleLine:
        return VehicleLine(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            brand_id=orm.brand_id
        )


class SQLAlchemyModelRepository(ModelRepository):
    """SQLAlchemy 기반 모델 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, model_id: int) -> Optional[Model]:
        db_model = self.db.query(ModelORM).filter(ModelORM.id == model_id).first()
        return self._to_entity(db_model) if db_model else None
    
    def find_by_name(self, name: str) -> Optional[Model]:
        db_model = self.db.query(ModelORM).filter(ModelORM.name == name).first()
        return self._to_entity(db_model) if db_model else None
    
    def find_all_by_vehicle_line(self, vehicle_line_id: int) -> List[Model]:
        db_models = self.db.query(ModelORM).filter(ModelORM.vehicle_line_id == vehicle_line_id).all()
        return [self._to_entity(m) for m in db_models]
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Model]:
        db_models = self.db.query(ModelORM).offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in db_models]
    
    def save(self, model: Model) -> Model:
        db_model = ModelORM(
            name=model.name,
            code=model.code,
            vehicle_line_id=model.vehicle_line_id,
            release_year=model.release_year,
            price=model.price,
            foreign=model.foreign
        )
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_entity(db_model)
    
    def update(self, model_id: int, model: Model) -> Optional[Model]:
        db_model = self.db.query(ModelORM).filter(ModelORM.id == model_id).first()
        if not db_model:
            return None
        
        db_model.name = model.name
        db_model.code = model.code
        db_model.vehicle_line_id = model.vehicle_line_id
        db_model.release_year = model.release_year
        db_model.price = model.price
        db_model.foreign = model.foreign
        
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_entity(db_model)
    
    def delete(self, model_id: int) -> bool:
        db_model = self.db.query(ModelORM).filter(ModelORM.id == model_id).first()
        if not db_model:
            return False
        
        self.db.delete(db_model)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: ModelORM) -> Model:
        return Model(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            vehicle_line_id=orm.vehicle_line_id,
            release_year=orm.release_year,
            price=orm.price,
            foreign=orm.foreign
        )


class SQLAlchemyTrimRepository(TrimRepository):
    """SQLAlchemy 기반 트림 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, trim_id: int) -> Optional[Trim]:
        db_trim = self.db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        return self._to_entity(db_trim) if db_trim else None
    
    def find_by_model_and_name(self, model_id: int, name: str) -> Optional[Trim]:
        db_trim = self.db.query(TrimORM).filter(
            TrimORM.model_id == model_id,
            TrimORM.name == name
        ).first()
        return self._to_entity(db_trim) if db_trim else None
    
    def find_all_by_model(self, model_id: int) -> List[Trim]:
        db_trims = self.db.query(TrimORM).filter(TrimORM.model_id == model_id).all()
        return [self._to_entity(t) for t in db_trims]
    
    def find_all(self, model_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Trim]:
        query = self.db.query(TrimORM)
        if model_id:
            query = query.filter(TrimORM.model_id == model_id)
        db_trims = query.offset(skip).limit(limit).all()
        return [self._to_entity(t) for t in db_trims]
    
    def save(self, trim: Trim) -> Trim:
        db_trim = TrimORM(
            name=trim.name,
            car_type=trim.car_type,
            fuel_name=trim.fuel_name,
            cc=trim.cc,
            base_price=trim.base_price,
            description=trim.description,
            model_id=trim.model_id
        )
        self.db.add(db_trim)
        self.db.commit()
        self.db.refresh(db_trim)
        return self._to_entity(db_trim)
    
    def update(self, trim_id: int, trim: Trim) -> Optional[Trim]:
        db_trim = self.db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        if not db_trim:
            return None
        
        db_trim.name = trim.name
        db_trim.car_type = trim.car_type
        db_trim.fuel_name = trim.fuel_name
        db_trim.cc = trim.cc
        db_trim.base_price = trim.base_price
        db_trim.description = trim.description
        db_trim.model_id = trim.model_id
        
        self.db.commit()
        self.db.refresh(db_trim)
        return self._to_entity(db_trim)
    
    def delete(self, trim_id: int) -> bool:
        db_trim = self.db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        if not db_trim:
            return False
        
        self.db.delete(db_trim)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: TrimORM) -> Trim:
        return Trim(
            id=orm.id,
            name=orm.name,
            car_type=orm.car_type,
            fuel_name=orm.fuel_name,
            cc=orm.cc,
            base_price=orm.base_price,
            description=orm.description,
            model_id=orm.model_id
        )


class SQLAlchemyColorRepository(ColorRepository):
    """SQLAlchemy 기반 색상 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_trim_and_name(self, trim_id: int, name: str) -> Optional[TrimCarColor]:
        db_color = self.db.query(TrimCarColorORM).filter(
            TrimCarColorORM.trim_id == trim_id,
            TrimCarColorORM.name == name
        ).first()
        return self._to_entity(db_color) if db_color else None
    
    def find_all_by_trim(self, trim_id: int) -> List[TrimCarColor]:
        db_colors = self.db.query(TrimCarColorORM).filter(TrimCarColorORM.trim_id == trim_id).all()
        return [self._to_entity(c) for c in db_colors]
    
    def save(self, color: TrimCarColor) -> TrimCarColor:
        db_color = TrimCarColorORM(
            name=color.name,
            color_code=color.color_code,
            additional_price=color.additional_price,
            vehicle_interior=color.vehicle_interior,
            trim_id=color.trim_id
        )
        self.db.add(db_color)
        self.db.commit()
        self.db.refresh(db_color)
        return self._to_entity(db_color)
    
    @staticmethod
    def _to_entity(orm: TrimCarColorORM) -> TrimCarColor:
        return TrimCarColor(
            id=orm.id,
            name=orm.name,
            color_code=orm.color_code,
            additional_price=orm.additional_price,
            vehicle_interior=orm.vehicle_interior,
            trim_id=orm.trim_id
        )


class SQLAlchemyOptionRepository(OptionRepository):
    """SQLAlchemy 기반 옵션 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_title_by_trim_and_name(self, trim_id: int, name: str) -> Optional[OptionTitle]:
        db_title = self.db.query(OptionTitleORM).filter(
            OptionTitleORM.trim_id == trim_id,
            OptionTitleORM.name == name
        ).first()
        return self._title_to_entity(db_title) if db_title else None
    
    def find_all_titles_by_trim(self, trim_id: int) -> List[OptionTitle]:
        db_titles = self.db.query(OptionTitleORM).filter(OptionTitleORM.trim_id == trim_id).all()
        return [self._title_to_entity(t) for t in db_titles]
    
    def save_title(self, option_title: OptionTitle) -> OptionTitle:
        db_title = OptionTitleORM(
            name=option_title.name,
            description=option_title.description,
            category=option_title.category,
            trim_id=option_title.trim_id
        )
        self.db.add(db_title)
        self.db.commit()
        self.db.refresh(db_title)
        return self._title_to_entity(db_title)
    
    def find_price_by_title_and_name(self, title_id: int, name: str) -> Optional[OptionPrice]:
        db_price = self.db.query(OptionPriceORM).filter(
            OptionPriceORM.option_title_id == title_id,
            OptionPriceORM.name == name
        ).first()
        return self._price_to_entity(db_price) if db_price else None
    
    def find_all_prices_by_title(self, title_id: int) -> List[OptionPrice]:
        db_prices = self.db.query(OptionPriceORM).filter(OptionPriceORM.option_title_id == title_id).all()
        return [self._price_to_entity(p) for p in db_prices]
    
    def save_price(self, option_price: OptionPrice) -> OptionPrice:
        db_price = OptionPriceORM(
            name=option_price.name,
            code=option_price.code,
            description=option_price.description,
            price=option_price.price,
            discounted_price=option_price.discounted_price,
            option_title_id=option_price.option_title_id
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return self._price_to_entity(db_price)
    
    @staticmethod
    def _title_to_entity(orm: OptionTitleORM) -> OptionTitle:
        return OptionTitle(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category=orm.category,
            trim_id=orm.trim_id
        )
    
    @staticmethod
    def _price_to_entity(orm: OptionPriceORM) -> OptionPrice:
        return OptionPrice(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            description=orm.description,
            price=orm.price,
            discounted_price=orm.discounted_price,
            option_title_id=orm.option_title_id
        )


# ===== Staging Repositories (새로운 구조) =====

class SQLAlchemyStagingVersionRepository:
    """SQLAlchemy 기반 Staging 버전 저장소 - 버전 단위 승인 관리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, version_id: int) -> Optional[StagingVersion]:
        db_version = self.db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        return self._to_entity(db_version) if db_version else None
    
    def find_by_name(self, version_name: str) -> Optional[StagingVersion]:
        db_version = self.db.query(StagingVersionORM).filter(StagingVersionORM.version_name == version_name).first()
        return self._to_entity(db_version) if db_version else None
    
    def find_all(self, skip: int = 0, limit: int = 100, approval_status: Optional[str] = None) -> List[StagingVersion]:
        query = self.db.query(StagingVersionORM)
        if approval_status:
            query = query.filter(StagingVersionORM.approval_status == approval_status)
        query = query.order_by(StagingVersionORM.created_at.desc())
        db_versions = query.offset(skip).limit(limit).all()
        return [self._to_entity(v) for v in db_versions]
    
    def count(self, approval_status: Optional[str] = None) -> int:
        query = self.db.query(StagingVersionORM)
        if approval_status:
            query = query.filter(StagingVersionORM.approval_status == approval_status)
        return query.count()
    
    def save(self, version: StagingVersion) -> StagingVersion:
        db_version = StagingVersionORM(
            version_name=version.version_name,
            description=version.description,
            approval_status=version.approval_status,
            approved_by=version.approved_by,
            approved_at=version.approved_at,
            rejected_by=version.rejected_by,
            rejected_at=version.rejected_at,
            rejection_reason=version.rejection_reason,
            created_by=version.created_by,
            # 통계 필드는 동적으로 계산하므로 저장하지 않음
        )
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        return self._to_entity(db_version)
    
    def update(self, version_id: int, version: StagingVersion) -> Optional[StagingVersion]:
        db_version = self.db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not db_version:
            return None
        
        db_version.version_name = version.version_name
        db_version.description = version.description
        db_version.approval_status = version.approval_status
        db_version.approved_by = version.approved_by
        db_version.approved_at = version.approved_at
        db_version.rejected_by = version.rejected_by
        db_version.rejected_at = version.rejected_at
        db_version.rejection_reason = version.rejection_reason
        # 통계 필드는 동적으로 계산하므로 업데이트하지 않음
        
        self.db.commit()
        self.db.refresh(db_version)
        return self._to_entity(db_version)
    
    def delete(self, version_id: int) -> bool:
        db_version = self.db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not db_version:
            return False
        
        self.db.delete(db_version)
        self.db.commit()
        return True
    
    @staticmethod
    def _to_entity(orm: StagingVersionORM) -> StagingVersion:
        return StagingVersion(
            id=orm.id,
            version_name=orm.version_name,
            description=orm.description,
            approval_status=orm.approval_status,
            approved_by=orm.approved_by,
            approved_at=orm.approved_at,
            rejected_by=orm.rejected_by,
            rejected_at=orm.rejected_at,
            rejection_reason=orm.rejection_reason,
            created_by=orm.created_by,
            # 통계 필드는 동적으로 계산하므로 엔티티에서 제거됨
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingBrandRepository:
    """SQLAlchemy 기반 Staging 브랜드 저장소 - version_id 직접 참조"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, brand_id: int) -> Optional[StagingBrand]:
        db_brand = self.db.query(StagingBrandORM).filter(StagingBrandORM.id == brand_id).first()
        return self._to_entity(db_brand) if db_brand else None
    
    def find_by_version_and_name(self, version_id: int, name: str) -> Optional[StagingBrand]:
        db_brand = self.db.query(StagingBrandORM).filter(
            StagingBrandORM.version_id == version_id,
            StagingBrandORM.name == name
        ).first()
        return self._to_entity(db_brand) if db_brand else None
    
    def find_all_by_version(self, version_id: int) -> List[StagingBrand]:
        db_brands = self.db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).all()
        return [self._to_entity(b) for b in db_brands]
    
    def count(self) -> int:
        return self.db.query(StagingBrandORM).count()
    
    def save(self, brand: StagingBrand) -> StagingBrand:
        db_brand = StagingBrandORM(
            name=brand.name,
            country=brand.country,
            version_id=brand.version_id,
            logo_url=brand.logo_url,
            manager=brand.manager,
            created_by=brand.created_by,
            created_by_username=brand.created_by_username,
            created_by_email=brand.created_by_email
        )
        self.db.add(db_brand)
        self.db.commit()
        self.db.refresh(db_brand)
        return self._to_entity(db_brand)
    
    def delete(self, brand_id: int) -> bool:
        """브랜드 삭제"""
        try:
            db_brand = self.db.query(StagingBrandORM).filter(StagingBrandORM.id == brand_id).first()
            if db_brand:
                self.db.delete(db_brand)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingBrandORM) -> StagingBrand:
        return StagingBrand(
            id=orm.id,
            name=orm.name,
            country=orm.country,
            version_id=orm.version_id,
            logo_url=orm.logo_url,
            manager=orm.manager,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingVehicleLineRepository:
    """SQLAlchemy 기반 Staging 차량 라인 저장소 - 새로 추가"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, vehicle_line_id: int) -> Optional[StagingVehicleLine]:
        db_vehicle_line = self.db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.id == vehicle_line_id).first()
        return self._to_entity(db_vehicle_line) if db_vehicle_line else None
    
    def find_by_brand_and_name(self, brand_id: int, name: str) -> Optional[StagingVehicleLine]:
        db_vehicle_line = self.db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.brand_id == brand_id,
            StagingVehicleLineORM.name == name
        ).first()
        return self._to_entity(db_vehicle_line) if db_vehicle_line else None
    
    def find_all_by_brand(self, brand_id: int) -> List[StagingVehicleLine]:
        db_vehicle_lines = self.db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.brand_id == brand_id).all()
        return [self._to_entity(vl) for vl in db_vehicle_lines]
    
    def count(self) -> int:
        return self.db.query(StagingVehicleLineORM).count()
    
    def save(self, vehicle_line: StagingVehicleLine) -> StagingVehicleLine:
        db_vehicle_line = StagingVehicleLineORM(
            name=vehicle_line.name,
            description=vehicle_line.description,
            brand_id=vehicle_line.brand_id,
            created_by=vehicle_line.created_by,
            created_by_username=vehicle_line.created_by_username,
            created_by_email=vehicle_line.created_by_email
        )
        self.db.add(db_vehicle_line)
        self.db.commit()
        self.db.refresh(db_vehicle_line)
        return self._to_entity(db_vehicle_line)
    
    def delete(self, vehicle_line_id: int) -> bool:
        """차량 라인 삭제"""
        try:
            db_vehicle_line = self.db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.id == vehicle_line_id).first()
            if db_vehicle_line:
                self.db.delete(db_vehicle_line)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingVehicleLineORM) -> StagingVehicleLine:
        return StagingVehicleLine(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            brand_id=orm.brand_id,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingModelRepository:
    """SQLAlchemy 기반 Staging 모델 저장소 - vehicle_line_id 참조"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, model_id: int) -> Optional[StagingModel]:
        db_model = self.db.query(StagingModelORM).filter(StagingModelORM.id == model_id).first()
        return self._to_entity(db_model) if db_model else None
    
    def find_by_vehicle_line_and_name(self, vehicle_line_id: int, name: str) -> Optional[StagingModel]:
        db_model = self.db.query(StagingModelORM).filter(
            StagingModelORM.vehicle_line_id == vehicle_line_id,
            StagingModelORM.name == name
        ).first()
        return self._to_entity(db_model) if db_model else None
    
    def find_all_by_vehicle_line(self, vehicle_line_id: int) -> List[StagingModel]:
        db_models = self.db.query(StagingModelORM).filter(StagingModelORM.vehicle_line_id == vehicle_line_id).all()
        return [self._to_entity(m) for m in db_models]
    
    def find_all_by_version(self, version_id: int) -> List[StagingModel]:
        db_models = self.db.query(StagingModelORM).filter(StagingModelORM.version_id == version_id).all()
        return [self._to_entity(m) for m in db_models]
    
    def count(self) -> int:
        return self.db.query(StagingModelORM).count()
    
    def save(self, model: StagingModel) -> StagingModel:
        db_model = StagingModelORM(
            name=model.name,
            code=model.code,
            vehicle_line_id=model.vehicle_line_id,
            release_year=model.release_year,
            price=model.price,
            foreign=model.foreign,
            created_by=model.created_by,
            created_by_username=model.created_by_username,
            created_by_email=model.created_by_email
        )
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_entity(db_model)
    
    def delete(self, model_id: int) -> bool:
        """모델 삭제"""
        try:
            db_model = self.db.query(StagingModelORM).filter(StagingModelORM.id == model_id).first()
            if db_model:
                self.db.delete(db_model)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingModelORM) -> StagingModel:
        return StagingModel(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            vehicle_line_id=orm.vehicle_line_id,
            release_year=orm.release_year,
            price=orm.price,
            foreign=orm.foreign,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingTrimRepository:
    """SQLAlchemy 기반 Staging 트림 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, trim_id: int) -> Optional[StagingTrim]:
        db_trim = self.db.query(StagingTrimORM).filter(StagingTrimORM.id == trim_id).first()
        return self._to_entity(db_trim) if db_trim else None
    
    def find_by_model_and_name(self, model_id: int, name: str) -> Optional[StagingTrim]:
        db_trim = self.db.query(StagingTrimORM).filter(
            StagingTrimORM.model_id == model_id,
            StagingTrimORM.name == name
        ).first()
        return self._to_entity(db_trim) if db_trim else None
    
    def find_all_by_model(self, model_id: int) -> List[StagingTrim]:
        db_trims = self.db.query(StagingTrimORM).filter(StagingTrimORM.model_id == model_id).all()
        return [self._to_entity(t) for t in db_trims]
    
    def count(self) -> int:
        return self.db.query(StagingTrimORM).count()
    
    def find_all_by_version(self, version_id: int) -> List[StagingTrim]:
        db_trims = self.db.query(StagingTrimORM).filter(StagingTrimORM.version_id == version_id).all()
        return [self._to_entity(t) for t in db_trims]
    
    def save(self, trim: StagingTrim) -> StagingTrim:
        db_trim = StagingTrimORM(
            name=trim.name,
            car_type=trim.car_type,
            fuel_name=trim.fuel_name,
            cc=trim.cc,
            base_price=trim.base_price,
            description=trim.description,
            model_id=trim.model_id,
            created_by=trim.created_by,
            created_by_username=trim.created_by_username,
            created_by_email=trim.created_by_email
        )
        self.db.add(db_trim)
        self.db.commit()
        self.db.refresh(db_trim)
        return self._to_entity(db_trim)
    
    def delete(self, trim_id: int) -> bool:
        """트림 삭제"""
        try:
            db_trim = self.db.query(StagingTrimORM).filter(StagingTrimORM.id == trim_id).first()
            if db_trim:
                self.db.delete(db_trim)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingTrimORM) -> StagingTrim:
        return StagingTrim(
            id=orm.id,
            name=orm.name,
            car_type=orm.car_type,
            fuel_name=orm.fuel_name,
            cc=orm.cc,
            base_price=orm.base_price,
            description=orm.description,
            model_id=orm.model_id,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingOptionTitleRepository:
    """SQLAlchemy 기반 Staging 옵션 타이틀 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, title_id: int) -> Optional[StagingOptionTitle]:
        db_title = self.db.query(StagingOptionTitleORM).filter(StagingOptionTitleORM.id == title_id).first()
        return self._to_entity(db_title) if db_title else None
    
    def find_by_trim_and_name(self, trim_id: int, name: str) -> Optional[StagingOptionTitle]:
        db_title = self.db.query(StagingOptionTitleORM).filter(
            StagingOptionTitleORM.trim_id == trim_id,
            StagingOptionTitleORM.name == name
        ).first()
        return self._to_entity(db_title) if db_title else None
    
    def find_all_by_trim(self, trim_id: int) -> List[StagingOptionTitle]:
        db_titles = self.db.query(StagingOptionTitleORM).filter(StagingOptionTitleORM.trim_id == trim_id).all()
        return [self._to_entity(t) for t in db_titles]
    
    def find_all_by_version(self, version_id: int) -> List[StagingOptionTitle]:
        db_titles = self.db.query(StagingOptionTitleORM).filter(StagingOptionTitleORM.version_id == version_id).all()
        return [self._to_entity(t) for t in db_titles]
    
    def save(self, title: StagingOptionTitle) -> StagingOptionTitle:
        db_title = StagingOptionTitleORM(
            name=title.name,
            description=title.description,
            category=title.category,
            trim_id=title.trim_id,
            created_by=title.created_by,
            created_by_username=title.created_by_username,
            created_by_email=title.created_by_email
        )
        self.db.add(db_title)
        self.db.commit()
        self.db.refresh(db_title)
        return self._to_entity(db_title)
    
    def delete(self, title_id: int) -> bool:
        """옵션 타이틀 삭제"""
        try:
            db_title = self.db.query(StagingOptionTitleORM).filter(StagingOptionTitleORM.id == title_id).first()
            if db_title:
                self.db.delete(db_title)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingOptionTitleORM) -> StagingOptionTitle:
        return StagingOptionTitle(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category=orm.category,
            trim_id=orm.trim_id,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


class SQLAlchemyStagingOptionPriceRepository:
    """SQLAlchemy 기반 Staging 옵션 가격 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, price_id: int) -> Optional[StagingOptionPrice]:
        db_price = self.db.query(StagingOptionPriceORM).filter(StagingOptionPriceORM.id == price_id).first()
        return self._to_entity(db_price) if db_price else None
    
    def find_by_title_and_name(self, title_id: int, name: str) -> Optional[StagingOptionPrice]:
        db_price = self.db.query(StagingOptionPriceORM).filter(
            StagingOptionPriceORM.option_title_id == title_id,
            StagingOptionPriceORM.name == name
        ).first()
        return self._to_entity(db_price) if db_price else None
    
    def find_all_by_title(self, title_id: int) -> List[StagingOptionPrice]:
        db_prices = self.db.query(StagingOptionPriceORM).filter(StagingOptionPriceORM.option_title_id == title_id).all()
        return [self._to_entity(p) for p in db_prices]
    
    def find_all_by_version(self, version_id: int) -> List[StagingOptionPrice]:
        db_prices = self.db.query(StagingOptionPriceORM).filter(StagingOptionPriceORM.version_id == version_id).all()
        return [self._to_entity(p) for p in db_prices]
    
    def save(self, price: StagingOptionPrice) -> StagingOptionPrice:
        db_price = StagingOptionPriceORM(
            name=price.name,
            code=price.code,
            description=price.description,
            price=price.price,
            discounted_price=price.discounted_price,
            option_title_id=price.option_title_id,
            created_by=price.created_by,
            created_by_username=price.created_by_username,
            created_by_email=price.created_by_email
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return self._to_entity(db_price)
    
    def delete(self, price_id: int) -> bool:
        """옵션 가격 삭제"""
        try:
            db_price = self.db.query(StagingOptionPriceORM).filter(StagingOptionPriceORM.id == price_id).first()
            if db_price:
                self.db.delete(db_price)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    @staticmethod
    def _to_entity(orm: StagingOptionPriceORM) -> StagingOptionPrice:
        return StagingOptionPrice(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            description=orm.description,
            price=orm.price,
            discounted_price=orm.discounted_price,
            option_title_id=orm.option_title_id,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )


# ===== 새로운 Staging Option Repository =====

class SQLAlchemyStagingOptionRepository(StagingOptionRepository):
    """SQLAlchemy 기반 Staging 옵션 저장소 - 통합된 옵션 관리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, option_id: int) -> Optional[StagingOption]:
        db_option = self.db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        return self._to_entity(db_option) if db_option else None
    
    def find_by_trim_and_name(self, trim_id: int, name: str) -> Optional[StagingOption]:
        db_option = self.db.query(StagingOptionORM).filter(
            StagingOptionORM.trim_id == trim_id,
            StagingOptionORM.name == name
        ).first()
        return self._to_entity(db_option) if db_option else None
    
    def count(self) -> int:
        return self.db.query(StagingOptionORM).count()
    
    def find_all_by_trim(self, trim_id: int, skip: int = 0, limit: int = 100) -> List[StagingOption]:
        db_options = self.db.query(StagingOptionORM).filter(
            StagingOptionORM.trim_id == trim_id
        ).offset(skip).limit(limit).all()
        return [self._to_entity(option) for option in db_options]
    
    def save(self, option: StagingOption) -> StagingOption:
        db_option = self._to_orm(option)
        self.db.add(db_option)
        self.db.commit()
        self.db.refresh(db_option)
        return self._to_entity(db_option)
    
    def update(self, option_id: int, option: StagingOption) -> Optional[StagingOption]:
        db_option = self.db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        if not db_option:
            return None
        
        # 업데이트
        db_option.name = option.name
        db_option.code = option.code
        db_option.description = option.description
        db_option.category = option.category
        db_option.price = option.price
        db_option.discounted_price = option.discounted_price
        db_option.updated_by_username = option.updated_by_username
        db_option.updated_by_email = option.updated_by_email
        
        self.db.commit()
        self.db.refresh(db_option)
        return self._to_entity(db_option)
    
    def delete(self, option_id: int) -> bool:
        db_option = self.db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        if not db_option:
            return False
        
        self.db.delete(db_option)
        self.db.commit()
        return True
    
    def _to_entity(self, orm: StagingOptionORM) -> StagingOption:
        """ORM을 엔티티로 변환"""
        return StagingOption(
            id=orm.id,
            name=orm.name,
            trim_id=orm.trim_id,
            code=orm.code,
            description=orm.description,
            category=orm.category,
            price=orm.price,
            discounted_price=orm.discounted_price,
            created_by=orm.created_by,
            created_by_username=orm.created_by_username,
            created_by_email=orm.created_by_email,
            created_at=orm.created_at,
            updated_by_username=orm.updated_by_username,
            updated_by_email=orm.updated_by_email,
            updated_at=orm.updated_at
        )
    
    def _to_orm(self, entity: StagingOption) -> StagingOptionORM:
        """엔티티를 ORM으로 변환"""
        return StagingOptionORM(
            name=entity.name,
            trim_id=entity.trim_id,
            code=entity.code,
            description=entity.description,
            category=entity.category,
            price=entity.price,
            discounted_price=entity.discounted_price,
            created_by=entity.created_by,
            created_by_username=entity.created_by_username,
            created_by_email=entity.created_by_email,
            created_at=entity.created_at,
            updated_by_username=entity.updated_by_username,
            updated_by_email=entity.updated_by_email,
            updated_at=entity.updated_at
        )


# Export all repositories
__all__ = [
    'SQLAlchemyUserRepository',
    'SQLAlchemyBrandRepository',
    'SQLAlchemyModelRepository', 
    'SQLAlchemyTrimRepository',
    'SQLAlchemyVehicleLineRepository',
    'SQLAlchemyOptionRepository',
    'SQLAlchemyStagingBrandRepository',
    'SQLAlchemyStagingVehicleLineRepository',
    'SQLAlchemyStagingModelRepository',
    'SQLAlchemyStagingTrimRepository',
    'SQLAlchemyStagingOptionRepository',
    'SQLAlchemyStagingVersionRepository',
    'SQLAlchemyEventRepository',
    'SQLAlchemyEventRegistrationRepository'
]