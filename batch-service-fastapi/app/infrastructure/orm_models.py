"""
SQLAlchemy ORM Models - 인프라 레이어
제시된 구조에 맞게 재설계된 테이블 구조
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum as SQLEnum, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from ..domain.entities import (
    CarType, JobStatus, JobType, ApprovalStatus, VersionStatus, UserRole, UserStatus, UserPosition, 
    ResourceType, ActionType, EventType, EventStatus, PolicyType, EventTypeForPrePurchase
)


# ===== 사용자 테이블 (RBAC) =====

class UserORM(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)  # 실제 이름 (중복 가능)
    email = Column(String(100), nullable=False, unique=True, index=True)  # 로그인 ID (중복 불가)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default="USER")
    position = Column(String(20), nullable=False, default="EMPLOYEE")
    status = Column(String(20), nullable=False, default="ACTIVE")
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계
    user_roles = relationship("UserRoleORM", foreign_keys="UserRoleORM.user_id", back_populates="user")
    user_permissions = relationship("UserPermissionORM", foreign_keys="UserPermissionORM.user_id")


class PermissionORM(Base):
    """권한 테이블"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    resource = Column(String(100), nullable=False)  # 리소스 (예: main_carsystem)
    action = Column(String(50), nullable=False)     # 액션 (예: read, write, cdc)
    description = Column(Text, nullable=True)
    
    # 관계
    role_permissions = relationship("RolePermissionORM", back_populates="permission")


class RoleORM(Base):
    """역할 테이블"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)  # 시스템 기본 역할
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 역할 생성자
    
    # 관계
    user_roles = relationship("UserRoleORM", back_populates="role")
    role_permissions = relationship("RolePermissionORM", back_populates="role")


class UserRoleORM(Base):
    """사용자-역할 연결 테이블"""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 역할을 부여한 사용자
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 관계
    user = relationship("UserORM", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("RoleORM", back_populates="user_roles")
    assigned_by_user = relationship("UserORM", foreign_keys=[assigned_by])


class RolePermissionORM(Base):
    """역할-권한 연결 테이블"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 권한을 부여한 사용자
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 관계
    role = relationship("RoleORM", back_populates="role_permissions")
    permission = relationship("PermissionORM", back_populates="role_permissions")
    granted_by_user = relationship("UserORM", foreign_keys=[granted_by])


class UserPermissionORM(Base):
    """사용자-권한 직접 연결 테이블 (실제 권한)"""
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_name = Column(String(100), nullable=False)  # excel_upload, excel_search 등
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 권한을 부여한 사용자
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 관계
    user = relationship("UserORM", foreign_keys=[user_id])
    granted_by_user = relationship("UserORM", foreign_keys=[granted_by])


# ===== Version Management Layer =====

class StagingVersionORM(Base):
    """Staging 버전 관리 테이블 - 버전 단위로 승인 관리"""
    __tablename__ = "staging_version"
    
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # 승인 상태 관리 (버전 단위)
    approval_status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_by = Column(String(100), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False, default="system")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 통계 정보는 동적으로 계산 (데이터베이스 필드 제거)
    
    # 관계 설정 - 직접 참조로 단순화
    brands = relationship("StagingBrandORM", back_populates="version", cascade="all, delete-orphan")


# ===== Staging Layer (임시 데이터) =====

class StagingBrandORM(Base):
    """임시 브랜드 테이블 - version_id로 직접 참조"""
    __tablename__ = "staging_brand"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(50), nullable=False)
    version_id = Column(Integer, ForeignKey("staging_version.id"), nullable=False)  # 버전에 직접 속함
    logo_url = Column(String(500), nullable=True)
    manager = Column(String(100), nullable=True)  # 브랜드 관리자
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False, default="batch_service")
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    version = relationship("StagingVersionORM", back_populates="brands")
    vehicle_lines = relationship("StagingVehicleLineORM", back_populates="brand", cascade="all, delete-orphan")


