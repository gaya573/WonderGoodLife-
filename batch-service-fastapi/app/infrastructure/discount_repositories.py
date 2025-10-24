"""
할인 정책 Repository 구현 - SQLAlchemy 기반
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from datetime import datetime

from ..domain.entities import (
    DiscountPolicy, BrandCardBenefit, BrandPromo, 
    BrandInventoryDiscount, BrandPrePurchase, PolicyType
)
from ..application.ports import (
    DiscountPolicyRepository, BrandCardBenefitRepository,
    BrandPromoRepository, BrandInventoryDiscountRepository,
    BrandPrePurchaseRepository
)
from .orm_models import (
    DiscountPolicyORM, BrandCardBenefitORM, BrandPromoORM,
    BrandInventoryDiscountORM, BrandPrePurchaseORM
)


class SQLAlchemyDiscountPolicyRepository(DiscountPolicyRepository):
    """할인 정책 Repository 구현"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, policy: DiscountPolicy) -> DiscountPolicy:
        """할인 정책 생성"""
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
        
        self.db.add(policy_orm)
        self.db.commit()
        self.db.refresh(policy_orm)
        
        return self._orm_to_entity(policy_orm)
    
    def find_by_id(self, policy_id: int) -> Optional[DiscountPolicy]:
        """ID로 할인 정책 조회"""
        policy_orm = self.db.query(DiscountPolicyORM).filter(
            DiscountPolicyORM.id == policy_id
        ).first()
        
        if not policy_orm:
            return None
        
        return self._orm_to_entity(policy_orm)
    
    def find_by_brand_trim_version(self, brand_id: int, trim_id: int, version_id: int) -> List[DiscountPolicy]:
        """브랜드, 트림, 버전으로 할인 정책 조회"""
        policies_orm = self.db.query(DiscountPolicyORM).filter(
            and_(
                DiscountPolicyORM.brand_id == brand_id,
                DiscountPolicyORM.trim_id == trim_id,
                DiscountPolicyORM.version_id == version_id
            )
        ).all()
        
        return [self._orm_to_entity(policy_orm) for policy_orm in policies_orm]
    
    def find_by_version(self, version_id: int) -> List[DiscountPolicy]:
        """버전별 할인 정책 조회"""
        policies_orm = self.db.query(DiscountPolicyORM).filter(
            DiscountPolicyORM.version_id == version_id
        ).all()
        
        return [self._orm_to_entity(policy_orm) for policy_orm in policies_orm]
    
    def find_all(self, 
                 brand_id: Optional[int] = None,
                 trim_id: Optional[int] = None,
                 version_id: Optional[int] = None,
                 policy_type: Optional[PolicyType] = None,
                 is_active: Optional[bool] = None,
                 limit: int = 20,
                 offset: int = 0,
                 sort_by: str = "created_at",
                 order: str = "desc") -> List[DiscountPolicy]:
        """할인 정책 목록 조회 (페이지네이션)"""
        query = self.db.query(DiscountPolicyORM)
        
        # 필터링
        filters = []
        if brand_id:
            filters.append(DiscountPolicyORM.brand_id == brand_id)
        if trim_id:
            filters.append(DiscountPolicyORM.trim_id == trim_id)
        if version_id:
            filters.append(DiscountPolicyORM.version_id == version_id)
        if policy_type:
            filters.append(DiscountPolicyORM.policy_type == policy_type)
        if is_active is not None:
            filters.append(DiscountPolicyORM.is_active == is_active)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 정렬
        if hasattr(DiscountPolicyORM, sort_by):
            sort_column = getattr(DiscountPolicyORM, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 페이지네이션
        policies_orm = query.offset(offset).limit(limit).all()
        
        return [self._orm_to_entity(policy_orm) for policy_orm in policies_orm]
    
    def count(self, 
              brand_id: Optional[int] = None,
              trim_id: Optional[int] = None,
              version_id: Optional[int] = None,
              policy_type: Optional[PolicyType] = None,
              is_active: Optional[bool] = None) -> int:
        """할인 정책 개수 조회"""
        query = self.db.query(DiscountPolicyORM)
        
        # 필터링
        filters = []
        if brand_id:
            filters.append(DiscountPolicyORM.brand_id == brand_id)
        if trim_id:
            filters.append(DiscountPolicyORM.trim_id == trim_id)
        if version_id:
            filters.append(DiscountPolicyORM.version_id == version_id)
        if policy_type:
            filters.append(DiscountPolicyORM.policy_type == policy_type)
        if is_active is not None:
            filters.append(DiscountPolicyORM.is_active == is_active)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()
    
    def update(self, policy_id: int, policy: DiscountPolicy) -> DiscountPolicy:
        """할인 정책 수정"""
        policy_orm = self.db.query(DiscountPolicyORM).filter(
            DiscountPolicyORM.id == policy_id
        ).first()
        
        if not policy_orm:
            raise ValueError(f"할인 정책을 찾을 수 없습니다: {policy_id}")
        
        # 필드 업데이트
        policy_orm.title = policy.title
        policy_orm.description = policy.description
        policy_orm.valid_from = policy.valid_from
        policy_orm.valid_to = policy.valid_to
        policy_orm.is_active = policy.is_active
        policy_orm.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy_orm)
        
        return self._orm_to_entity(policy_orm)
    
    def delete(self, policy_id: int) -> bool:
        """할인 정책 삭제"""
        policy_orm = self.db.query(DiscountPolicyORM).filter(
            DiscountPolicyORM.id == policy_id
        ).first()
        
        if not policy_orm:
            return False
        
        self.db.delete(policy_orm)
        self.db.commit()
        
        return True
    
    def _orm_to_entity(self, policy_orm: DiscountPolicyORM) -> DiscountPolicy:
        """ORM을 도메인 엔티티로 변환"""
        return DiscountPolicy(
            id=policy_orm.id,
            brand_id=policy_orm.brand_id,
            vehicle_line_id=policy_orm.vehicle_line_id,
            trim_id=policy_orm.trim_id,
            version_id=policy_orm.version_id,
            policy_type=policy_orm.policy_type,
            title=policy_orm.title,
            description=policy_orm.description,
            valid_from=policy_orm.valid_from,
            valid_to=policy_orm.valid_to,
            is_active=policy_orm.is_active
        )


