"""
할인 정책 서비스 - 비즈니스 로직 처리
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from ..domain.entities import (
    StagingDiscountPolicy, StagingBrandCardBenefit, StagingBrandPromo, 
    StagingBrandInventoryDiscount, StagingBrandPrePurchase, PolicyType
)

# 타입 별칭
DiscountPolicy = StagingDiscountPolicy
BrandCardBenefit = StagingBrandCardBenefit
BrandPromo = StagingBrandPromo
BrandInventoryDiscount = StagingBrandInventoryDiscount
BrandPrePurchase = StagingBrandPrePurchase
from .ports import (
    StagingDiscountPolicyRepository, StagingBrandCardBenefitRepository,
    StagingBrandPromoRepository, StagingBrandInventoryDiscountRepository,
    StagingBrandPrePurchaseRepository
)
from ..infrastructure.orm_models import (
    StagingDiscountPolicyORM, StagingBrandCardBenefitORM, StagingBrandPromoORM,
    StagingBrandInventoryDiscountORM, StagingBrandPrePurchaseORM
)

# 타입 별칭
DiscountPolicyORM = StagingDiscountPolicyORM
BrandCardBenefitORM = StagingBrandCardBenefitORM
BrandPromoORM = StagingBrandPromoORM
BrandInventoryDiscountORM = StagingBrandInventoryDiscountORM
BrandPrePurchaseORM = StagingBrandPrePurchaseORM


class DiscountPolicyService:
    """할인 정책 서비스"""
    
    def __init__(
        self,
        policy_repo: StagingDiscountPolicyRepository,
        card_benefit_repo: StagingBrandCardBenefitRepository,
        promo_repo: StagingBrandPromoRepository,
        inventory_discount_repo: StagingBrandInventoryDiscountRepository,
        pre_purchase_repo: StagingBrandPrePurchaseRepository
    ):
        self.policy_repo = policy_repo
        self.card_benefit_repo = card_benefit_repo
        self.promo_repo = promo_repo
        self.inventory_discount_repo = inventory_discount_repo
        self.pre_purchase_repo = pre_purchase_repo
    
    # ===== 기본 할인 정책 CRUD =====
    
    async def create_discount_policy(
        self,
        brand_id: int,
        vehicle_line_id: int,
        trim_id: int,
        version_id: int,
        policy_type: PolicyType,
        title: str,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True
    ) -> DiscountPolicy:
        """할인 정책 생성"""
        # 도메인 엔티티 생성
        policy = DiscountPolicy(
            brand_id=brand_id,
            vehicle_line_id=vehicle_line_id,
            trim_id=trim_id,
            version_id=version_id,
            policy_type=policy_type,
            title=title,
            description=description,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to or datetime.utcnow(),
            is_active=is_active
        )
        
        # 검증
        policy.validate()
        
        # 저장
        return self.policy_repo.create(policy)
    
    async def get_discount_policy(self, policy_id: int) -> Optional[DiscountPolicy]:
        """할인 정책 단일 조회"""
        return self.policy_repo.find_by_id(policy_id)
    
    async def get_discount_policies(
        self,
        brand_id: Optional[int] = None,
        trim_id: Optional[int] = None,
        version_id: Optional[int] = None,
        policy_type: Optional[PolicyType] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """할인 정책 목록 조회 (페이지네이션)"""
        offset = (page - 1) * limit
        
        # 데이터 조회
        policies = self.policy_repo.find_all(
            brand_id=brand_id,
            trim_id=trim_id,
            version_id=version_id,
            policy_type=policy_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        # 총 개수 조회
        total = self.policy_repo.count(
            brand_id=brand_id,
            trim_id=trim_id,
            version_id=version_id,
            policy_type=policy_type,
            is_active=is_active
        )
        
        # 페이지네이션 정보 계산
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "items": policies,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_discount_policy(
        self,
        policy_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: Optional[bool] = None
    ) -> DiscountPolicy:
        """할인 정책 수정"""
        # 기존 정책 조회
        existing_policy = self.policy_repo.find_by_id(policy_id)
        if not existing_policy:
            raise ValueError(f"할인 정책을 찾을 수 없습니다: {policy_id}")
        
        # 수정할 필드만 업데이트
        updated_policy = DiscountPolicy(
            id=existing_policy.id,
            brand_id=existing_policy.brand_id,
            trim_id=existing_policy.trim_id,
            version_id=existing_policy.version_id,
            policy_type=existing_policy.policy_type,
            title=title if title is not None else existing_policy.title,
            description=description if description is not None else existing_policy.description,
            valid_from=valid_from if valid_from is not None else existing_policy.valid_from,
            valid_to=valid_to if valid_to is not None else existing_policy.valid_to,
            is_active=is_active if is_active is not None else existing_policy.is_active
        )
        
        # 검증
        updated_policy.validate()
        
        # 저장
        return self.policy_repo.update(policy_id, updated_policy)
    
    async def delete_discount_policy(self, policy_id: int) -> bool:
        """할인 정책 삭제"""
        return self.policy_repo.delete(policy_id)
    
    # ===== 카드사 제휴 CRUD =====
    
    async def create_card_benefit(
        self,
        discount_policy_id: int,
        card_partner: str,
        cashback_rate: float,
        title: str,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True
    ) -> BrandCardBenefit:
        """카드사 제휴 생성"""
        # 도메인 엔티티 생성
        benefit = BrandCardBenefit(
            discount_policy_id=discount_policy_id,
            card_partner=card_partner,
            cashback_rate=cashback_rate,
            title=title,
            description=description,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to or datetime.utcnow(),
            is_active=is_active
        )
        
        # 검증
        benefit.validate()
        
        # 저장
        return self.card_benefit_repo.create(benefit)
    
    async def get_card_benefit(self, benefit_id: int) -> Optional[BrandCardBenefit]:
        """카드사 제휴 단일 조회"""
        return self.card_benefit_repo.find_by_id(benefit_id)
    
    async def get_card_benefits(
        self,
        policy_id: Optional[int] = None,
        card_partner: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """카드사 제휴 목록 조회 (페이지네이션)"""
        offset = (page - 1) * limit
        
        # 데이터 조회
        benefits = self.card_benefit_repo.find_all(
            policy_id=policy_id,
            card_partner=card_partner,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        # 총 개수 조회 (간단한 구현)
        total = len(benefits)  # 실제로는 별도 count 메서드 필요
        
        # 페이지네이션 정보 계산
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "items": benefits,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_card_benefit(
        self,
        benefit_id: int,
        card_partner: Optional[str] = None,
        cashback_rate: Optional[float] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: Optional[bool] = None
    ) -> BrandCardBenefit:
        """카드사 제휴 수정"""
        # 기존 제휴 조회
        existing_benefit = self.card_benefit_repo.find_by_id(benefit_id)
        if not existing_benefit:
            raise ValueError(f"카드사 제휴를 찾을 수 없습니다: {benefit_id}")
        
        # 수정할 필드만 업데이트
        updated_benefit = BrandCardBenefit(
            id=existing_benefit.id,
            discount_policy_id=existing_benefit.discount_policy_id,
            card_partner=card_partner if card_partner is not None else existing_benefit.card_partner,
            cashback_rate=cashback_rate if cashback_rate is not None else existing_benefit.cashback_rate,
            title=title if title is not None else existing_benefit.title,
            description=description if description is not None else existing_benefit.description,
            valid_from=valid_from if valid_from is not None else existing_benefit.valid_from,
            valid_to=valid_to if valid_to is not None else existing_benefit.valid_to,
            is_active=is_active if is_active is not None else existing_benefit.is_active
        )
        
        # 검증
        updated_benefit.validate()
        
        # 저장
        return self.card_benefit_repo.update(benefit_id, updated_benefit)
    
    async def delete_card_benefit(self, benefit_id: int) -> bool:
        """카드사 제휴 삭제"""
        return self.card_benefit_repo.delete(benefit_id)
    
    # ===== 브랜드 프로모션 CRUD =====
    
    async def create_promo(
        self,
        discount_policy_id: int,
        title: str,
        discount_rate: Optional[float] = None,
        discount_amount: Optional[int] = None,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True
    ) -> BrandPromo:
        """브랜드 프로모션 생성"""
        # 도메인 엔티티 생성
        promo = BrandPromo(
            discount_policy_id=discount_policy_id,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            title=title,
            description=description,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to or datetime.utcnow(),
            is_active=is_active
        )
        
        # 검증
        promo.validate()
        
        # 저장
        return self.promo_repo.create(promo)
    
    async def get_promo(self, promo_id: int) -> Optional[BrandPromo]:
        """브랜드 프로모션 단일 조회"""
        return self.promo_repo.find_by_id(promo_id)
    
    async def get_promos(
        self,
        policy_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """브랜드 프로모션 목록 조회 (페이지네이션)"""
        offset = (page - 1) * limit
        
        # 데이터 조회
        promos = self.promo_repo.find_all(
            policy_id=policy_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        # 총 개수 조회 (간단한 구현)
        total = len(promos)  # 실제로는 별도 count 메서드 필요
        
        # 페이지네이션 정보 계산
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "items": promos,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_promo(
        self,
        promo_id: int,
        discount_rate: Optional[float] = None,
        discount_amount: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: Optional[bool] = None
    ) -> BrandPromo:
        """브랜드 프로모션 수정"""
        # 기존 프로모션 조회
        existing_promo = self.promo_repo.find_by_id(promo_id)
        if not existing_promo:
            raise ValueError(f"브랜드 프로모션을 찾을 수 없습니다: {promo_id}")
        
        # 수정할 필드만 업데이트
        updated_promo = BrandPromo(
            id=existing_promo.id,
            discount_policy_id=existing_promo.discount_policy_id,
            discount_rate=discount_rate if discount_rate is not None else existing_promo.discount_rate,
            discount_amount=discount_amount if discount_amount is not None else existing_promo.discount_amount,
            title=title if title is not None else existing_promo.title,
            description=description if description is not None else existing_promo.description,
            valid_from=valid_from if valid_from is not None else existing_promo.valid_from,
            valid_to=valid_to if valid_to is not None else existing_promo.valid_to,
            is_active=is_active if is_active is not None else existing_promo.is_active
        )
        
        # 검증
        updated_promo.validate()
        
        # 저장
        return self.promo_repo.update(promo_id, updated_promo)
    
    async def delete_promo(self, promo_id: int) -> bool:
        """브랜드 프로모션 삭제"""
        return self.promo_repo.delete(promo_id)
    
    # ===== 재고 할인 CRUD =====
    
    async def create_inventory_discount(
        self,
        discount_policy_id: int,
        inventory_level_threshold: int,
        discount_rate: float,
        title: str,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True
    ) -> BrandInventoryDiscount:
        """재고 할인 생성"""
        # 도메인 엔티티 생성
        discount = BrandInventoryDiscount(
            discount_policy_id=discount_policy_id,
            inventory_level_threshold=inventory_level_threshold,
            discount_rate=discount_rate,
            title=title,
            description=description,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to or datetime.utcnow(),
            is_active=is_active
        )
        
        # 검증
        discount.validate()
        
        # 저장
        return self.inventory_discount_repo.create(discount)
    
    async def get_inventory_discount(self, discount_id: int) -> Optional[BrandInventoryDiscount]:
        """재고 할인 단일 조회"""
        return self.inventory_discount_repo.find_by_id(discount_id)
    
    async def get_inventory_discounts(
        self,
        policy_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """재고 할인 목록 조회 (페이지네이션)"""
        offset = (page - 1) * limit
        
        # 데이터 조회
        discounts = self.inventory_discount_repo.find_all(
            policy_id=policy_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        # 총 개수 조회 (간단한 구현)
        total = len(discounts)  # 실제로는 별도 count 메서드 필요
        
        # 페이지네이션 정보 계산
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "items": discounts,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_inventory_discount(
        self,
        discount_id: int,
        inventory_level_threshold: Optional[int] = None,
        discount_rate: Optional[float] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: Optional[bool] = None
    ) -> BrandInventoryDiscount:
        """재고 할인 수정"""
        # 기존 할인 조회
        existing_discount = self.inventory_discount_repo.find_by_id(discount_id)
        if not existing_discount:
            raise ValueError(f"재고 할인을 찾을 수 없습니다: {discount_id}")
        
        # 수정할 필드만 업데이트
        updated_discount = BrandInventoryDiscount(
            id=existing_discount.id,
            discount_policy_id=existing_discount.discount_policy_id,
            inventory_level_threshold=inventory_level_threshold if inventory_level_threshold is not None else existing_discount.inventory_level_threshold,
            discount_rate=discount_rate if discount_rate is not None else existing_discount.discount_rate,
            title=title if title is not None else existing_discount.title,
            description=description if description is not None else existing_discount.description,
            valid_from=valid_from if valid_from is not None else existing_discount.valid_from,
            valid_to=valid_to if valid_to is not None else existing_discount.valid_to,
            is_active=is_active if is_active is not None else existing_discount.is_active
        )
        
        # 검증
        updated_discount.validate()
        
        # 저장
        return self.inventory_discount_repo.update(discount_id, updated_discount)
    
    async def delete_inventory_discount(self, discount_id: int) -> bool:
        """재고 할인 삭제"""
        return self.inventory_discount_repo.delete(discount_id)
    
    # ===== 선구매 할인 CRUD =====
    
    async def create_pre_purchase(
        self,
        discount_policy_id: int,
        title: str,
        event_type: Optional[str] = "PRE_PURCHASE_SPECIAL",
        discount_rate: Optional[float] = None,
        discount_amount: Optional[int] = None,
        description: Optional[str] = None,
        pre_purchase_start: Optional[datetime] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True
    ) -> BrandPrePurchase:
        """선구매 할인 생성 (선구매/특가 통합)"""
        # 도메인 엔티티 생성
        pre_purchase = BrandPrePurchase(
            discount_policy_id=discount_policy_id,
            event_type=event_type,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            title=title,
            description=description,
            pre_purchase_start=pre_purchase_start,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to or datetime.utcnow(),
            is_active=is_active
        )
        
        # 검증
        pre_purchase.validate()
        
        # 저장
        return self.pre_purchase_repo.create(pre_purchase)
    
    async def get_pre_purchase(self, pre_purchase_id: int) -> Optional[BrandPrePurchase]:
        """선구매 할인 단일 조회"""
        return self.pre_purchase_repo.find_by_id(pre_purchase_id)
    
    async def get_pre_purchases(
        self,
        policy_id: Optional[int] = None,
        event_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """선구매 할인 목록 조회 (페이지네이션)"""
        offset = (page - 1) * limit
        
        # 데이터 조회
        pre_purchases = self.pre_purchase_repo.find_all(
            policy_id=policy_id,
            event_type=event_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        # 총 개수 조회 (간단한 구현)
        total = len(pre_purchases)  # 실제로는 별도 count 메서드 필요
        
        # 페이지네이션 정보 계산
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "items": pre_purchases,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_pre_purchase(
        self,
        pre_purchase_id: int,
        event_type: Optional[str] = None,
        discount_rate: Optional[float] = None,
        discount_amount: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        pre_purchase_start: Optional[datetime] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: Optional[bool] = None
    ) -> BrandPrePurchase:
        """선구매 할인 수정"""
        # 기존 선구매 할인 조회
        existing_pre_purchase = self.pre_purchase_repo.find_by_id(pre_purchase_id)
        if not existing_pre_purchase:
            raise ValueError(f"선구매 할인을 찾을 수 없습니다: {pre_purchase_id}")
        
        # 수정할 필드만 업데이트
        updated_pre_purchase = BrandPrePurchase(
            id=existing_pre_purchase.id,
            discount_policy_id=existing_pre_purchase.discount_policy_id,
            event_type=event_type if event_type is not None else existing_pre_purchase.event_type,
            discount_rate=discount_rate if discount_rate is not None else existing_pre_purchase.discount_rate,
            discount_amount=discount_amount if discount_amount is not None else existing_pre_purchase.discount_amount,
            title=title if title is not None else existing_pre_purchase.title,
            description=description if description is not None else existing_pre_purchase.description,
            pre_purchase_start=pre_purchase_start if pre_purchase_start is not None else existing_pre_purchase.pre_purchase_start,
            valid_from=valid_from if valid_from is not None else existing_pre_purchase.valid_from,
            valid_to=valid_to if valid_to is not None else existing_pre_purchase.valid_to,
            is_active=is_active if is_active is not None else existing_pre_purchase.is_active
        )
        
        # 검증
        updated_pre_purchase.validate()
        
        # 저장
        return self.pre_purchase_repo.update(pre_purchase_id, updated_pre_purchase)
    
    async def delete_pre_purchase(self, pre_purchase_id: int) -> bool:
        """선구매 할인 삭제"""
        return self.pre_purchase_repo.delete(pre_purchase_id)
    
    # ===== 통합 조회 메서드 =====
    
    async def create_discount_policy_with_details(
        self,
        brand_id: int,
        vehicle_line_id: int,
        trim_id: int,
        version_id: int,
        policy_type: PolicyType,
        title: str,
        description: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        is_active: bool = True,
        # 세부 정보
        card_partner: Optional[str] = None,
        cashback_rate: Optional[float] = None,
        discount_rate: Optional[float] = None,
        discount_amount: Optional[int] = None,
        inventory_level_threshold: Optional[int] = None,
        event_type: Optional[str] = None,
        pre_purchase_start: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        할인 정책과 세부 정보를 트랜잭션으로 함께 생성
        """
        # 트랜잭션 시작을 위해 Repository의 db에 직접 접근
        db = self.policy_repo.db
        
        try:
            # 1. 기본 정책 생성
            policy = DiscountPolicy(
                brand_id=brand_id,
                vehicle_line_id=vehicle_line_id,
                trim_id=trim_id,
                version_id=version_id,
                policy_type=policy_type,
                title=title,
                description=description,
                valid_from=valid_from or datetime.utcnow(),
                valid_to=valid_to or datetime.utcnow(),
                is_active=is_active
            )
            policy.validate()
            
            # ORM 객체 생성 및 추가 (아직 commit 안 함)
            policy_orm = DiscountPolicyORM(
                brand_id=policy.brand_id,
                vehicle_line_id=policy.vehicle_line_id,
                trim_id=policy.trim_id,
                version_id=policy.version_id,
                policy_type=policy.policy_type,
                title=policy.title,
                description=policy.description,
                valid_from=policy.valid_from,
                valid_to=policy.valid_to,
                is_active=policy.is_active
            )
            db.add(policy_orm)
            db.flush()  # ID를 얻기 위해 flush만 (commit 아님)
            
            # 2. 세부 정보 생성 (policy_type에 따라)
            if policy_type == PolicyType.CARD_BENEFIT:
                if not card_partner or cashback_rate is None:
                    raise ValueError("카드사명과 캐시백 비율은 필수입니다")
                
                benefit = BrandCardBenefit(
                    discount_policy_id=policy_orm.id,
                    card_partner=card_partner,
                    cashback_rate=cashback_rate,
                    title=title,
                    description=description,
                    valid_from=valid_from or datetime.utcnow(),
                    valid_to=valid_to or datetime.utcnow(),
                    is_active=is_active
                )
                benefit.validate()
                
                benefit_orm = BrandCardBenefitORM(
                    discount_policy_id=policy_orm.id,
                    card_partner=benefit.card_partner,
                    cashback_rate=str(benefit.cashback_rate),
                    title=benefit.title,
                    description=benefit.description,
                    valid_from=benefit.valid_from,
                    valid_to=benefit.valid_to,
                    is_active=benefit.is_active
                )
                db.add(benefit_orm)
                
            elif policy_type == PolicyType.BRAND_PROMO:
                if discount_rate is None and discount_amount is None:
                    raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
                
                promo = BrandPromo(
                    discount_policy_id=policy_orm.id,
                    discount_rate=discount_rate,
                    discount_amount=discount_amount,
                    title=title,
                    description=description,
                    valid_from=valid_from or datetime.utcnow(),
                    valid_to=valid_to or datetime.utcnow(),
                    is_active=is_active
                )
                promo.validate()
                
                promo_orm = BrandPromoORM(
                    discount_policy_id=policy_orm.id,
                    discount_rate=str(promo.discount_rate) if promo.discount_rate else None,
                    discount_amount=promo.discount_amount,
                    title=promo.title,
                    description=promo.description,
                    valid_from=promo.valid_from,
                    valid_to=promo.valid_to,
                    is_active=promo.is_active
                )
                db.add(promo_orm)
                
            elif policy_type == PolicyType.INVENTORY:
                if inventory_level_threshold is None or discount_rate is None:
                    raise ValueError("재고 기준 수량과 할인율은 필수입니다")
                
                inventory = BrandInventoryDiscount(
                    discount_policy_id=policy_orm.id,
                    inventory_level_threshold=inventory_level_threshold,
                    discount_rate=discount_rate,
                    title=title,
                    description=description,
                    valid_from=valid_from or datetime.utcnow(),
                    valid_to=valid_to or datetime.utcnow(),
                    is_active=is_active
                )
                inventory.validate()
                
                inventory_orm = BrandInventoryDiscountORM(
                    discount_policy_id=policy_orm.id,
                    inventory_level_threshold=inventory.inventory_level_threshold,
                    discount_rate=str(inventory.discount_rate),
                    title=inventory.title,
                    description=inventory.description,
                    valid_from=inventory.valid_from,
                    valid_to=inventory.valid_to,
                    is_active=inventory.is_active
                )
                db.add(inventory_orm)
                
            elif policy_type == PolicyType.PRE_PURCHASE:
                if discount_rate is None and discount_amount is None:
                    raise ValueError("할인율 또는 할인 금액 중 하나는 필수입니다")
                
                pre_purchase = BrandPrePurchase(
                    discount_policy_id=policy_orm.id,
                    event_type=event_type or "PRE_PURCHASE",
                    discount_rate=discount_rate,
                    discount_amount=discount_amount,
                    title=title,
                    description=description,
                    pre_purchase_start=pre_purchase_start,
                    valid_from=valid_from or datetime.utcnow(),
                    valid_to=valid_to or datetime.utcnow(),
                    is_active=is_active
                )
                pre_purchase.validate()
                
                pre_purchase_orm = BrandPrePurchaseORM(
                    discount_policy_id=policy_orm.id,
                    event_type=pre_purchase.event_type,
                    discount_rate=str(pre_purchase.discount_rate) if pre_purchase.discount_rate else None,
                    discount_amount=pre_purchase.discount_amount,
                    title=pre_purchase.title,
                    description=pre_purchase.description,
                    pre_purchase_start=pre_purchase.pre_purchase_start,
                    valid_from=pre_purchase.valid_from,
                    valid_to=pre_purchase.valid_to,
                    is_active=pre_purchase.is_active
                )
                db.add(pre_purchase_orm)
            
            # 3. 모든 변경사항 commit (트랜잭션 성공)
            db.commit()
            db.refresh(policy_orm)
            
            return {
                "policy": self.policy_repo._orm_to_entity(policy_orm),
                "success": True
            }
            
        except Exception as e:
            # 에러 발생 시 롤백
            db.rollback()
            raise ValueError(f"할인 정책 생성 실패: {str(e)}")
    
    async def get_discount_policy_details(self, policy_id: int) -> Dict[str, Any]:
        """할인 정책 상세 조회 (모든 유형 포함)"""
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
