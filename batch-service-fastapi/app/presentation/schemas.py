"""
API Request/Response Schemas - Pydantic
새로운 구조에 맞게 재설계된 스키마
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..domain.entities import CarType, JobStatus, JobType, ApprovalStatus, VersionStatus, EventType, EventStatus, PolicyType, EventTypeForPrePurchase


# ===== Brand Schemas =====
class BrandRequest(BaseModel):
    name: str
    country: str
    logo_url: Optional[str] = None


class BrandResponse(BaseModel):
    id: int
    name: str
    country: str
    logo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ===== Vehicle Line Schemas =====
class VehicleLineRequest(BaseModel):
    name: str
    description: Optional[str] = None
    brand_id: int


class VehicleLineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    brand_id: int
    
    class Config:
        from_attributes = True


# ===== Model Schemas =====
class ModelRequest(BaseModel):
    name: str
    code: str
    vehicle_line_id: int
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: bool = False


class ModelResponse(BaseModel):
    id: int
    name: str
    code: str
    vehicle_line_id: int
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: bool = False
    
    class Config:
        from_attributes = True


# ===== Trim Schemas =====
class TrimRequest(BaseModel):
    name: str
    car_type: CarType
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    model_id: int


class TrimResponse(BaseModel):
    id: int
    name: str
    car_type: CarType
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    model_id: int
    
    class Config:
        from_attributes = True


# ===== Staging Brand Schemas =====
class StagingBrandCreate(BaseModel):
    """Staging 브랜드 생성 요청"""
    name: str
    country: str
    logo_url: Optional[str] = None
    version_id: int
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingBrandUpdate(BaseModel):
    """Staging 브랜드 수정 요청"""
    name: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None


class StagingBrandResponse(BaseModel):
    """Staging 브랜드 응답"""
    id: int
    name: str
    country: str
    logo_url: Optional[str] = None
    version_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Vehicle Line Schemas =====
class StagingVehicleLineCreate(BaseModel):
    """Staging 차량 라인 생성 요청"""
    name: str
    description: Optional[str] = None
    brand_id: int
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingVehicleLineUpdate(BaseModel):
    """Staging 차량 라인 수정 요청"""
    name: Optional[str] = None
    description: Optional[str] = None


class StagingVehicleLineResponse(BaseModel):
    """Staging 차량 라인 응답"""
    id: int
    name: str
    description: Optional[str] = None
    brand_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Model Schemas =====
class StagingModelCreate(BaseModel):
    """Staging 모델 생성 요청"""
    name: str
    code: str
    vehicle_line_id: int
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: bool = False
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingModelUpdate(BaseModel):
    """Staging 모델 수정 요청"""
    name: Optional[str] = None
    code: Optional[str] = None
    vehicle_line_id: Optional[int] = None
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: Optional[bool] = None


class StagingModelResponse(BaseModel):
    """Staging 모델 응답"""
    id: int
    name: str
    code: str
    vehicle_line_id: int
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: bool
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Trim Schemas =====
class StagingTrimCreate(BaseModel):
    """Staging 트림 생성 요청"""
    name: str
    car_type: CarType
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    model_id: int
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingTrimUpdate(BaseModel):
    """Staging 트림 수정 요청"""
    name: Optional[str] = None
    car_type: Optional[CarType] = None
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    model_id: Optional[int] = None


class StagingTrimResponse(BaseModel):
    """Staging 트림 응답"""
    id: int
    name: str
    car_type: CarType
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    model_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Option Title Schemas =====
class StagingOptionTitleCreate(BaseModel):
    """Staging 옵션 타이틀 생성 요청"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    trim_id: int
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingOptionTitleUpdate(BaseModel):
    """Staging 옵션 타이틀 수정 요청"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class StagingOptionTitleResponse(BaseModel):
    """Staging 옵션 타이틀 응답"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    trim_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Option Price Schemas =====
class StagingOptionPriceCreate(BaseModel):
    """Staging 옵션 가격 생성 요청"""
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    option_title_id: int
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingOptionPriceUpdate(BaseModel):
    """Staging 옵션 가격 수정 요청"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None


class StagingOptionPriceResponse(BaseModel):
    """Staging 옵션 가격 응답"""
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    option_title_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Staging Option Schemas (새로운 통합 옵션) =====
class StagingOptionCreate(BaseModel):
    """Staging 통합 옵션 생성 요청"""
    name: str
    trim_id: int
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str


class StagingOptionUpdate(BaseModel):
    """Staging 통합 옵션 수정 요청"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None