class StagingVehicleLineORM(Base):
    """임시 차량 라인 테이블 - 브랜드와 모델 사이의 중간 계층"""
    __tablename__ = "staging_vehicle_line"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 예: 아반떼, 소나타, 그랜저
    description = Column(Text, nullable=True)
    brand_id = Column(Integer, ForeignKey("staging_brand.id"), nullable=False)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False, default="batch_service")
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    brand = relationship("StagingBrandORM", back_populates="vehicle_lines")
    models = relationship("StagingModelORM", back_populates="vehicle_line", cascade="all, delete-orphan")


class StagingModelORM(Base):
    """임시 모델 테이블 - vehicle_line_id로 참조"""
    __tablename__ = "staging_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 예: 아반떼 LPI, 아반떼 하이브리드
    code = Column(String(100), nullable=False)
    vehicle_line_id = Column(Integer, ForeignKey("staging_vehicle_line.id"), nullable=False)
    release_year = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    foreign = Column(Boolean, nullable=True, default=False)  # 외제차 여부
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False, default="batch_service")
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    vehicle_line = relationship("StagingVehicleLineORM", back_populates="models")
    trims = relationship("StagingTrimORM", back_populates="model", cascade="all, delete-orphan")


class StagingTrimORM(Base):
    """임시 트림 테이블"""
    __tablename__ = "staging_trim"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 예: 모던, 프리미엄, 스포츠
    car_type = Column(String(50), nullable=False)  # CarType enum 값
    fuel_name = Column(String(100), nullable=True)
    cc = Column(String(50), nullable=True)
    base_price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    model_id = Column(Integer, ForeignKey("staging_model.id"), nullable=False)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False, default="batch_service")
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    model = relationship("StagingModelORM", back_populates="trims")
    options = relationship("StagingOptionORM", back_populates="trim", cascade="all, delete-orphan")
    option_titles = relationship("StagingOptionTitleORM", back_populates="trim", cascade="all, delete-orphan")  # 호환성 유지


class StagingOptionORM(Base):
    """Staging 옵션 테이블 - 옵션 이름과 가격을 하나로 통합"""
    __tablename__ = "staging_option"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 옵션 이름
    code = Column(String(100), nullable=True)   # 옵션 코드
    description = Column(Text, nullable=True)   # 옵션 설명
    category = Column(String(100), nullable=True)  # 옵션 카테고리 (기존 OptionGroup)
    price = Column(Integer, nullable=True)      # 옵션 가격
    discounted_price = Column(Integer, nullable=True)  # 할인 가격
    trim_id = Column(Integer, ForeignKey("staging_trim.id"), nullable=False)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False)
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    trim = relationship("StagingTrimORM", back_populates="options")


# 기존 테이블들 - 호환성을 위해 유지 (마이그레이션 후 제거 예정)
class StagingOptionTitleORM(Base):
    """Staging 옵션 타이틀 테이블 - 호환성을 위해 유지"""
    __tablename__ = "staging_option_title"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    trim_id = Column(Integer, ForeignKey("staging_trim.id"), nullable=False)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False)
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    trim = relationship("StagingTrimORM", back_populates="option_titles")
    option_prices = relationship("StagingOptionPriceORM", back_populates="option_title", cascade="all, delete-orphan")


class StagingOptionPriceORM(Base):
    """Staging 옵션 가격 테이블 - 호환성을 위해 유지"""
    __tablename__ = "staging_option_price"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    discounted_price = Column(Integer, nullable=True)
    option_title_id = Column(Integer, ForeignKey("staging_option_title.id"), nullable=False)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=False)
    created_by_username = Column(String(100), nullable=True)
    created_by_email = Column(String(100), nullable=False, default="batch_service")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    # 수정자 정보
    updated_by_username = Column(String(100), nullable=True)
    updated_by_email = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계 설정
    option_title = relationship("StagingOptionTitleORM", back_populates="option_prices")


# ===== Main (Production) Layer =====

class BrandORM(Base):
    """브랜드 메인 테이블"""
    __tablename__ = "brand"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(50), nullable=False)
    logo_url = Column(String(500), nullable=True)
    manager = Column(String(100), nullable=True)  # 브랜드 관리자
    
    # 관계
    vehicle_lines = relationship("VehicleLineORM", back_populates="brand", cascade="all, delete-orphan")


