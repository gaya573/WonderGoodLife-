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

router = APIRouter(prefix="/api/discount", tags=["할인 정책"])


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="할인 정책 생성 중 오류가 발생했습니다")


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

@router.get("/policies/{policy_id}/details", response_model=DiscountPolicyDetailResponse)
async def get_discount_policy_details(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 상세 조회 (모든 유형 포함)"""
    try:
        result = await service.get_discount_policy_details(policy_id)
        
        # 기본 정책 정보 변환
        policy_response = DiscountPolicyResponse(
            id=result["policy"].id,
            brand_id=result["policy"].brand_id,
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
        for benefit in result["card_benefits"]:
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
        for promo in result["promos"]:
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
        for discount in result["inventory_discounts"]:
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
        for pre_purchase in result["pre_purchases"]:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="할인 정책 상세 조회 중 오류가 발생했습니다")


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