class StagingOptionResponse(BaseModel):
    """Staging 통합 옵션 응답"""
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    trim_id: int
    
    # 생성자 정보
    created_by: str
    created_by_username: Optional[str] = None
    created_by_email: str
    created_at: datetime
    
    # 수정자 정보
    updated_by_username: Optional[str] = None
    updated_by_email: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Version Management Schemas =====

class VersionCreateRequest(BaseModel):
    version_name: str
    description: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "version_name": "v2025.10",
                "description": "2025년 10월 차량 데이터 업데이트",
                "created_by": "admin"
            }
        }


class VersionUpdateRequest(BaseModel):
    version_name: Optional[str] = None
    description: Optional[str] = None
    approval_status: Optional[ApprovalStatus] = None
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "version_name": "v2025.10.1",
                "description": "2025년 10월 차량 데이터 업데이트 (수정)",
                "approval_status": "APPROVED",
                "approved_by": "admin"
            }
        }


class VersionResponse(BaseModel):
    id: int
    version_name: str
    description: Optional[str] = None
    approval_status: ApprovalStatus
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_by: str
    total_brands: int
    total_models: int
    total_trims: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VersionApprovalRequest(BaseModel):
    """버전 승인/거부 요청"""
    approval_status: ApprovalStatus
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class VersionListResponse(BaseModel):
    items: List[VersionResponse]
    total_count: int
    current_page: int
    total_pages: int
    page_size: int
    has_next: bool
    has_prev: bool

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total_count": 0,
                "current_page": 1,
                "total_pages": 0,
                "page_size": 20,
                "has_next": False,
                "has_prev": False
            }
        }


class VersionDetailResponse(BaseModel):
    """버전 상세 정보 (하위 데이터 포함)"""
    version: VersionResponse
    brands: List[StagingBrandResponse]
    vehicle_lines: List[StagingVehicleLineResponse]
    models: List[StagingModelResponse]
    trims: List[StagingTrimResponse]


# ===== Approval Schemas =====
class VersionApprovalRequest(BaseModel):
    """버전 승인/거부 요청"""
    approval_status: ApprovalStatus
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApprovalResponse(BaseModel):
    """승인/거부 응답"""
    success: bool
    message: str
    entity_type: str  # version, brand, model, trim, all
    entity_id: int


# ===== Excel Import Result =====
class ImportResultResponse(BaseModel):
    success: bool
    message: str
    total_rows: int
    processed_rows: int
    trim_count: int
    option_count: int
    color_count: int
    errors: List[str] = []


# ===== Job Schemas =====
class JobCreateRequest(BaseModel):
    """작업 생성 요청"""
    target_url: str  # 크롤링 대상 URL


class JobResponse(BaseModel):
    """작업 응답"""
    id: int
    job_type: JobType
    status: JobStatus
    task_id: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_rows: int = 0
    processed_rows: int = 0
    progress_percentage: int = 0  # 진행률 (0-100)
    error_message: Optional[str] = None
    result_data: Optional[dict] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """작업 목록 응답"""
    total: int
    jobs: List[JobResponse]


# ===== Hierarchy Tree Schemas =====
class BrandTreeResponse(BaseModel):
    """브랜드 계층 트리 응답"""
    id: int
    name: str
    country: str
    logo_url: Optional[str] = None
    vehicle_lines: List['VehicleLineTreeResponse'] = []
    
    class Config:
        from_attributes = True


class VehicleLineTreeResponse(BaseModel):
    """차량 라인 계층 트리 응답"""
    id: int
    name: str
    description: Optional[str] = None
    models: List['ModelTreeResponse'] = []
    
    class Config:
        from_attributes = True


class ModelTreeResponse(BaseModel):
    """모델 계층 트리 응답"""
    id: int
    name: str
    code: str
    release_year: Optional[int] = None
    price: Optional[int] = None
    foreign: bool
    trims: List['TrimTreeResponse'] = []
    
    class Config:
        from_attributes = True