class SQLAlchemyBrandCardBenefitRepository(BrandCardBenefitRepository):
    """카드사 제휴 Repository 구현"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, benefit: BrandCardBenefit) -> BrandCardBenefit:
        """카드사 제휴 생성"""
        benefit_orm = BrandCardBenefitORM(
            discount_policy_id=benefit.discount_policy_id,
            card_partner=benefit.card_partner,
            cashback_rate=str(benefit.cashback_rate),
            title=benefit.title,
            description=benefit.description,
            valid_from=benefit.valid_from,
            valid_to=benefit.valid_to,
            is_active=benefit.is_active
        )
        
        self.db.add(benefit_orm)
        self.db.commit()
        self.db.refresh(benefit_orm)
        
        return self._orm_to_entity(benefit_orm)
    
    def create_bulk(self, benefits: List[BrandCardBenefit]) -> List[BrandCardBenefit]:
        """카드사 제휴 일괄 생성"""
        benefit_orms = []
        for benefit in benefits:
            benefit_orm = BrandCardBenefitORM(
                discount_policy_id=benefit.discount_policy_id,
                card_partner=benefit.card_partner,
                cashback_rate=str(benefit.cashback_rate),
                title=benefit.title,
                description=benefit.description,
                valid_from=benefit.valid_from,
                valid_to=benefit.valid_to,
                is_active=benefit.is_active
            )
            benefit_orms.append(benefit_orm)
        
        self.db.add_all(benefit_orms)
        self.db.commit()
        
        for benefit_orm in benefit_orms:
            self.db.refresh(benefit_orm)
        
        return [self._orm_to_entity(benefit_orm) for benefit_orm in benefit_orms]
    
    def find_by_id(self, benefit_id: int) -> Optional[BrandCardBenefit]:
        """ID로 카드사 제휴 조회"""
        benefit_orm = self.db.query(BrandCardBenefitORM).filter(
            BrandCardBenefitORM.id == benefit_id
        ).first()
        
        if not benefit_orm:
            return None
        
        return self._orm_to_entity(benefit_orm)
    
    def find_by_policy_id(self, policy_id: int) -> List[BrandCardBenefit]:
        """정책 ID로 카드사 제휴 조회"""
        benefits_orm = self.db.query(BrandCardBenefitORM).filter(
            BrandCardBenefitORM.discount_policy_id == policy_id
        ).all()
        
        return [self._orm_to_entity(benefit_orm) for benefit_orm in benefits_orm]
    
    def find_all(self, 
                 policy_id: Optional[int] = None,
                 card_partner: Optional[str] = None,
                 is_active: Optional[bool] = None,
                 limit: int = 20,
                 offset: int = 0,
                 sort_by: str = "created_at",
                 order: str = "desc") -> List[BrandCardBenefit]:
        """카드사 제휴 목록 조회 (페이지네이션)"""
        query = self.db.query(BrandCardBenefitORM)
        
        # 필터링
        filters = []
        if policy_id:
            filters.append(BrandCardBenefitORM.discount_policy_id == policy_id)
        if card_partner:
            filters.append(BrandCardBenefitORM.card_partner.ilike(f"%{card_partner}%"))
        if is_active is not None:
            filters.append(BrandCardBenefitORM.is_active == is_active)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 정렬
        if hasattr(BrandCardBenefitORM, sort_by):
            sort_column = getattr(BrandCardBenefitORM, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 페이지네이션
        benefits_orm = query.offset(offset).limit(limit).all()
        
        return [self._orm_to_entity(benefit_orm) for benefit_orm in benefits_orm]
    
    def update(self, benefit_id: int, benefit: BrandCardBenefit) -> BrandCardBenefit:
        """카드사 제휴 수정"""
        benefit_orm = self.db.query(BrandCardBenefitORM).filter(
            BrandCardBenefitORM.id == benefit_id
        ).first()
        
        if not benefit_orm:
            raise ValueError(f"카드사 제휴를 찾을 수 없습니다: {benefit_id}")
        
        # 필드 업데이트
        benefit_orm.card_partner = benefit.card_partner
        benefit_orm.cashback_rate = str(benefit.cashback_rate)
        benefit_orm.title = benefit.title
        benefit_orm.description = benefit.description
        benefit_orm.valid_from = benefit.valid_from
        benefit_orm.valid_to = benefit.valid_to
        benefit_orm.is_active = benefit.is_active
        
        self.db.commit()
        self.db.refresh(benefit_orm)
        
        return self._orm_to_entity(benefit_orm)
    
    def delete(self, benefit_id: int) -> bool:
        """카드사 제휴 삭제"""
        benefit_orm = self.db.query(BrandCardBenefitORM).filter(
            BrandCardBenefitORM.id == benefit_id
        ).first()
        
        if not benefit_orm:
            return False
        
        self.db.delete(benefit_orm)
        self.db.commit()
        
        return True
    
    def _orm_to_entity(self, benefit_orm: BrandCardBenefitORM) -> BrandCardBenefit:
        """ORM을 도메인 엔티티로 변환"""
        return BrandCardBenefit(
            id=benefit_orm.id,
            discount_policy_id=benefit_orm.discount_policy_id,
            card_partner=benefit_orm.card_partner,
            cashback_rate=float(benefit_orm.cashback_rate),
            title=benefit_orm.title,
            description=benefit_orm.description,
            valid_from=benefit_orm.valid_from,
            valid_to=benefit_orm.valid_to,
            is_active=benefit_orm.is_active
        )


class SQLAlchemyBrandPromoRepository(BrandPromoRepository):
    """브랜드 프로모션 Repository 구현"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, promo: BrandPromo) -> BrandPromo:
        promo_orm = BrandPromoORM(
            discount_policy_id=promo.discount_policy_id,
            discount_rate=str(promo.discount_rate) if promo.discount_rate else None,
            discount_amount=promo.discount_amount,
            title=promo.title,
            description=promo.description,
            valid_from=promo.valid_from,
            valid_to=promo.valid_to,
            is_active=promo.is_active
        )
        self.db.add(promo_orm)
        self.db.commit()
        self.db.refresh(promo_orm)
        return self._orm_to_entity(promo_orm)
    
    def create_bulk(self, promos: List[BrandPromo]) -> List[BrandPromo]:
        promo_orms = []
        for promo in promos:
            promo_orm = BrandPromoORM(
                discount_policy_id=promo.discount_policy_id,
                discount_rate=str(promo.discount_rate) if promo.discount_rate else None,
                discount_amount=promo.discount_amount,
                title=promo.title,
                description=promo.description,
                valid_from=promo.valid_from,
                valid_to=promo.valid_to,
                is_active=promo.is_active
            )
            promo_orms.append(promo_orm)
        self.db.add_all(promo_orms)
        self.db.commit()
        for promo_orm in promo_orms:
            self.db.refresh(promo_orm)
        return [self._orm_to_entity(promo_orm) for promo_orm in promo_orms]
    
    def find_by_id(self, promo_id: int) -> Optional[BrandPromo]:
        promo_orm = self.db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        return self._orm_to_entity(promo_orm) if promo_orm else None
    
    def find_by_policy_id(self, policy_id: int) -> List[BrandPromo]:
        promos_orm = self.db.query(BrandPromoORM).filter(BrandPromoORM.discount_policy_id == policy_id).all()
        return [self._orm_to_entity(promo_orm) for promo_orm in promos_orm]
    
    def find_all(self, policy_id: Optional[int] = None, is_active: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "created_at",
                 order: str = "desc") -> List[BrandPromo]:
        query = self.db.query(BrandPromoORM)
        filters = []
        if policy_id:
            filters.append(BrandPromoORM.discount_policy_id == policy_id)
        if is_active is not None:
            filters.append(BrandPromoORM.is_active == is_active)
        if filters:
            query = query.filter(and_(*filters))
        if hasattr(BrandPromoORM, sort_by):
            sort_column = getattr(BrandPromoORM, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        promos_orm = query.offset(offset).limit(limit).all()
        return [self._orm_to_entity(promo_orm) for promo_orm in promos_orm]
    
    def update(self, promo_id: int, promo: BrandPromo) -> BrandPromo:
        promo_orm = self.db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        if not promo_orm:
            raise ValueError(f"브랜드 프로모션을 찾을 수 없습니다: {promo_id}")
        promo_orm.discount_rate = str(promo.discount_rate) if promo.discount_rate else None
        promo_orm.discount_amount = promo.discount_amount
        promo_orm.title = promo.title
        promo_orm.description = promo.description
        promo_orm.valid_from = promo.valid_from
        promo_orm.valid_to = promo.valid_to
        promo_orm.is_active = promo.is_active
        self.db.commit()
        self.db.refresh(promo_orm)
        return self._orm_to_entity(promo_orm)
    
    def delete(self, promo_id: int) -> bool:
        promo_orm = self.db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        if not promo_orm:
            return False
        self.db.delete(promo_orm)
        self.db.commit()
        return True
    
    def _orm_to_entity(self, promo_orm: BrandPromoORM) -> BrandPromo:
        return BrandPromo(
            id=promo_orm.id,
            discount_policy_id=promo_orm.discount_policy_id,
            discount_rate=float(promo_orm.discount_rate) if promo_orm.discount_rate else None,
            discount_amount=promo_orm.discount_amount,
            title=promo_orm.title,
            description=promo_orm.description,
            valid_from=promo_orm.valid_from,
            valid_to=promo_orm.valid_to,
            is_active=promo_orm.is_active
        )


class SQLAlchemyBrandInventoryDiscountRepository(BrandInventoryDiscountRepository):
    """재고 할인 Repository 구현"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        discount_orm = BrandInventoryDiscountORM(
            discount_policy_id=discount.discount_policy_id,
            inventory_level_threshold=discount.inventory_level_threshold,
            discount_rate=str(discount.discount_rate),
            title=discount.title,
            description=discount.description,
            valid_from=discount.valid_from,
            valid_to=discount.valid_to,
            is_active=discount.is_active
        )
        self.db.add(discount_orm)
        self.db.commit()
        self.db.refresh(discount_orm)
        return self._orm_to_entity(discount_orm)
    
    def create_bulk(self, discounts: List[BrandInventoryDiscount]) -> List[BrandInventoryDiscount]:
        discount_orms = []
        for discount in discounts:
            discount_orm = BrandInventoryDiscountORM(
                discount_policy_id=discount.discount_policy_id,
                inventory_level_threshold=discount.inventory_level_threshold,
                discount_rate=str(discount.discount_rate),
                title=discount.title,
                description=discount.description,
                valid_from=discount.valid_from,
                valid_to=discount.valid_to,
                is_active=discount.is_active
            )
            discount_orms.append(discount_orm)
        self.db.add_all(discount_orms)
        self.db.commit()
        for discount_orm in discount_orms:
            self.db.refresh(discount_orm)
        return [self._orm_to_entity(discount_orm) for discount_orm in discount_orms]
    
    def find_by_id(self, discount_id: int) -> Optional[BrandInventoryDiscount]:
        discount_orm = self.db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        return self._orm_to_entity(discount_orm) if discount_orm else None
    
    def find_by_policy_id(self, policy_id: int) -> List[BrandInventoryDiscount]:
        discounts_orm = self.db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.discount_policy_id == policy_id).all()
        return [self._orm_to_entity(discount_orm) for discount_orm in discounts_orm]
    
    def find_all(self, policy_id: Optional[int] = None, is_active: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "created_at",
                 order: str = "desc") -> List[BrandInventoryDiscount]:
        query = self.db.query(BrandInventoryDiscountORM)
        filters = []
        if policy_id:
            filters.append(BrandInventoryDiscountORM.discount_policy_id == policy_id)
        if is_active is not None:
            filters.append(BrandInventoryDiscountORM.is_active == is_active)
        if filters:
            query = query.filter(and_(*filters))
        if hasattr(BrandInventoryDiscountORM, sort_by):
            sort_column = getattr(BrandInventoryDiscountORM, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        discounts_orm = query.offset(offset).limit(limit).all()
        return [self._orm_to_entity(discount_orm) for discount_orm in discounts_orm]
    
    def update(self, discount_id: int, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        discount_orm = self.db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        if not discount_orm:
            raise ValueError(f"재고 할인을 찾을 수 없습니다: {discount_id}")
        discount_orm.inventory_level_threshold = discount.inventory_level_threshold
        discount_orm.discount_rate = str(discount.discount_rate)
        discount_orm.title = discount.title
        discount_orm.description = discount.description
        discount_orm.valid_from = discount.valid_from
        discount_orm.valid_to = discount.valid_to
        discount_orm.is_active = discount.is_active
        self.db.commit()
        self.db.refresh(discount_orm)
        return self._orm_to_entity(discount_orm)
    
    def delete(self, discount_id: int) -> bool:
        discount_orm = self.db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        if not discount_orm:
            return False
        self.db.delete(discount_orm)
        self.db.commit()
        return True
    
    def _orm_to_entity(self, discount_orm: BrandInventoryDiscountORM) -> BrandInventoryDiscount:
        return BrandInventoryDiscount(
            id=discount_orm.id,
            discount_policy_id=discount_orm.discount_policy_id,
            inventory_level_threshold=discount_orm.inventory_level_threshold,
            discount_rate=float(discount_orm.discount_rate),
            title=discount_orm.title,
            description=discount_orm.description,
            valid_from=discount_orm.valid_from,
            valid_to=discount_orm.valid_to,
            is_active=discount_orm.is_active
        )


class SQLAlchemyBrandPrePurchaseRepository(BrandPrePurchaseRepository):
    """선구매 할인 Repository 구현"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        pre_purchase_orm = BrandPrePurchaseORM(
            discount_policy_id=pre_purchase.discount_policy_id,
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
        self.db.add(pre_purchase_orm)
        self.db.commit()
        self.db.refresh(pre_purchase_orm)
        return self._orm_to_entity(pre_purchase_orm)
    
    def create_bulk(self, pre_purchases: List[BrandPrePurchase]) -> List[BrandPrePurchase]:
        pre_purchase_orms = []
        for pre_purchase in pre_purchases:
            pre_purchase_orm = BrandPrePurchaseORM(
                discount_policy_id=pre_purchase.discount_policy_id,
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
            pre_purchase_orms.append(pre_purchase_orm)
        self.db.add_all(pre_purchase_orms)
        self.db.commit()
        for pre_purchase_orm in pre_purchase_orms:
            self.db.refresh(pre_purchase_orm)
        return [self._orm_to_entity(pre_purchase_orm) for pre_purchase_orm in pre_purchase_orms]
    
    def find_by_id(self, pre_purchase_id: int) -> Optional[BrandPrePurchase]:
        pre_purchase_orm = self.db.query(BrandPrePurchaseORM).filter(BrandPrePurchaseORM.id == pre_purchase_id).first()
        return self._orm_to_entity(pre_purchase_orm) if pre_purchase_orm else None
    
    def find_by_policy_id(self, policy_id: int) -> List[BrandPrePurchase]:
        pre_purchases_orm = self.db.query(BrandPrePurchaseORM).filter(BrandPrePurchaseORM.discount_policy_id == policy_id).all()
        return [self._orm_to_entity(pre_purchase_orm) for pre_purchase_orm in pre_purchases_orm]
    
    def find_all(self, policy_id: Optional[int] = None, event_type: Optional[str] = None,
                 is_active: Optional[bool] = None, limit: int = 20, offset: int = 0,
                 sort_by: str = "created_at", order: str = "desc") -> List[BrandPrePurchase]:
        query = self.db.query(BrandPrePurchaseORM)
        filters = []
        if policy_id:
            filters.append(BrandPrePurchaseORM.discount_policy_id == policy_id)
        if event_type:
            filters.append(BrandPrePurchaseORM.event_type == event_type)
        if is_active is not None:
            filters.append(BrandPrePurchaseORM.is_active == is_active)
        if filters:
            query = query.filter(and_(*filters))
        if hasattr(BrandPrePurchaseORM, sort_by):
            sort_column = getattr(BrandPrePurchaseORM, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        pre_purchases_orm = query.offset(offset).limit(limit).all()
        return [self._orm_to_entity(pre_purchase_orm) for pre_purchase_orm in pre_purchases_orm]
    
    def update(self, pre_purchase_id: int, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        pre_purchase_orm = self.db.query(BrandPrePurchaseORM).filter(BrandPrePurchaseORM.id == pre_purchase_id).first()
        if not pre_purchase_orm:
            raise ValueError(f"선구매 할인을 찾을 수 없습니다: {pre_purchase_id}")
        pre_purchase_orm.event_type = pre_purchase.event_type
        pre_purchase_orm.discount_rate = str(pre_purchase.discount_rate) if pre_purchase.discount_rate else None
        pre_purchase_orm.discount_amount = pre_purchase.discount_amount
        pre_purchase_orm.title = pre_purchase.title
        pre_purchase_orm.description = pre_purchase.description
        pre_purchase_orm.pre_purchase_start = pre_purchase.pre_purchase_start
        pre_purchase_orm.valid_from = pre_purchase.valid_from
        pre_purchase_orm.valid_to = pre_purchase.valid_to
        pre_purchase_orm.is_active = pre_purchase.is_active
        self.db.commit()
        self.db.refresh(pre_purchase_orm)
        return self._orm_to_entity(pre_purchase_orm)
    
    def delete(self, pre_purchase_id: int) -> bool:
        pre_purchase_orm = self.db.query(BrandPrePurchaseORM).filter(BrandPrePurchaseORM.id == pre_purchase_id).first()
        if not pre_purchase_orm:
            return False
        self.db.delete(pre_purchase_orm)
        self.db.commit()
        return True
    
    def _orm_to_entity(self, pre_purchase_orm: BrandPrePurchaseORM) -> BrandPrePurchase:
        return BrandPrePurchase(
            id=pre_purchase_orm.id,
            discount_policy_id=pre_purchase_orm.discount_policy_id,
            event_type=pre_purchase_orm.event_type,
            discount_rate=float(pre_purchase_orm.discount_rate) if pre_purchase_orm.discount_rate else None,
            discount_amount=pre_purchase_orm.discount_amount,
            title=pre_purchase_orm.title,
            description=pre_purchase_orm.description,
            pre_purchase_start=pre_purchase_orm.pre_purchase_start,
            valid_from=pre_purchase_orm.valid_from,
            valid_to=pre_purchase_orm.valid_to,
            is_active=pre_purchase_orm.is_active
        )