class VehicleLineORM(Base):
    """차량 라인 메인 테이블"""
    __tablename__ = "vehicle_line"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)
    
    # 관계
    brand = relationship("BrandORM", back_populates="vehicle_lines")
    models = relationship("ModelORM", back_populates="vehicle_line", cascade="all, delete-orphan")


class ModelORM(Base):
    """모델 메인 테이블"""
    __tablename__ = "model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)  # 모델 설명 추가
    vehicle_line_id = Column(Integer, ForeignKey("vehicle_line.id"), nullable=False)
    release_year = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    foreign = Column(Boolean, nullable=True, default=False)  # 외제차 여부
    
    # 관계
    vehicle_line = relationship("VehicleLineORM", back_populates="models")
    trims = relationship("TrimORM", back_populates="model", cascade="all, delete-orphan")


class TrimORM(Base):
    """트림 메인 테이블"""
    __tablename__ = "trim"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    car_type = Column(String(50), nullable=False)  # CarType enum 값
    fuel_name = Column(String(100), nullable=True)
    cc = Column(String(50), nullable=True)
    base_price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    model_id = Column(Integer, ForeignKey("model.id"), nullable=False)
    
    # 관계
    model = relationship("ModelORM", back_populates="trims")
    car_colors = relationship("TrimCarColorORM", back_populates="trim", cascade="all, delete-orphan")
    options = relationship("OptionORM", back_populates="trim", cascade="all, delete-orphan")
    option_titles = relationship("OptionTitleORM", back_populates="trim", cascade="all, delete-orphan")


class TrimCarColorORM(Base):
    """트림 색상 메인 테이블"""
    __tablename__ = "trim_car_color"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    color_code = Column(String(50), nullable=True)
    additional_price = Column(Integer, nullable=True)
    vehicle_interior = Column(Boolean, default=False)
    trim_id = Column(Integer, ForeignKey("trim.id"), nullable=False)
    
    # 관계
    trim = relationship("TrimORM", back_populates="car_colors")


class OptionORM(Base):
    """옵션 메인 테이블 - 옵션 이름과 가격을 하나로 통합"""
    __tablename__ = "option"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 옵션 이름
    code = Column(String(100), nullable=True)   # 옵션 코드
    description = Column(Text, nullable=True)   # 옵션 설명
    price = Column(Integer, nullable=True)      # 옵션 가격
    discounted_price = Column(Integer, nullable=True)  # 할인 가격
    category = Column(String(100), nullable=True)  # 옵션 카테고리
    trim_id = Column(Integer, ForeignKey("trim.id"), nullable=False)
    
    # 관계
    trim = relationship("TrimORM", back_populates="options")

# 호환성을 위해 기존 모델들 유지 (사용하지 않음)
class OptionTitleORM(Base):
    """옵션 타이틀 메인 테이블 - 호환성을 위해 유지"""
    __tablename__ = "option_title"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    trim_id = Column(Integer, ForeignKey("trim.id"), nullable=False)
    
    # 관계
    trim = relationship("TrimORM", back_populates="option_titles")
    option_prices = relationship("OptionPriceORM", back_populates="option_title", cascade="all, delete-orphan")


class OptionPriceORM(Base):
    """옵션 가격 메인 테이블 - 호환성을 위해 유지"""
    __tablename__ = "option_price"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    discounted_price = Column(Integer, nullable=True)
    option_title_id = Column(Integer, ForeignKey("option_title.id"), nullable=False)
    
    # 관계
    option_title = relationship("OptionTitleORM", back_populates="option_prices")


# ===== Batch / Job Layer =====

class BatchJobORM(Base):
    """배치 작업 테이블 - 작업 상태 추적"""
    __tablename__ = "batch_job"
    
    id = Column(Integer, primary_key=True, index=True)  # 기존 테이블 구조에 맞춰 Integer로 유지
    job_type = Column(String(20), nullable=False)  # JobType enum 값
    status = Column(String(20), nullable=False, default="PENDING")  # JobStatus enum 값
    task_id = Column(String(100), nullable=True, unique=False, index=True)  # Celery Task ID (nullable) (UUID)
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)


# ===== Event Management =====

