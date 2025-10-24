# 🎯 할인 정책 API 구현 가이드

## 📋 구현 순서
1. [Pydantic 스키마 생성](#pydantic-스키마-생성)
2. [Repository 구현](#repository-구현)
3. [Service 구현](#service-구현)
4. [API 엔드포인트 구현](#api-엔드포인트-구현)
5. [테스트 코드](#테스트-코드)

---

## 📝 Pydantic 스키마 생성

### 1. 기본 스키마 (`app/presentation/schemas.py`에 추가)

```python
# ===== 할인 정책 스키마 =====

class DiscountPolicyBase(BaseModel):
    """할인 정책 기본 스키마"""
    brand_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class DiscountPolicyCreate(DiscountPolicyBase):
    """할인 정책 생성 스키마"""
    pass

class DiscountPolicyUpdate(BaseModel):
    """할인 정책 수정 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None

class DiscountPolicyResponse(DiscountPolicyBase):
    """할인 정책 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ===== 카드사 제휴 스키마 =====

class BrandCardBenefitBase(BaseModel):
    """카드사 제휴 기본 스키마"""
    discount_policy_id: int
    card_partner: str
    cashback_rate: float
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandCardBenefitCreate(BrandCardBenefitBase):
    """카드사 제휴 생성 스키마"""
    pass

class BrandCardBenefitBulkCreate(BaseModel):
    """카드사 제휴 일괄 생성 스키마"""
    discount_policy_id: int
    card_benefits: List[BrandCardBenefitCreate]
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandCardBenefitResponse(BrandCardBenefitBase):
    """카드사 제휴 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

# ===== 브랜드 프로모션 스키마 =====

class BrandPromoBase(BaseModel):
    """브랜드 프로모션 기본 스키마"""
    discount_policy_id: int
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandPromoCreate(BrandPromoBase):
    """브랜드 프로모션 생성 스키마"""
    pass

class BrandPromoBulkCreate(BaseModel):
    """브랜드 프로모션 일괄 생성 스키마"""
    discount_policy_id: int
    promos: List[BrandPromoCreate]
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandPromoResponse(BrandPromoBase):
    """브랜드 프로모션 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

# ===== 재고 할인 스키마 =====

class BrandInventoryDiscountBase(BaseModel):
    """재고 할인 기본 스키마"""
    discount_policy_id: int
    inventory_level_threshold: int
    discount_rate: float
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandInventoryDiscountCreate(BrandInventoryDiscountBase):
    """재고 할인 생성 스키마"""
    pass

class BrandInventoryDiscountBulkCreate(BaseModel):
    """재고 할인 일괄 생성 스키마"""
    discount_policy_id: int
    inventory_discounts: List[BrandInventoryDiscountCreate]
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandInventoryDiscountResponse(BrandInventoryDiscountBase):
    """재고 할인 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

# ===== 선구매 할인 스키마 =====

class BrandPrePurchaseBase(BaseModel):
    """선구매 할인 기본 스키마"""
    discount_policy_id: int
    event_type: EventTypeForPrePurchase
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    title: str
    description: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandPrePurchaseCreate(BrandPrePurchaseBase):
    """선구매 할인 생성 스키마"""
    pass

class BrandPrePurchaseBulkCreate(BaseModel):
    """선구매 할인 일괄 생성 스키마"""
    discount_policy_id: int
    pre_purchases: List[BrandPrePurchaseCreate]
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class BrandPrePurchaseResponse(BrandPrePurchaseBase):
    """선구매 할인 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

# ===== 통합 등록 스키마 =====

class DiscountPolicyBulkRegister(BaseModel):
    """할인 정책 통합 등록 스키마"""
    brand_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True
    
    # 선택적 할인 유형들
    card_benefits: Optional[List[BrandCardBenefitCreate]] = None
    promos: Optional[List[BrandPromoCreate]] = None
    inventory_discounts: Optional[List[BrandInventoryDiscountCreate]] = None
    pre_purchases: Optional[List[BrandPrePurchaseCreate]] = None

class DiscountPolicyBulkRegisterResponse(BaseModel):
    """할인 정책 통합 등록 응답 스키마"""
    discount_policy: DiscountPolicyResponse
    card_benefits: Optional[List[BrandCardBenefitResponse]] = None
    promos: Optional[List[BrandPromoResponse]] = None
    inventory_discounts: Optional[List[BrandInventoryDiscountResponse]] = None
    pre_purchases: Optional[List[BrandPrePurchaseResponse]] = None
    summary: dict

# ===== 조회 스키마 =====

class DiscountPolicyDetailsResponse(BaseModel):
    """할인 정책 상세 조회 응답 스키마"""
    policy: DiscountPolicyResponse
    card_benefits: List[BrandCardBenefitResponse] = []
    promos: List[BrandPromoResponse] = []
    inventory_discounts: List[BrandInventoryDiscountResponse] = []
    pre_purchases: List[BrandPrePurchaseResponse] = []

class DiscountPolicySummaryResponse(BaseModel):
    """할인 정책 요약 응답 스키마"""
    version_id: int
    total_policies: int
    policies_by_type: dict
    total_card_benefits: int
    total_promos: int
    total_inventory_discounts: int
    total_pre_purchases: int
```

---

## 🗄️ Repository 구현

### 2. Repository 인터페이스 (`app/application/ports.py`에 추가)

```python
# ===== 할인 정책 Repository 인터페이스 =====

class DiscountPolicyRepository(ABC):
    """할인 정책 Repository 인터페이스"""
    
    @abstractmethod
    def create(self, policy: DiscountPolicy) -> DiscountPolicy:
        """할인 정책 생성"""
        pass
    
    @abstractmethod
    def find_by_id(self, policy_id: int) -> Optional[DiscountPolicy]:
        """ID로 할인 정책 조회"""
        pass
    
    @abstractmethod
    def find_by_brand_trim_version(self, brand_id: int, trim_id: int, version_id: int) -> List[DiscountPolicy]:
        """브랜드, 트림, 버전으로 할인 정책 조회"""
        pass
    
    @abstractmethod
    def find_by_version(self, version_id: int) -> List[DiscountPolicy]:
        """버전별 할인 정책 조회"""
        pass
    
    @abstractmethod
    def update(self, policy_id: int, policy: DiscountPolicy) -> DiscountPolicy:
        """할인 정책 수정"""
        pass
    
    @abstractmethod
    def delete(self, policy_id: int) -> bool:
        """할인 정책 삭제"""
        pass

class BrandCardBenefitRepository(ABC):
    """카드사 제휴 Repository 인터페이스"""
    
    @abstractmethod
    def create(self, benefit: BrandCardBenefit) -> BrandCardBenefit:
        """카드사 제휴 생성"""
        pass
    
    @abstractmethod
    def create_bulk(self, benefits: List[BrandCardBenefit]) -> List[BrandCardBenefit]:
        """카드사 제휴 일괄 생성"""
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandCardBenefit]:
        """정책 ID로 카드사 제휴 조회"""
        pass
    
    @abstractmethod
    def update(self, benefit_id: int, benefit: BrandCardBenefit) -> BrandCardBenefit:
        """카드사 제휴 수정"""
        pass
    
    @abstractmethod
    def delete(self, benefit_id: int) -> bool:
        """카드사 제휴 삭제"""
        pass

class BrandPromoRepository(ABC):
    """브랜드 프로모션 Repository 인터페이스"""
    
    @abstractmethod
    def create(self, promo: BrandPromo) -> BrandPromo:
        """프로모션 생성"""
        pass
    
    @abstractmethod
    def create_bulk(self, promos: List[BrandPromo]) -> List[BrandPromo]:
        """프로모션 일괄 생성"""
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandPromo]:
        """정책 ID로 프로모션 조회"""
        pass
    
    @abstractmethod
    def update(self, promo_id: int, promo: BrandPromo) -> BrandPromo:
        """프로모션 수정"""
        pass
    
    @abstractmethod
    def delete(self, promo_id: int) -> bool:
        """프로모션 삭제"""
        pass

class BrandInventoryDiscountRepository(ABC):
    """재고 할인 Repository 인터페이스"""
    
    @abstractmethod
    def create(self, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        """재고 할인 생성"""
        pass
    
    @abstractmethod
    def create_bulk(self, discounts: List[BrandInventoryDiscount]) -> List[BrandInventoryDiscount]:
        """재고 할인 일괄 생성"""
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandInventoryDiscount]:
        """정책 ID로 재고 할인 조회"""
        pass
    
    @abstractmethod
    def update(self, discount_id: int, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        """재고 할인 수정"""
        pass
    
    @abstractmethod
    def delete(self, discount_id: int) -> bool:
        """재고 할인 삭제"""
        pass

class BrandPrePurchaseRepository(ABC):
    """선구매 할인 Repository 인터페이스"""
    
    @abstractmethod
    def create(self, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        """선구매 할인 생성"""
        pass
    
    @abstractmethod
    def create_bulk(self, pre_purchases: List[BrandPrePurchase]) -> List[BrandPrePurchase]:
        """선구매 할인 일괄 생성"""
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandPrePurchase]:
        """정책 ID로 선구매 할인 조회"""
        pass
    
    @abstractmethod
    def update(self, pre_purchase_id: int, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        """선구매 할인 수정"""
        pass
    
    @abstractmethod
    def delete(self, pre_purchase_id: int) -> bool:
        """선구매 할인 삭제"""
        pass
```

---

## 🔧 Service 구현

### 3. 할인 정책 서비스 (`app/application/discount_service.py`)

```python
"""
할인 정책 서비스 - 비즈니스 로직 처리
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from ..domain.entities import (
    DiscountPolicy, BrandCardBenefit, BrandPromo, 
    BrandInventoryDiscount, BrandPrePurchase, PolicyType
)
from .ports import (
    DiscountPolicyRepository, BrandCardBenefitRepository,
    BrandPromoRepository, BrandInventoryDiscountRepository,
    BrandPrePurchaseRepository
)
from ..presentation.schemas import (
    DiscountPolicyCreate, DiscountPolicyBulkRegister,
    BrandCardBenefitCreate, BrandPromoCreate,
    BrandInventoryDiscountCreate, BrandPrePurchaseCreate
)

class DiscountPolicyService:
    """할인 정책 서비스"""
    
    def __init__(
        self,
        policy_repo: DiscountPolicyRepository,
        card_benefit_repo: BrandCardBenefitRepository,
        promo_repo: BrandPromoRepository,
        inventory_discount_repo: BrandInventoryDiscountRepository,
        pre_purchase_repo: BrandPrePurchaseRepository
    ):
        self.policy_repo = policy_repo
        self.card_benefit_repo = card_benefit_repo
        self.promo_repo = promo_repo
        self.inventory_discount_repo = inventory_discount_repo
        self.pre_purchase_repo = pre_purchase_repo
    
    async def create_discount_policy(self, policy_data: DiscountPolicyCreate) -> DiscountPolicy:
        """할인 정책 생성"""
        # 도메인 엔티티 생성
        policy = DiscountPolicy(
            brand_id=policy_data.brand_id,
            trim_id=policy_data.trim_id,
            version_id=policy_data.version_id,
            policy_type=policy_data.policy_type,
            title=policy_data.title,
            description=policy_data.description,
            valid_from=policy_data.valid_from,
            valid_to=policy_data.valid_to,
            is_active=policy_data.is_active
        )
        
        # 검증
        policy.validate()
        
        # 저장
        return self.policy_repo.create(policy)
    
    async def create_card_benefit(self, benefit_data: BrandCardBenefitCreate) -> BrandCardBenefit:
        """카드사 제휴 생성"""
        # 도메인 엔티티 생성
        benefit = BrandCardBenefit(
            discount_policy_id=benefit_data.discount_policy_id,
            card_partner=benefit_data.card_partner,
            cashback_rate=benefit_data.cashback_rate,
            title=benefit_data.title,
            description=benefit_data.description,
            valid_from=benefit_data.valid_from,
            valid_to=benefit_data.valid_to,
            is_active=benefit_data.is_active
        )
        
        # 검증
        benefit.validate()
        
        # 저장
        return self.card_benefit_repo.create(benefit)
    
    async def create_promo(self, promo_data: BrandPromoCreate) -> BrandPromo:
        """브랜드 프로모션 생성"""
        # 도메인 엔티티 생성
        promo = BrandPromo(
            discount_policy_id=promo_data.discount_policy_id,
            discount_rate=promo_data.discount_rate,
            discount_amount=promo_data.discount_amount,
            title=promo_data.title,
            description=promo_data.description,
            valid_from=promo_data.valid_from,
            valid_to=promo_data.valid_to,
            is_active=promo_data.is_active
        )
        
        # 검증
        promo.validate()
        
        # 저장
        return self.promo_repo.create(promo)
    
    async def create_inventory_discount(self, discount_data: BrandInventoryDiscountCreate) -> BrandInventoryDiscount:
        """재고 할인 생성"""
        # 도메인 엔티티 생성
        discount = BrandInventoryDiscount(
            discount_policy_id=discount_data.discount_policy_id,
            inventory_level_threshold=discount_data.inventory_level_threshold,
            discount_rate=discount_data.discount_rate,
            title=discount_data.title,
            description=discount_data.description,
            valid_from=discount_data.valid_from,
            valid_to=discount_data.valid_to,
            is_active=discount_data.is_active
        )
        
        # 검증
        discount.validate()
        
        # 저장
        return self.inventory_discount_repo.create(discount)
    
    async def create_pre_purchase(self, pre_purchase_data: BrandPrePurchaseCreate) -> BrandPrePurchase:
        """선구매 할인 생성"""
        # 도메인 엔티티 생성
        pre_purchase = BrandPrePurchase(
            discount_policy_id=pre_purchase_data.discount_policy_id,
            event_type=pre_purchase_data.event_type,
            discount_rate=pre_purchase_data.discount_rate,
            discount_amount=pre_purchase_data.discount_amount,
            title=pre_purchase_data.title,
            description=pre_purchase_data.description,
            pre_purchase_start=pre_purchase_data.pre_purchase_start,
            valid_from=pre_purchase_data.valid_from,
            valid_to=pre_purchase_data.valid_to,
            is_active=pre_purchase_data.is_active
        )
        
        # 검증
        pre_purchase.validate()
        
        # 저장
        return self.pre_purchase_repo.create(pre_purchase)
    
    async def bulk_register_discount_policy(self, bulk_data: DiscountPolicyBulkRegister) -> Dict[str, Any]:
        """할인 정책 통합 등록"""
        # 1. 기본 정책 생성
        policy = await self.create_discount_policy(
            DiscountPolicyCreate(
                brand_id=bulk_data.brand_id,
                trim_id=bulk_data.trim_id,
                version_id=bulk_data.version_id,
                policy_type=bulk_data.policy_type,
                title=bulk_data.title,
                description=bulk_data.description,
                valid_from=bulk_data.valid_from,
                valid_to=bulk_data.valid_to,
                is_active=bulk_data.is_active
            )
        )
        
        result = {
            "discount_policy": policy,
            "card_benefits": [],
            "promos": [],
            "inventory_discounts": [],
            "pre_purchases": []
        }
        
        # 2. 카드사 제휴 등록
        if bulk_data.card_benefits:
            card_benefits = []
            for benefit_data in bulk_data.card_benefits:
                benefit_data.discount_policy_id = policy.id
                benefit_data.valid_from = bulk_data.valid_from
                benefit_data.valid_to = bulk_data.valid_to
                benefit_data.is_active = bulk_data.is_active
                
                benefit = await self.create_card_benefit(benefit_data)
                card_benefits.append(benefit)
            
            result["card_benefits"] = card_benefits
        
        # 3. 브랜드 프로모션 등록
        if bulk_data.promos:
            promos = []
            for promo_data in bulk_data.promos:
                promo_data.discount_policy_id = policy.id
                promo_data.valid_from = bulk_data.valid_from
                promo_data.valid_to = bulk_data.valid_to
                promo_data.is_active = bulk_data.is_active
                
                promo = await self.create_promo(promo_data)
                promos.append(promo)
            
            result["promos"] = promos
        
        # 4. 재고 할인 등록
        if bulk_data.inventory_discounts:
            inventory_discounts = []
            for discount_data in bulk_data.inventory_discounts:
                discount_data.discount_policy_id = policy.id
                discount_data.valid_from = bulk_data.valid_from
                discount_data.valid_to = bulk_data.valid_to
                discount_data.is_active = bulk_data.is_active
                
                discount = await self.create_inventory_discount(discount_data)
                inventory_discounts.append(discount)
            
            result["inventory_discounts"] = inventory_discounts
        
        # 5. 선구매 할인 등록
        if bulk_data.pre_purchases:
            pre_purchases = []
            for pre_purchase_data in bulk_data.pre_purchases:
                pre_purchase_data.discount_policy_id = policy.id
                pre_purchase_data.valid_from = bulk_data.valid_from
                pre_purchase_data.valid_to = bulk_data.valid_to
                pre_purchase_data.is_active = bulk_data.is_active
                
                pre_purchase = await self.create_pre_purchase(pre_purchase_data)
                pre_purchases.append(pre_purchase)
            
            result["pre_purchases"] = pre_purchases
        
        # 6. 요약 정보 생성
        result["summary"] = {
            "total_policies": 1,
            "total_card_benefits": len(result["card_benefits"]),
            "total_promos": len(result["promos"]),
            "total_inventory_discounts": len(result["inventory_discounts"]),
            "total_pre_purchases": len(result["pre_purchases"])
        }
        
        return result
    
    async def get_discount_policy_details(self, policy_id: int) -> Dict[str, Any]:
        """할인 정책 상세 조회"""
        # 기본 정책 조회
        policy = self.policy_repo.find_by_id(policy_id)
        if not policy:
            raise ValueError(f"할인 정책을 찾을 수 없습니다: {policy_id}")
        
        # 각 유형별 세부 정보 조회
        card_benefits = self.card_benefit_repo.find_by_policy_id(policy_id)
        promos = self.promo_repo.find_by_policy_id(policy_id)
        inventory_discounts = self.inventory_discount_repo.find_by_policy_id(policy_id)
        pre_purchases = self.pre_purchase_repo.find_by_policy_id(policy_id)
        
        return {
            "policy": policy,
            "card_benefits": card_benefits,
            "promos": promos,
            "inventory_discounts": inventory_discounts,
            "pre_purchases": pre_purchases
        }
    
    async def get_version_discount_summary(self, version_id: int) -> Dict[str, Any]:
        """버전별 할인 정책 요약"""
        # 버전별 정책 조회
        policies = self.policy_repo.find_by_version(version_id)
        
        # 정책 유형별 카운트
        policies_by_type = {}
        for policy in policies:
            policy_type = policy.policy_type.value
            policies_by_type[policy_type] = policies_by_type.get(policy_type, 0) + 1
        
        # 각 유형별 총 개수 계산
        total_card_benefits = 0
        total_promos = 0
        total_inventory_discounts = 0
        total_pre_purchases = 0
        
        for policy in policies:
            total_card_benefits += len(self.card_benefit_repo.find_by_policy_id(policy.id))
            total_promos += len(self.promo_repo.find_by_policy_id(policy.id))
            total_inventory_discounts += len(self.inventory_discount_repo.find_by_policy_id(policy.id))
            total_pre_purchases += len(self.pre_purchase_repo.find_by_policy_id(policy.id))
        
        return {
            "version_id": version_id,
            "total_policies": len(policies),
            "policies_by_type": policies_by_type,
            "total_card_benefits": total_card_benefits,
            "total_promos": total_promos,
            "total_inventory_discounts": total_inventory_discounts,
            "total_pre_purchases": total_pre_purchases
        }
```

---

## 🚀 API 엔드포인트 구현

### 4. API 라우터 (`app/presentation/api/discount/`)

```python
# app/presentation/api/discount/policies.py
"""
할인 정책 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.infrastructure.database import get_db
from app.application.discount_service import DiscountPolicyService
from app.domain.entities import User, PolicyType
from ...schemas import (
    DiscountPolicyCreate, DiscountPolicyResponse, DiscountPolicyUpdate,
    DiscountPolicyBulkRegister, DiscountPolicyBulkRegisterResponse,
    DiscountPolicyDetailsResponse, DiscountPolicySummaryResponse
)
from ...dependencies import get_current_user, get_discount_policy_service

router = APIRouter(prefix="/api/discount/policies", tags=["discount-policies"])

@router.post("/", response_model=DiscountPolicyResponse)
async def create_discount_policy(
    policy_data: DiscountPolicyCreate,
    service: DiscountPolicyService = Depends(get_discount_policy_service),
    current_user: User = Depends(get_current_user)
):
    """할인 정책 생성"""
    try:
        policy = await service.create_discount_policy(policy_data)
        return DiscountPolicyResponse.from_orm(policy)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 생성 실패: {str(e)}")

@router.get("/", response_model=List[DiscountPolicyResponse])
async def get_discount_policies(
    brand_id: Optional[int] = Query(None),
    trim_id: Optional[int] = Query(None),
    version_id: Optional[int] = Query(None),
    policy_type: Optional[PolicyType] = Query(None),
    service: DiscountPolicyService = Depends(get_discount_policy_service),
    current_user: User = Depends(get_current_user)
):
    """할인 정책 조회"""
    try:
        if version_id:
            policies = service.policy_repo.find_by_version(version_id)
        elif brand_id and trim_id and version_id:
            policies = service.policy_repo.find_by_brand_trim_version(brand_id, trim_id, version_id)
        else:
            policies = service.policy_repo.find_all()
        
        # 필터링
        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]
        
        return [DiscountPolicyResponse.from_orm(policy) for policy in policies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 조회 실패: {str(e)}")

@router.get("/{policy_id}/details", response_model=DiscountPolicyDetailsResponse)
async def get_discount_policy_details(
    policy_id: int,
    service: DiscountPolicyService = Depends(get_discount_policy_service),
    current_user: User = Depends(get_current_user)
):
    """할인 정책 상세 조회"""
    try:
        details = await service.get_discount_policy_details(policy_id)
        return DiscountPolicyDetailsResponse(**details)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 상세 조회 실패: {str(e)}")

@router.post("/bulk-register", response_model=DiscountPolicyBulkRegisterResponse)
async def bulk_register_discount_policy(
    bulk_data: DiscountPolicyBulkRegister,
    service: DiscountPolicyService = Depends(get_discount_policy_service),
    current_user: User = Depends(get_current_user)
):
    """할인 정책 통합 등록"""
    try:
        result = await service.bulk_register_discount_policy(bulk_data)
        return DiscountPolicyBulkRegisterResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 통합 등록 실패: {str(e)}")

@router.get("/versions/{version_id}/summary", response_model=DiscountPolicySummaryResponse)
async def get_version_discount_summary(
    version_id: int,
    service: DiscountPolicyService = Depends(get_discount_policy_service),
    current_user: User = Depends(get_current_user)
):
    """버전별 할인 정책 요약"""
    try:
        summary = await service.get_version_discount_summary(version_id)
        return DiscountPolicySummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전별 할인 정책 요약 조회 실패: {str(e)}")
```

---

## 🧪 테스트 코드

### 5. 테스트 예시

```python
# tests/test_discount_policy_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_create_discount_policy(client: TestClient, auth_headers: dict):
    """할인 정책 생성 테스트"""
    policy_data = {
        "brand_id": 1,
        "trim_id": 5,
        "version_id": 10,
        "policy_type": "CARD_BENEFIT",
        "title": "삼성카드 제휴 할인 정책",
        "description": "삼성카드로 결제 시 다양한 혜택 제공",
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2024-12-31T23:59:59",
        "is_active": True
    }
    
    response = client.post("/api/discount/policies/", json=policy_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == policy_data["title"]
    assert data["policy_type"] == policy_data["policy_type"]
    assert "id" in data

def test_bulk_register_discount_policy(client: TestClient, auth_headers: dict):
    """할인 정책 통합 등록 테스트"""
    bulk_data = {
        "brand_id": 1,
        "trim_id": 5,
        "version_id": 10,
        "policy_type": "CARD_BENEFIT",
        "title": "현대 아반떼 하이브리드 종합 할인 정책",
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2024-12-31T23:59:59",
        "card_benefits": [
            {
                "card_partner": "삼성카드",
                "cashback_rate": 5.00,
                "title": "삼성카드 5% 캐시백"
            }
        ],
        "promos": [
            {
                "discount_rate": 10.00,
                "title": "신규 고객 10% 할인"
            }
        ]
    }
    
    response = client.post("/api/discount/policies/bulk-register", json=bulk_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["discount_policy"]["title"] == bulk_data["title"]
    assert len(data["card_benefits"]) == 1
    assert len(data["promos"]) == 1
    assert data["summary"]["total_card_benefits"] == 1
    assert data["summary"]["total_promos"] == 1
```

---

## 📚 요약

### 구현 완료 항목
1. **Pydantic 스키마**: 모든 요청/응답 스키마 정의
2. **Repository 인터페이스**: 각 유형별 Repository 인터페이스
3. **Service 구현**: 비즈니스 로직 처리 서비스
4. **API 엔드포인트**: RESTful API 구현
5. **테스트 코드**: 기본 테스트 케이스

### 다음 단계
1. **SQLAlchemy Repository 구현**: 실제 데이터베이스 연동
2. **의존성 주입 설정**: FastAPI 의존성 설정
3. **에러 처리**: 상세한 에러 처리 로직
4. **로깅**: 구조화된 로깅 시스템
5. **프론트엔드 연동**: React 컴포넌트 구현

이 구조는 **확장 가능하고 유지보수하기 쉬운 할인 정책 관리 시스템**을 제공합니다.