class TrimTreeResponse(BaseModel):
    """트림 계층 트리 응답"""
    id: int
    name: str
    car_type: CarType
    fuel_name: Optional[str] = None
    cc: Optional[str] = None
    base_price: Optional[int] = None
    description: Optional[str] = None
    car_colors: List['TrimCarColorResponse'] = []
    option_titles: List['OptionTitleTreeResponse'] = []
    
    class Config:
        from_attributes = True


class TrimCarColorResponse(BaseModel):
    """트림 색상 응답"""
    id: int
    name: str
    color_code: Optional[str] = None
    additional_price: Optional[int] = None
    vehicle_interior: bool
    
    class Config:
        from_attributes = True


class OptionTitleTreeResponse(BaseModel):
    """옵션 타이틀 계층 트리 응답"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    option_prices: List['OptionPriceResponse'] = []
    
    class Config:
        from_attributes = True


class OptionPriceResponse(BaseModel):
    """옵션 가격 응답"""
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discounted_price: Optional[int] = None
    
    class Config:
        from_attributes = True


# ===== Event Schemas =====

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.PROMOTION
    status: EventStatus = EventStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    address: Optional[str] = None
    max_participants: Optional[int] = None
    registration_fee: Optional[int] = None
    related_brand_id: Optional[int] = None
    related_model_id: Optional[int] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    address: Optional[str] = None
    max_participants: Optional[int] = None
    registration_fee: Optional[int] = None
    related_brand_id: Optional[int] = None
    related_model_id: Optional[int] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    event_type: EventType
    status: EventStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    address: Optional[str] = None
    max_participants: Optional[int] = None
    current_participants: int = 0
    registration_fee: Optional[int] = None
    related_brand_id: Optional[int] = None
    related_model_id: Optional[int] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, event) -> 'EventResponse':
        return cls(
            id=event.id,
            title=event.title,
            description=event.description,
            event_type=event.event_type,
            status=event.status,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            address=event.address,
            max_participants=event.max_participants,
            current_participants=event.current_participants,
            registration_fee=event.registration_fee,
            related_brand_id=event.related_brand_id,
            related_model_id=event.related_model_id,
            created_by=event.created_by,
            created_at=event.created_at,
            updated_at=event.updated_at
        )
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    skip: int
    limit: int


class EventRegistrationCreate(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class EventRegistrationResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    registration_date: datetime
    phone_number: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    status: str
    
    @classmethod
    def from_entity(cls, registration) -> 'EventRegistrationResponse':
        return cls(
            id=registration.id,
            event_id=registration.event_id,
            user_id=registration.user_id,
            registration_date=registration.registration_date,
            phone_number=registration.phone_number,
            email=registration.email,
            notes=registration.notes,
            status=registration.status
        )
    
    class Config:
        from_attributes = True


class EventRegistrationListResponse(BaseModel):
    registrations: List[EventRegistrationResponse]
    total: int
    skip: int
    limit: int


# Forward references 해결
BrandTreeResponse.model_rebuild()
VehicleLineTreeResponse.model_rebuild()
ModelTreeResponse.model_rebuild()
TrimTreeResponse.model_rebuild()
OptionTitleTreeResponse.model_rebuild()


# ===== 할인 정책 스키마 =====

# 기본 할인 정책 스키마
class DiscountPolicyCreate(BaseModel):
    """할인 정책 생성 요청"""
    brand_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True


class DiscountPolicyUpdate(BaseModel):
    """할인 정책 수정 요청"""
    title: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class DiscountPolicyResponse(BaseModel):
    """할인 정책 응답"""
    id: int
    brand_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class DiscountPolicyListResponse(BaseModel):
    """할인 정책 목록 응답"""
    items: List[DiscountPolicyResponse]
    pagination: dict


# 카드사 제휴 스키마
class BrandCardBenefitCreate(BaseModel):
    """카드사 제휴 생성 요청"""
    discount_policy_id: int
    card_partner: str
    cashback_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True


class BrandCardBenefitUpdate(BaseModel):
    """카드사 제휴 수정 요청"""
    card_partner: Optional[str] = None
    cashback_rate: Optional[float] = None
    title: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class BrandCardBenefitResponse(BaseModel):
    """카드사 제휴 응답"""
    id: int
    discount_policy_id: int
    card_partner: str
    cashback_rate: float
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class BrandCardBenefitListResponse(BaseModel):
    """카드사 제휴 목록 응답"""
    items: List[BrandCardBenefitResponse]
    pagination: dict


# 브랜드 프로모션 스키마
class BrandPromoCreate(BaseModel):
    """브랜드 프로모션 생성 요청"""
    discount_policy_id: int
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True


class BrandPromoUpdate(BaseModel):
    """브랜드 프로모션 수정 요청"""
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class BrandPromoResponse(BaseModel):
    """브랜드 프로모션 응답"""
    id: int
    discount_policy_id: int
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class BrandPromoListResponse(BaseModel):
    """브랜드 프로모션 목록 응답"""
    items: List[BrandPromoResponse]
    pagination: dict


# 재고 할인 스키마
class BrandInventoryDiscountCreate(BaseModel):
    """재고 할인 생성 요청"""
    discount_policy_id: int
    inventory_level_threshold: int
    discount_rate: float
    title: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True


class BrandInventoryDiscountUpdate(BaseModel):
    """재고 할인 수정 요청"""
    inventory_level_threshold: Optional[int] = None
    discount_rate: Optional[float] = None
    title: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class BrandInventoryDiscountResponse(BaseModel):
    """재고 할인 응답"""
    id: int
    discount_policy_id: int
    inventory_level_threshold: int
    discount_rate: float
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class BrandInventoryDiscountListResponse(BaseModel):
    """재고 할인 목록 응답"""
    items: List[BrandInventoryDiscountResponse]
    pagination: dict


# 선구매 할인 스키마
class BrandPrePurchaseCreate(BaseModel):
    """선구매 할인 생성 요청"""
    discount_policy_id: int
    event_type: EventTypeForPrePurchase
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True


class BrandPrePurchaseUpdate(BaseModel):
    """선구매 할인 수정 요청"""
    event_type: Optional[EventTypeForPrePurchase] = None
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class BrandPrePurchaseResponse(BaseModel):
    """선구매 할인 응답"""
    id: int
    discount_policy_id: int
    event_type: EventTypeForPrePurchase
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class BrandPrePurchaseListResponse(BaseModel):
    """선구매 할인 목록 응답"""
    items: List[BrandPrePurchaseResponse]
    pagination: dict


# 통합 할인 정책 상세 조회 스키마
class DiscountPolicyDetailResponse(BaseModel):
    """할인 정책 상세 조회 응답 (모든 유형 포함)"""
    policy: DiscountPolicyResponse
    card_benefits: List[BrandCardBenefitResponse]
    promos: List[BrandPromoResponse]
    inventory_discounts: List[BrandInventoryDiscountResponse]
    pre_purchases: List[BrandPrePurchaseResponse]


# 버전별 할인 정책 요약 스키마
class VersionDiscountSummaryResponse(BaseModel):
    """버전별 할인 정책 요약 응답"""
    version_id: int
    total_policies: int
    policies_by_type: dict
    total_card_benefits: int
    total_promos: int
    total_inventory_discounts: int
    total_pre_purchases: int


# 페이지네이션 공통 스키마
class PaginationInfo(BaseModel):
    """페이지네이션 정보"""
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


# 필터링 파라미터 스키마
class DiscountPolicyFilterParams(BaseModel):
    """할인 정책 필터링 파라미터"""
    brand_id: Optional[int] = None
    trim_id: Optional[int] = None
    version_id: Optional[int] = None
    policy_type: Optional[PolicyType] = None
    is_active: Optional[bool] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "desc"


class CardBenefitFilterParams(BaseModel):
    """카드사 제휴 필터링 파라미터"""
    policy_id: Optional[int] = None
    card_partner: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "desc"


class PromoFilterParams(BaseModel):
    """브랜드 프로모션 필터링 파라미터"""
    policy_id: Optional[int] = None
    is_active: Optional[bool] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "desc"


class InventoryDiscountFilterParams(BaseModel):
    """재고 할인 필터링 파라미터"""
    policy_id: Optional[int] = None
    is_active: Optional[bool] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "desc"


class PrePurchaseFilterParams(BaseModel):
    """선구매 할인 필터링 파라미터"""
    policy_id: Optional[int] = None
    event_type: Optional[EventTypeForPrePurchase] = None
    is_active: Optional[bool] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "desc"