class EventORM(Base):
    """이벤트 테이블"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(SQLEnum(EventType), nullable=False, default=EventType.PROMOTION)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    
    # 이벤트 기간
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # 이벤트 위치
    location = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    
    # 이벤트 상세 정보
    max_participants = Column(Integer, nullable=True)
    current_participants = Column(Integer, nullable=False, default=0)
    registration_fee = Column(Integer, nullable=True)
    
    # 관련 차량 (선택사항)
    related_brand_id = Column(Integer, nullable=True)
    related_model_id = Column(Integer, nullable=True)
    
    # 생성자 정보
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계
    registrations = relationship("EventRegistrationORM", back_populates="event", cascade="all, delete-orphan")


class EventRegistrationORM(Base):
    """이벤트 등록 테이블"""
    __tablename__ = "event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 추가 정보
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # 상태
    status = Column(String(20), nullable=False, default="confirmed")
    
    # 관계
    event = relationship("EventORM", back_populates="registrations")
    user = relationship("UserORM", foreign_keys=[user_id])


# ===== 할인 정책 관리 =====

class DiscountPolicyORM(Base):
    """할인 정책 허브 테이블 - 브랜드, 트림, 버전 단위"""
    __tablename__ = "discount_policy"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)
    trim_id = Column(Integer, ForeignKey("trim.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("staging_version.id"), nullable=False)
    policy_type = Column(SQLEnum(PolicyType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 관계
    brand = relationship("BrandORM", foreign_keys=[brand_id])
    trim = relationship("TrimORM", foreign_keys=[trim_id])
    version = relationship("StagingVersionORM", foreign_keys=[version_id])
    
    # 할인 유형별 관계
    card_benefits = relationship("BrandCardBenefitORM", back_populates="policy", cascade="all, delete-orphan")
    promos = relationship("BrandPromoORM", back_populates="policy", cascade="all, delete-orphan")
    inventory_discounts = relationship("BrandInventoryDiscountORM", back_populates="policy", cascade="all, delete-orphan")
    pre_purchases = relationship("BrandPrePurchaseORM", back_populates="policy", cascade="all, delete-orphan")


class BrandCardBenefitORM(Base):
    """카드사 제휴 할인 테이블"""
    __tablename__ = "brand_card_benefit"
    
    id = Column(Integer, primary_key=True, index=True)
    discount_policy_id = Column(Integer, ForeignKey("discount_policy.id"), nullable=False)
    card_partner = Column(String(255), nullable=False)
    cashback_rate = Column(String(5), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 관계
    policy = relationship("DiscountPolicyORM", back_populates="card_benefits")


class BrandPromoORM(Base):
    """브랜드 프로모션 할인 테이블"""
    __tablename__ = "brand_promo"
    
    id = Column(Integer, primary_key=True, index=True)
    discount_policy_id = Column(Integer, ForeignKey("discount_policy.id"), nullable=False)
    discount_rate = Column(String(5), nullable=True)
    discount_amount = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 관계
    policy = relationship("DiscountPolicyORM", back_populates="promos")


class BrandInventoryDiscountORM(Base):
    """재고 보유 할인 테이블"""
    __tablename__ = "brand_inventory_discount"
    
    id = Column(Integer, primary_key=True, index=True)
    discount_policy_id = Column(Integer, ForeignKey("discount_policy.id"), nullable=False)
    inventory_level_threshold = Column(Integer, nullable=False)
    discount_rate = Column(String(5), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 관계
    policy = relationship("DiscountPolicyORM", back_populates="inventory_discounts")


class BrandPrePurchaseORM(Base):
    """선구매/특가 할인 테이블"""
    __tablename__ = "brand_pre_purchase"
    
    id = Column(Integer, primary_key=True, index=True)
    discount_policy_id = Column(Integer, ForeignKey("discount_policy.id"), nullable=False)
    event_type = Column(SQLEnum(EventTypeForPrePurchase), nullable=False)
    discount_rate = Column(String(5), nullable=True)
    discount_amount = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    pre_purchase_start = Column(DateTime, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 관계
    policy = relationship("DiscountPolicyORM", back_populates="pre_purchases")