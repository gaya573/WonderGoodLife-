"""
Domain Entities - 비즈니스 엔티티
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime
import hashlib


class CarType(str, Enum):
    """차량 타입"""
    COMPACT = "경_소형승용"
    MIDSIZE = "중형승용"
    FULLSIZE = "대형승용"
    SUV_RV = "SUV_RV"
    TRUCK_VAN = "화물_승합"


class JobStatus(str, Enum):
    """작업 상태"""
    PENDING = "PENDING"      # 대기 중
    PROCESSING = "PROCESSING"  # 처리 중
    COMPLETED = "COMPLETED"   # 완료
    FAILED = "FAILED"        # 실패


class JobType(str, Enum):
    """작업 타입"""
    EXCEL_IMPORT = "EXCEL_IMPORT"  # 엑셀 업로드
    WEB_CRAWLING = "WEB_CRAWLING"  # 웹 크롤링


class ApprovalStatus(str, Enum):
    """승인 상태"""
    PENDING = "PENDING"      # 승인 대기
    APPROVED = "APPROVED"    # 승인됨
    REJECTED = "REJECTED"    # 거부됨


class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "ADMIN"          # 관리자
    USER = "USER"            # 일반 사용자


class UserPosition(str, Enum):
    """사용자 직급"""
    CEO = "CEO"              # 대표
    MANAGER = "MANAGER"      # 부장
    EMPLOYEE = "EMPLOYEE"    # 사원



class UserStatus(str, Enum):
    """사용자 상태"""
    ACTIVE = "ACTIVE"        # 활성
    INACTIVE = "INACTIVE"    # 비활성
    SUSPENDED = "SUSPENDED"  # 정지


class ResourceType(str, Enum):
    """리소스 타입"""
    MAIN_CARSYSTEM = "main_carsystem"       # 메인 자동차 시스템
    DEMO_CARSYSTEM = "demo_carsystem"       # 데모 자동차 시스템
    STAGING_DATA = "staging_data"           # Staging 데이터
    USER_MANAGEMENT = "user_management"     # 사용자 관리
    USER_ROLE = "user_role"                 # 사용자 권한 관리
    SYSTEM_ADMIN = "system_admin"           # 시스템 관리
    EVENT_DATA = "event_data"               # 이벤트 데이터


class ActionType(str, Enum):
    """액션 타입"""
    READ = "read"                           # 조회
    WRITE = "write"                         # 생성/수정
    DELETE = "delete"                       # 삭제
    CDC = "cdc"                             # 마이그레이션
    ADMIN = "admin"                         # 관리


# ===== 사용자 엔티티 =====

@dataclass
class User:
    """사용자 엔티티"""
    username: str
    email: str
    password_hash: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.USER
    position: UserPosition = UserPosition.EMPLOYEE
    status: UserStatus = UserStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.username or len(self.username.strip()) < 3:
            raise ValueError("사용자명은 3자 이상이어야 합니다")
        if not self.email or "@" not in self.email:
            raise ValueError("올바른 이메일 주소를 입력하세요")
        if not self.password_hash:
            raise ValueError("비밀번호 해시는 필수입니다")
        if self.phone_number and len(self.phone_number.replace("-", "").replace(" ", "")) < 10:
            raise ValueError("올바른 전화번호를 입력하세요")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """비밀번호 검증"""
        return self.password_hash == self.hash_password(password)
    
    def is_admin(self) -> bool:
        """관리자 여부 확인"""
        return self.role == UserRole.ADMIN
    
    def is_active(self) -> bool:
        """활성 사용자 여부 확인"""
        return self.status == UserStatus.ACTIVE
    
    def get_position_name(self) -> str:
        """직급명 반환"""
        position_names = {
            UserPosition.CEO: "대표관리",
            UserPosition.MANAGER: "부장관리",
            UserPosition.EMPLOYEE: "사원"
        }
        return position_names.get(self.position, "알 수 없음")
    
    def is_ceo(self) -> bool:
        """대표관리 여부 확인"""
        return self.position == UserPosition.CEO


@dataclass
class Permission:
    """권한 엔티티"""
    resource: str  # 리소스 (예: main_carsystem)
    action: str    # 액션 (예: read, write, cdc)
    description: Optional[str] = None
    id: Optional[int] = None
    
    def get_permission_string(self) -> str:
        """권한 문자열 반환 (예: main_carsystem_read)"""
        return f"{self.resource}_{self.action}"


@dataclass
class Role:
    """역할 엔티티"""
    name: str
    description: Optional[str] = None
    is_system_role: bool = False  # 시스템 기본 역할 여부
    created_by: Optional[int] = None  # 역할 생성자 (대표관리만)
    id: Optional[int] = None


@dataclass
class UserRoleAssignment:
    """사용자-역할 연결 엔티티"""
    user_id: int
    role_id: int
    assigned_by: int  # 역할을 부여한 사용자 ID (대표관리만)
    assigned_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class RolePermission:
    """역할-권한 연결 엔티티"""
    role_id: int
    permission_id: int
    granted_by: int  # 권한을 부여한 사용자 ID (대표관리만)
    granted_at: Optional[datetime] = None
    id: Optional[int] = None


# ===== Staging 엔티티 (임시 데이터) =====

@dataclass
class StagingBrand:
    """임시 브랜드 데이터"""
    name: str
    country: str
    version_id: int  # 버전에 속함
    logo_url: Optional[str] = None
    manager: Optional[str] = None  # 브랜드 관리자
    
    # 생성자 정보
    created_by: str = "batch_service"  # 하위 호환성 유지
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("브랜드 이름은 필수입니다")
        if not self.country or len(self.country) != 2:
            raise ValueError("국가 코드는 2자리여야 합니다 (예: KR, US)")


@dataclass
class StagingVehicleLine:
    """임시 차량 라인 데이터"""
    name: str
    brand_id: int
    description: Optional[str] = None
    
    # 생성자 정보
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("차량 라인 이름은 필수입니다")


@dataclass
class StagingModel:
    """임시 모델 데이터"""
    name: str
    code: str
    vehicle_line_id: int  # vehicle_line 참조로 변경
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: Optional[bool] = False  # 외제차 여부
    
    # 생성자 정보
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("모델 이름은 필수입니다")
        if not self.code:
            raise ValueError("모델 코드는 필수입니다")


@dataclass
class StagingTrim:
    """임시 트림 데이터"""
    name: str
    car_type: CarType
    model_id: int
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    
    # 생성자 정보
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("트림 이름은 필수입니다")


@dataclass
class StagingOption:
    """Staging 옵션 엔티티 - 옵션 이름과 가격을 하나로 통합"""
    name: str
    trim_id: int
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None  # 기존 OptionGroup
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("옵션 이름은 필수입니다")


# 기존 엔티티들 - 호환성을 위해 유지 (마이그레이션 후 제거 예정)
@dataclass
class StagingOptionTitle:
    """Staging 옵션 타이틀 엔티티 - 호환성을 위해 유지"""
    name: str
    trim_id: int
    description: Optional[str] = None
    category: Optional[str] = None
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("옵션 타이틀 이름은 필수입니다")


@dataclass
class StagingOptionPrice:
    """Staging 옵션 가격 엔티티 - 호환성을 위해 유지"""
    name: str
    option_title_id: int
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    created_by: str = "batch_service"
    created_by_username: Optional[str] = None
    created_by_email: str = "batch_service"
    created_at: Optional[datetime] = None
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("옵션 가격 이름은 필수입니다")


# ===== 메인 엔티티 (승인 후 CDC로 전송될 데이터) =====

@dataclass
class Brand:
    """브랜드 도메인 엔티티"""
    name: str
    country: str
    logo_url: Optional[str] = None
    manager: Optional[str] = None  # 브랜드 관리자
    id: Optional[int] = None


@dataclass
class VehicleLine:
    """차량 라인 도메인 엔티티"""
    name: str
    brand_id: int
    description: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Model:
    """모델 도메인 엔티티"""
    name: str
    code: str
    vehicle_line_id: int  # vehicle_line 참조로 변경
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: Optional[bool] = False  # 외제차 여부
    id: Optional[int] = None


@dataclass
class Trim:
    """트림 도메인 엔티티"""
    name: str
    car_type: CarType
    model_id: int
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    id: Optional[int] = None


@dataclass
class TrimCarColor:
    """트림 색상 도메인 엔티티"""
    name: str
    trim_id: int
    color_code: Optional[str] = None
    additional_price: Optional[int] = None
    vehicle_interior: bool = False
    id: Optional[int] = None


@dataclass
class OptionTitle:
    """옵션 그룹 도메인 엔티티"""
    name: str
    trim_id: int
    description: Optional[str] = None
    category: Optional[str] = None
    id: Optional[int] = None


@dataclass
class OptionPrice:
    """옵션 가격 도메인 엔티티"""
    name: str
    option_title_id: int
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    id: Optional[int] = None


@dataclass
class BatchJob:
    """배치 작업 엔티티"""
    job_type: JobType
    status: JobStatus
    task_id: str  # Celery Task ID
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_rows: int = 0
    processed_rows: int = 0
    error_message: Optional[str] = None
    result_data: Optional[dict] = None
    id: Optional[int] = None


# ===== Version Management =====

class VersionStatus(str, Enum):
    DRAFT = "DRAFT"          # 초안
    PENDING = "PENDING"      # 검토 대기
    APPROVED = "APPROVED"    # 승인됨
    MIGRATED = "MIGRATED"    # 마이그레이션 완료
    REJECTED = "REJECTED"    # 거부됨


@dataclass
class StagingVersion:
    """Staging 데이터 버전 관리 - 버전 단위 승인 관리"""
    version_name: str
    description: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING  # 버전 단위 승인 상태
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_by: str = "system"
    # 통계 필드는 동적으로 계산 (엔티티에서 제거)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None

    def validate(self):
        """버전 데이터 검증"""
        if not self.version_name or len(self.version_name.strip()) == 0:
            raise ValueError("버전명은 필수입니다")
        if len(self.version_name) > 100:
            raise ValueError("버전명은 100자를 초과할 수 없습니다")
        if self.description and len(self.description) > 500:
            raise ValueError("설명은 500자를 초과할 수 없습니다")
    
    def is_approved(self) -> bool:
        """승인 상태 확인"""
        return self.approval_status == ApprovalStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """거부 상태 확인"""
        return self.approval_status == ApprovalStatus.REJECTED


# ===== Event Management =====

class EventType(str, Enum):
    """이벤트 타입"""
    PROMOTION = "promotion"           # 프로모션
    EXHIBITION = "exhibition"         # 전시회
    TEST_DRIVE = "test_drive"         # 시승
    LAUNCH = "launch"                 # 신차 출시
    SALE = "sale"                     # 세일
    CUSTOMER_EVENT = "customer_event" # 고객 이벤트


class EventStatus(str, Enum):
    """이벤트 상태"""
    DRAFT = "DRAFT"           # 초안
    ACTIVE = "ACTIVE"         # 활성
    INACTIVE = "INACTIVE"     # 비활성
    COMPLETED = "COMPLETED"   # 완료
    CANCELLED = "CANCELLED"   # 취소


@dataclass
class Event:
    """이벤트 도메인 엔티티"""
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.PROMOTION
    status: EventStatus = EventStatus.DRAFT
    
    # 이벤트 기간
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # 이벤트 위치
    location: Optional[str] = None
    address: Optional[str] = None
    
    # 이벤트 상세 정보
    max_participants: Optional[int] = None
    current_participants: int = 0
    registration_fee: Optional[int] = None
    
    # 관련 차량 (선택사항)
    related_brand_id: Optional[int] = None
    related_model_id: Optional[int] = None
    
    # 생성자 정보
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        """이벤트 데이터 검증"""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("이벤트 제목은 필수입니다")
        if len(self.title) > 200:
            raise ValueError("이벤트 제목은 200자를 초과할 수 없습니다")
        if self.description and len(self.description) > 1000:
            raise ValueError("이벤트 설명은 1000자를 초과할 수 없습니다")
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("이벤트 종료일은 시작일보다 늦어야 합니다")
        if self.max_participants is not None and self.max_participants < 1:
            raise ValueError("최대 참가자 수는 1명 이상이어야 합니다")
        if self.registration_fee is not None and self.registration_fee < 0:
            raise ValueError("등록비는 0원 이상이어야 합니다")
    
    def is_active(self) -> bool:
        """이벤트 활성 상태 확인"""
        return self.status == EventStatus.ACTIVE
    
    def is_ongoing(self) -> bool:
        """이벤트 진행 중 확인"""
        now = datetime.utcnow()
        if not self.start_date or not self.end_date:
            return False
        return self.start_date <= now <= self.end_date
    
    def can_register(self) -> bool:
        """이벤트 등록 가능 여부 확인"""
        return (self.is_active() and 
                self.is_ongoing() and 
                (self.max_participants is None or self.current_participants < self.max_participants))


@dataclass
class EventRegistration:
    """이벤트 등록 도메인 엔티티"""
    event_id: int
    user_id: int
    registration_date: datetime = field(default_factory=datetime.utcnow)
    
    # 추가 정보
    phone_number: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    
    # 상태
    status: str = "confirmed"  # confirmed, cancelled, waitlisted
    
    id: Optional[int] = None
    
    def validate(self) -> None:
        """등록 데이터 검증"""
        if not self.event_id:
            raise ValueError("이벤트 ID는 필수입니다")
        if not self.user_id:
            raise ValueError("사용자 ID는 필수입니다")


# 매핑 테이블 제거 - 직접 참조로 단순화


# ===== 할인 정책 엔티티 =====

class PolicyType(str, Enum):
    """할인 정책 타입"""
    CARD_BENEFIT = "CARD_BENEFIT"      # 카드사 제휴 할인
    BRAND_PROMO = "BRAND_PROMO"       # 브랜드 고유 할인
    INVENTORY = "INVENTORY"           # 재고 보유 할인
    PRE_PURCHASE = "PRE_PURCHASE"     # 선구매/특가 할인


class EventTypeForPrePurchase(str, Enum):
    """선구매 이벤트 타입"""
    PRE_PURCHASE = "PRE_PURCHASE"     # 선구매
    SPECIAL_OFFER = "SPECIAL_OFFER"   # 특가


@dataclass
class StagingDiscountPolicy:
    """할인 정책 허브 엔티티 - 브랜드, Vehicle Line, 트림, 버전 단위"""
    brand_id: int
    vehicle_line_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """정책 데이터 검증"""
        if not self.brand_id:
            raise ValueError("브랜드 ID는 필수입니다")
        if not self.vehicle_line_id:
            raise ValueError("Vehicle Line ID는 필수입니다")
        if not self.trim_id:
            raise ValueError("트림 ID는 필수입니다")
        if not self.version_id:
            raise ValueError("버전 ID는 필수입니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("정책 제목은 필수입니다")
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValueError("유효 종료일은 시작일보다 늦어야 합니다")
    
    def is_valid_now(self) -> bool:
        """현재 유효한 정책인지 확인"""
        if not self.is_active:
            return False
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True


@dataclass
class StagingBrandCardBenefit:
    """카드사 제휴 할인 엔티티"""
    discount_policy_id: int
    card_partner: str
    cashback_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """카드 제휴 데이터 검증"""
        if not self.card_partner or len(self.card_partner.strip()) == 0:
            raise ValueError("카드사명은 필수입니다")
        if self.cashback_rate < 0 or self.cashback_rate > 100:
            raise ValueError("캐시백 비율은 0-100 사이여야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")


@dataclass
class StagingBrandPromo:
    """브랜드 프로모션 할인 엔티티"""
    discount_policy_id: int
    title: str
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """프로모션 데이터 검증"""
        # 할인율과 할인 금액이 모두 None이면 안 됨 (하지만 0은 허용)
        if self.discount_rate is None and self.discount_amount is None:
            raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
        if self.discount_rate is not None and (self.discount_rate < 0 or self.discount_rate > 100):
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if self.discount_amount is not None and self.discount_amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def calculate_discount(self, base_price: int) -> int:
        """할인 금액 계산"""
        if self.discount_amount:
            return self.discount_amount
        if self.discount_rate:
            return int(base_price * self.discount_rate / 100)
        return 0


@dataclass
class StagingBrandInventoryDiscount:
    """재고 보유 할인 엔티티"""
    discount_policy_id: int
    inventory_level_threshold: int
    discount_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """재고 할인 데이터 검증"""
        if self.inventory_level_threshold < 0:
            raise ValueError("재고 기준 수량은 0 이상이어야 합니다")
        if self.discount_rate < 0 or self.discount_rate > 100:
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def is_eligible(self, current_inventory: int) -> bool:
        """재고 기준 충족 여부"""
        return current_inventory >= self.inventory_level_threshold


@dataclass
class StagingBrandPrePurchase:
    """선구매/특가 할인 엔티티"""
    discount_policy_id: int
    event_type: EventTypeForPrePurchase
    title: str
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """선구매 할인 데이터 검증"""
        # 할인율과 할인 금액이 모두 None이면 안 됨 (하지만 0은 허용)
        if self.discount_rate is None and self.discount_amount is None:
            raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
        if self.discount_rate is not None and (self.discount_rate < 0 or self.discount_rate > 100):
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if self.discount_amount is not None and self.discount_amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def calculate_discount(self, base_price: int) -> int:
        """할인 금액 계산"""
        if self.discount_amount:
            return self.discount_amount
        if self.discount_rate:
            return int(base_price * self.discount_rate / 100)
        return 0
    
    def is_pre_purchase_active(self) -> bool:
        """선구매 기간인지 확인"""
        if self.event_type != EventTypeForPrePurchase.PRE_PURCHASE:
            return False
        if not self.pre_purchase_start:
            return False
        now = datetime.utcnow()
        return now >= self.pre_purchase_start and self.is_valid_now()


# ===== Main (Production) 할인 정책 엔티티 =====

@dataclass
class DiscountPolicy:
    """할인 정책 허브 엔티티 - 브랜드, Vehicle Line, 트림 단위"""
    brand_id: int
    vehicle_line_id: int
    trim_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """정책 데이터 검증"""
        if not self.brand_id:
            raise ValueError("브랜드 ID는 필수입니다")
        if not self.vehicle_line_id:
            raise ValueError("Vehicle Line ID는 필수입니다")
        if not self.trim_id:
            raise ValueError("트림 ID는 필수입니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("정책 제목은 필수입니다")
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValueError("유효 종료일은 시작일보다 늦어야 합니다")
    
    def is_valid_now(self) -> bool:
        """현재 유효한 정책인지 확인"""
        if not self.is_active:
            return False
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True


@dataclass
class BrandCardBenefit:
    """카드사 제휴 할인 엔티티"""
    discount_policy_id: int
    card_partner: str
    cashback_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """카드 제휴 데이터 검증"""
        if not self.card_partner or len(self.card_partner.strip()) == 0:
            raise ValueError("카드사명은 필수입니다")
        if self.cashback_rate < 0 or self.cashback_rate > 100:
            raise ValueError("캐시백 비율은 0-100 사이여야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")


@dataclass
class BrandPromo:
    """브랜드 프로모션 할인 엔티티"""
    discount_policy_id: int
    title: str
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """프로모션 데이터 검증"""
        if self.discount_rate is None and self.discount_amount is None:
            raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
        if self.discount_rate is not None and (self.discount_rate < 0 or self.discount_rate > 100):
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if self.discount_amount is not None and self.discount_amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def calculate_discount(self, base_price: int) -> int:
        """할인 금액 계산"""
        if self.discount_amount:
            return self.discount_amount
        if self.discount_rate:
            return int(base_price * self.discount_rate / 100)
        return 0


@dataclass
class BrandInventoryDiscount:
    """재고 보유 할인 엔티티"""
    discount_policy_id: int
    inventory_level_threshold: int
    discount_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """재고 할인 데이터 검증"""
        if self.inventory_level_threshold < 0:
            raise ValueError("재고 기준 수량은 0 이상이어야 합니다")
        if self.discount_rate < 0 or self.discount_rate > 100:
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def is_eligible(self, current_inventory: int) -> bool:
        """재고 기준 충족 여부"""
        return current_inventory >= self.inventory_level_threshold


@dataclass
class BrandPrePurchase:
    """선구매/특가 할인 엔티티"""
    discount_policy_id: int
    event_type: EventTypeForPrePurchase
    title: str
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None
    
    def validate(self) -> None:
        """선구매 할인 데이터 검증"""
        if self.discount_rate is None and self.discount_amount is None:
            raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
        if self.discount_rate is not None and (self.discount_rate < 0 or self.discount_rate > 100):
            raise ValueError("할인율은 0-100 사이여야 합니다")
        if self.discount_amount is not None and self.discount_amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("제목은 필수입니다")
    
    def calculate_discount(self, base_price: int) -> int:
        """할인 금액 계산"""
        if self.discount_amount:
            return self.discount_amount
        if self.discount_rate:
            return int(base_price * self.discount_rate / 100)
        return 0
    
    def is_pre_purchase_active(self) -> bool:
        """선구매 기간인지 확인"""
        if self.event_type != EventTypeForPrePurchase.PRE_PURCHASE:
            return False
        if not self.pre_purchase_start:
            return False
        now = datetime.utcnow()
        return now >= self.pre_purchase_start and self.is_valid_now()
