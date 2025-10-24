"""
할인 정책 API 라우터 - 기본 할인 정책 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from ....application.discount_service import DiscountPolicyService
from ....presentation.dependencies import get_discount_policy_service, get_current_active_user
from ....presentation.schemas import (
    DiscountPolicyCreate,
    DiscountPolicyUpdate,
    DiscountPolicyResponse,
    DiscountPolicyListResponse,
    DiscountPolicyDetailResponse,
    DiscountPolicyFilterParams,
    PaginationInfo
)
from ....domain.entities import PolicyType, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/discount", tags=["할인 정책"])


# ===== 통합 생성 스키마 =====
class DiscountPolicyCreateWithDetails(BaseModel):
    """트랜잭션으로 할인 정책과 세부 정보 함께 생성"""
    brand_id: int
    vehicle_line_id: int
    trim_id: int
    version_id: int
    policy_type: PolicyType
    title: str
    description: Optional[str] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True
    
    # 세부 정보 (정책 유형에 따라 선택)
    card_partner: Optional[str] = None
    cashback_rate: Optional[float] = None
    discount_rate: Optional[float] = None
    discount_amount: Optional[int] = None
    inventory_level_threshold: Optional[int] = None
    event_type: Optional[str] = None
    pre_purchase_start: Optional[datetime] = None


# ===== 기본 할인 정책 CRUD =====

@router.post("/policies/", response_model=DiscountPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_discount_policy(
    policy_data: DiscountPolicyCreate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 생성"""
    try:
        policy = await service.create_discount_policy(
            brand_id=policy_data.brand_id,
            vehicle_line_id=policy_data.vehicle_line_id,
            trim_id=policy_data.trim_id,
            version_id=policy_data.version_id,
            policy_type=policy_data.policy_type,
            title=policy_data.title,
            description=policy_data.description,
            valid_from=policy_data.valid_from,
            valid_to=policy_data.valid_to,
            is_active=policy_data.is_active
        )
        
        return DiscountPolicyResponse(
            id=policy.id,
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 할인 정책 생성 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"할인 정책 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/policies/{policy_id}", response_model=DiscountPolicyResponse)
async def get_discount_policy(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 단일 조회"""
    policy = await service.get_discount_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
    
    return DiscountPolicyResponse(
        id=policy.id,
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


@router.get("/policies/", response_model=DiscountPolicyListResponse)
async def get_discount_policies(
    brand_id: Optional[int] = Query(None, description="브랜드 ID"),
    trim_id: Optional[int] = Query(None, description="트림 ID"),
    version_id: Optional[int] = Query(None, description="버전 ID"),
    policy_type: Optional[PolicyType] = Query(None, description="정책 유형"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 목록 조회 (페이지네이션)"""
    try:
        result = await service.get_discount_policies(
            brand_id=brand_id,
            trim_id=trim_id,
            version_id=version_id,
            policy_type=policy_type,
            is_active=is_active,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # 응답 데이터 변환
        policies = []
        for policy in result["items"]:
            policies.append(DiscountPolicyResponse(
                id=policy.id,
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
            ))
        
        return DiscountPolicyListResponse(
            items=policies,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="할인 정책 목록 조회 중 오류가 발생했습니다")


@router.put("/policies/{policy_id}", response_model=DiscountPolicyResponse)
async def update_discount_policy(
    policy_id: int,
    policy_data: DiscountPolicyUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 수정"""
    try:
        policy = await service.update_discount_policy(
            policy_id=policy_id,
            title=policy_data.title,
            description=policy_data.description,
            valid_from=policy_data.valid_from,
            valid_to=policy_data.valid_to,
            is_active=policy_data.is_active
        )
        
        return DiscountPolicyResponse(
            id=policy.id,
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="할인 정책 수정 중 오류가 발생했습니다")


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discount_policy(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 삭제"""
    try:
        success = await service.delete_discount_policy(policy_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="할인 정책 삭제 중 오류가 발생했습니다")


# ===== 통합 조회 메서드 =====

@router.post("/policies/with-details", response_model=DiscountPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_discount_policy_with_details(
    policy_data: DiscountPolicyCreateWithDetails,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책과 세부 정보를 트랜잭션으로 함께 생성"""
    try:
        result = await service.create_discount_policy_with_details(
            brand_id=policy_data.brand_id,
            vehicle_line_id=policy_data.vehicle_line_id,
            trim_id=policy_data.trim_id,
            version_id=policy_data.version_id,
            policy_type=policy_data.policy_type,
            title=policy_data.title,
            description=policy_data.description,
            valid_from=policy_data.valid_from,
            valid_to=policy_data.valid_to,
            is_active=policy_data.is_active,
            card_partner=policy_data.card_partner,
            cashback_rate=policy_data.cashback_rate,
            discount_rate=policy_data.discount_rate,
            discount_amount=policy_data.discount_amount,
            inventory_level_threshold=policy_data.inventory_level_threshold,
            event_type=policy_data.event_type,
            pre_purchase_start=policy_data.pre_purchase_start
        )
        
        policy = result["policy"]
        
        return DiscountPolicyResponse(
            id=policy.id,
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 할인 정책 생성 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"할인 정책 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/policies/{policy_id}/details", response_model=DiscountPolicyDetailResponse)
async def get_discount_policy_details(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 상세 조회 (모든 유형 포함)"""
    try:
        result = await service.get_discount_policy_details(policy_id)
        
        if not result.get("policy"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
        
        # 기본 정책 정보 변환
        policy_response = DiscountPolicyResponse(
            id=result["policy"].id,
            brand_id=result["policy"].brand_id,
            vehicle_line_id=result["policy"].vehicle_line_id,
            trim_id=result["policy"].trim_id,
            version_id=result["policy"].version_id,
            policy_type=result["policy"].policy_type,
            title=result["policy"].title,
            description=result["policy"].description,
            valid_from=result["policy"].valid_from,
            valid_to=result["policy"].valid_to,
            is_active=result["policy"].is_active
        )
        
        # 각 유형별 세부 정보 변환
        from ...presentation.schemas import (
            BrandCardBenefitResponse,
            BrandPromoResponse,
            BrandInventoryDiscountResponse,
            BrandPrePurchaseResponse
        )
        
        card_benefits = []
        for benefit in result.get("card_benefits", []):
            card_benefits.append(BrandCardBenefitResponse(
                id=benefit.id,
                discount_policy_id=benefit.discount_policy_id,
                card_partner=benefit.card_partner,
                cashback_rate=benefit.cashback_rate,
                title=benefit.title,
                description=benefit.description,
                valid_from=benefit.valid_from,
                valid_to=benefit.valid_to,
                is_active=benefit.is_active
            ))
        
        promos = []
        for promo in result.get("promos", []):
            promos.append(BrandPromoResponse(
                id=promo.id,
                discount_policy_id=promo.discount_policy_id,
                discount_rate=promo.discount_rate,
                discount_amount=promo.discount_amount,
                title=promo.title,
                description=promo.description,
                valid_from=promo.valid_from,
                valid_to=promo.valid_to,
                is_active=promo.is_active
            ))
        
        inventory_discounts = []
        for discount in result.get("inventory_discounts", []):
            inventory_discounts.append(BrandInventoryDiscountResponse(
                id=discount.id,
                discount_policy_id=discount.discount_policy_id,
                inventory_level_threshold=discount.inventory_level_threshold,
                discount_rate=discount.discount_rate,
                title=discount.title,
                description=discount.description,
                valid_from=discount.valid_from,
                valid_to=discount.valid_to,
                is_active=discount.is_active
            ))
        
        pre_purchases = []
        for pre_purchase in result.get("pre_purchases", []):
            pre_purchases.append(BrandPrePurchaseResponse(
                id=pre_purchase.id,
                discount_policy_id=pre_purchase.discount_policy_id,
                event_type=pre_purchase.event_type,
                discount_rate=pre_purchase.discount_rate,
                discount_amount=pre_purchase.discount_amount,
                title=pre_purchase.title,
                description=pre_purchase.description,
                pre_purchase_start=pre_purchase.pre_purchase_start,
                valid_from=pre_purchase.valid_from,
                valid_to=pre_purchase.valid_to,
                is_active=pre_purchase.is_active
            ))
        
        return DiscountPolicyDetailResponse(
            policy=policy_response,
            card_benefits=card_benefits,
            promos=promos,
            inventory_discounts=inventory_discounts,
            pre_purchases=pre_purchases
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 할인 정책 상세 조회 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"할인 정책 상세 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/versions/{version_id}/summary")
async def get_version_discount_summary(
    version_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """버전별 할인 정책 요약"""
    try:
        result = await service.get_version_discount_summary(version_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="버전별 할인 정책 요약 조회 중 오류가 발생했습니다")


# ===== 통합 삭제 API (기본 정책과 세부 정보 함께 삭제) =====

@router.delete("/policies/{policy_id}/with-details", status_code=status.HTTP_200_OK)
async def delete_discount_policy_with_details(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책과 세부 정보를 트랜잭션으로 함께 삭제"""
    try:
        # 기존 정책 조회
        policy = await service.get_discount_policy(policy_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
        
        # 세부 정보 먼저 삭제
        if policy.policy_type == PolicyType.CARD_BENEFIT:
            card_benefits = await service.get_card_benefits(policy_id=policy_id, limit=100)
            for benefit in card_benefits.get("items", []):
                await service.delete_card_benefit(benefit.id)
        
        elif policy.policy_type == PolicyType.BRAND_PROMO:
            promos = await service.get_promos(policy_id=policy_id, limit=100)
            for promo in promos.get("items", []):
                await service.delete_promo(promo.id)
        
        elif policy.policy_type == PolicyType.INVENTORY:
            inventory_discounts = await service.get_inventory_discounts(policy_id=policy_id, limit=100)
            for discount in inventory_discounts.get("items", []):
                await service.delete_inventory_discount(discount.id)
        
        elif policy.policy_type == PolicyType.PRE_PURCHASE:
            pre_purchases = await service.get_pre_purchases(policy_id=policy_id, limit=100)
            for pre_purchase in pre_purchases.get("items", []):
                await service.delete_pre_purchase(pre_purchase.id)
        
        # 기본 정책 삭제
        await service.delete_discount_policy(policy_id)
        
        return {"message": "할인 정책이 성공적으로 삭제되었습니다", "policy_id": policy_id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 할인 정책 삭제 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"할인 정책 삭제 중 오류가 발생했습니다: {str(e)}")
