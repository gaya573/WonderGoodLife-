"""
Ports - 인터페이스 정의 (추상화)
외부 의존성을 추상화하여 도메인이 인프라에 의존하지 않도록 함
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..domain.entities import Brand, Model, Trim, TrimCarColor, OptionTitle, OptionPrice, StagingOption, DiscountPolicy, BrandCardBenefit, BrandPromo, BrandInventoryDiscount, BrandPrePurchase, PolicyType


# ===== Repository Ports =====
class BrandRepository(ABC):
    """브랜드 저장소 인터페이스"""
    
    @abstractmethod
    def find_by_id(self, brand_id: int) -> Optional[Brand]:
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Brand]:
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Brand]:
        pass
    
    @abstractmethod
    def save(self, brand: Brand) -> Brand:
        pass
    
    @abstractmethod
    def update(self, brand_id: int, brand: Brand) -> Optional[Brand]:
        pass
    
    @abstractmethod
    def delete(self, brand_id: int) -> bool:
        pass


class ModelRepository(ABC):
    """모델 저장소 인터페이스"""
    
    @abstractmethod
    def find_by_id(self, model_id: int) -> Optional[Model]:
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Model]:
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Model]:
        pass
    
    @abstractmethod
    def save(self, model: Model) -> Model:
        pass
    
    @abstractmethod
    def update(self, model_id: int, model: Model) -> Optional[Model]:
        pass
    
    @abstractmethod
    def delete(self, model_id: int) -> bool:
        pass


class TrimRepository(ABC):
    """트림 저장소 인터페이스"""
    
    @abstractmethod
    def find_by_id(self, trim_id: int) -> Optional[Trim]:
        pass
    
    @abstractmethod
    def find_by_model_and_name(self, model_id: int, name: str) -> Optional[Trim]:
        pass
    
    @abstractmethod
    def find_all(self, model_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Trim]:
        pass
    
    @abstractmethod
    def save(self, trim: Trim) -> Trim:
        pass
    
    @abstractmethod
    def update(self, trim_id: int, trim: Trim) -> Optional[Trim]:
        pass
    
    @abstractmethod
    def delete(self, trim_id: int) -> bool:
        pass


class ColorRepository(ABC):
    """색상 저장소 인터페이스"""
    
    @abstractmethod
    def find_by_trim_and_name(self, trim_id: int, name: str) -> Optional[TrimCarColor]:
        pass
    
    @abstractmethod
    def save(self, color: TrimCarColor) -> TrimCarColor:
        pass


class OptionRepository(ABC):
    """옵션 저장소 인터페이스"""
    
    @abstractmethod
    def find_title_by_trim_and_name(self, trim_id: int, name: str) -> Optional[OptionTitle]:
        pass
    
    @abstractmethod
    def save_title(self, option_title: OptionTitle) -> OptionTitle:
        pass
    
    @abstractmethod
    def find_price_by_title_and_name(self, title_id: int, name: str) -> Optional[OptionPrice]:
        pass
    
    @abstractmethod
    def save_price(self, option_price: OptionPrice) -> OptionPrice:
        pass


class StagingOptionRepository(ABC):
    """Staging 옵션 저장소 인터페이스 - 통합된 옵션 관리"""
    
    @abstractmethod
    def find_by_id(self, option_id: int) -> Optional[StagingOption]:
        pass
    
    @abstractmethod
    def find_by_trim_and_name(self, trim_id: int, name: str) -> Optional[StagingOption]:
        pass
    
    @abstractmethod
    def find_all_by_trim(self, trim_id: int, skip: int = 0, limit: int = 100) -> List[StagingOption]:
        pass
    
    @abstractmethod
    def save(self, option: StagingOption) -> StagingOption:
        pass
    
    @abstractmethod
    def update(self, option_id: int, option: StagingOption) -> Optional[StagingOption]:
        pass
    
    @abstractmethod
    def delete(self, option_id: int) -> bool:
        pass


# ===== Excel Parser Port =====
class ExcelParser(ABC):
    """엑셀 파서 인터페이스 - 시트별 브랜드 처리"""
    
    @abstractmethod
    async def parse(self, file_content: bytes) -> Dict[str, List[dict]]:
        """
        엑셀 파일을 파싱하여 브랜드별 딕셔너리 리스트로 반환
        
        반환: {
            "현대": [{"RowType": "TRIM", "Model": "아반떼", ...}, ...],
            "기아": [{"RowType": "TRIM", "Model": "모닝", ...}, ...],
            ...
        }
        """
        pass


# ===== 할인 정책 Repository Ports =====
class DiscountPolicyRepository(ABC):
    """할인 정책 저장소 인터페이스"""
    
    @abstractmethod
    def create(self, policy: DiscountPolicy) -> DiscountPolicy:
        pass
    
    @abstractmethod
    def find_by_id(self, policy_id: int) -> Optional[DiscountPolicy]:
        pass
    
    @abstractmethod
    def find_by_brand_trim_version(self, brand_id: int, trim_id: int, version_id: int) -> List[DiscountPolicy]:
        pass
    
    @abstractmethod
    def find_by_version(self, version_id: int) -> List[DiscountPolicy]:
        pass
    
    @abstractmethod
    def find_all(self, brand_id: Optional[int] = None, trim_id: Optional[int] = None, 
                 version_id: Optional[int] = None, policy_type: Optional[PolicyType] = None,
                 is_active: Optional[bool] = None, limit: int = 20, offset: int = 0,
                 sort_by: str = "created_at", order: str = "desc") -> List[DiscountPolicy]:
        pass
    
    @abstractmethod
    def count(self, brand_id: Optional[int] = None, trim_id: Optional[int] = None,
              version_id: Optional[int] = None, policy_type: Optional[PolicyType] = None,
              is_active: Optional[bool] = None) -> int:
        pass
    
    @abstractmethod
    def update(self, policy_id: int, policy: DiscountPolicy) -> DiscountPolicy:
        pass
    
    @abstractmethod
    def delete(self, policy_id: int) -> bool:
        pass


class BrandCardBenefitRepository(ABC):
    """카드사 제휴 저장소 인터페이스"""
    
    @abstractmethod
    def create(self, benefit: BrandCardBenefit) -> BrandCardBenefit:
        pass
    
    @abstractmethod
    def create_bulk(self, benefits: List[BrandCardBenefit]) -> List[BrandCardBenefit]:
        pass
    
    @abstractmethod
    def find_by_id(self, benefit_id: int) -> Optional[BrandCardBenefit]:
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandCardBenefit]:
        pass
    
    @abstractmethod
    def find_all(self, policy_id: Optional[int] = None, card_partner: Optional[str] = None,
                 is_active: Optional[bool] = None, limit: int = 20, offset: int = 0,
                 sort_by: str = "created_at", order: str = "desc") -> List[BrandCardBenefit]:
        pass
    
    @abstractmethod
    def update(self, benefit_id: int, benefit: BrandCardBenefit) -> BrandCardBenefit:
        pass
    
    @abstractmethod
    def delete(self, benefit_id: int) -> bool:
        pass


class BrandPromoRepository(ABC):
    """브랜드 프로모션 저장소 인터페이스"""
    
    @abstractmethod
    def create(self, promo: BrandPromo) -> BrandPromo:
        pass
    
    @abstractmethod
    def create_bulk(self, promos: List[BrandPromo]) -> List[BrandPromo]:
        pass
    
    @abstractmethod
    def find_by_id(self, promo_id: int) -> Optional[BrandPromo]:
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandPromo]:
        pass
    
    @abstractmethod
    def find_all(self, policy_id: Optional[int] = None, is_active: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "created_at",
                 order: str = "desc") -> List[BrandPromo]:
        pass
    
    @abstractmethod
    def update(self, promo_id: int, promo: BrandPromo) -> BrandPromo:
        pass
    
    @abstractmethod
    def delete(self, promo_id: int) -> bool:
        pass


class BrandInventoryDiscountRepository(ABC):
    """재고 할인 저장소 인터페이스"""
    
    @abstractmethod
    def create(self, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        pass
    
    @abstractmethod
    def create_bulk(self, discounts: List[BrandInventoryDiscount]) -> List[BrandInventoryDiscount]:
        pass
    
    @abstractmethod
    def find_by_id(self, discount_id: int) -> Optional[BrandInventoryDiscount]:
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandInventoryDiscount]:
        pass
    
    @abstractmethod
    def find_all(self, policy_id: Optional[int] = None, is_active: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "created_at",
                 order: str = "desc") -> List[BrandInventoryDiscount]:
        pass
    
    @abstractmethod
    def update(self, discount_id: int, discount: BrandInventoryDiscount) -> BrandInventoryDiscount:
        pass
    
    @abstractmethod
    def delete(self, discount_id: int) -> bool:
        pass


class BrandPrePurchaseRepository(ABC):
    """선구매 할인 저장소 인터페이스"""
    
    @abstractmethod
    def create(self, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        pass
    
    @abstractmethod
    def create_bulk(self, pre_purchases: List[BrandPrePurchase]) -> List[BrandPrePurchase]:
        pass
    
    @abstractmethod
    def find_by_id(self, pre_purchase_id: int) -> Optional[BrandPrePurchase]:
        pass
    
    @abstractmethod
    def find_by_policy_id(self, policy_id: int) -> List[BrandPrePurchase]:
        pass
    
    @abstractmethod
    def find_all(self, policy_id: Optional[int] = None, event_type: Optional[str] = None,
                 is_active: Optional[bool] = None, limit: int = 20, offset: int = 0,
                 sort_by: str = "created_at", order: str = "desc") -> List[BrandPrePurchase]:
        pass
    
    @abstractmethod
    def update(self, pre_purchase_id: int, pre_purchase: BrandPrePurchase) -> BrandPrePurchase:
        pass
    
    @abstractmethod
    def delete(self, pre_purchase_id: int) -> bool:
        pass

