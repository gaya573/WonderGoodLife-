"""
카드사 제휴 API 라우터 - 카드사 제휴 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from ....application.discount_service import DiscountPolicyService
from ....presentation.dependencies import get_discount_policy_service, get_current_active_user
from ....presentation.schemas import (
    BrandCardBenefitCreate,
    BrandCardBenefitUpdate,
    BrandCardBenefitResponse,
    BrandCardBenefitListResponse,
    CardBenefitFilterParams
)
from ....domain.entities import User

router = APIRouter(prefix="/api/discount", tags=["카드사 제휴"])


# ===== 카드사 제휴 CRUD =====

@router.post("/card-benefits/", response_model=BrandCardBenefitResponse, status_code=status.HTTP_201_CREATED)
async def create_card_benefit(
    benefit_data: BrandCardBenefitCreate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 생성"""
    try:
        benefit = await service.create_card_benefit(
            discount_policy_id=benefit_data.discount_policy_id,
            card_partner=benefit_data.card_partner,
            cashback_rate=benefit_data.cashback_rate,
            title=benefit_data.title,
            description=benefit_data.description,
            valid_from=benefit_data.valid_from,
            valid_to=benefit_data.valid_to,
            is_active=benefit_data.is_active
        )
        
        return BrandCardBenefitResponse(
            id=benefit.id,
            discount_policy_id=benefit.discount_policy_id,
            card_partner=benefit.card_partner,
            cashback_rate=benefit.cashback_rate,
            title=benefit.title,
            description=benefit.description,
            valid_from=benefit.valid_from,
            valid_to=benefit.valid_to,
            is_active=benefit.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="카드사 제휴 생성 중 오류가 발생했습니다")


@router.get("/card-benefits/{benefit_id}", response_model=BrandCardBenefitResponse)
async def get_card_benefit(
    benefit_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 단일 조회"""
    benefit = await service.get_card_benefit(benefit_id)
    if not benefit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="카드사 제휴를 찾을 수 없습니다")
    
    return BrandCardBenefitResponse(
        id=benefit.id,
        discount_policy_id=benefit.discount_policy_id,
        card_partner=benefit.card_partner,
        cashback_rate=benefit.cashback_rate,
        title=benefit.title,
        description=benefit.description,
        valid_from=benefit.valid_from,
        valid_to=benefit.valid_to,
        is_active=benefit.is_active
    )


@router.get("/card-benefits/", response_model=BrandCardBenefitListResponse)
async def get_card_benefits(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    card_partner: Optional[str] = Query(None, description="카드사명"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 목록 조회 (페이지네이션)"""
    try:
        result = await service.get_card_benefits(
            policy_id=policy_id,
            card_partner=card_partner,
            is_active=is_active,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # 응답 데이터 변환
        benefits = []
        for benefit in result["items"]:
            benefits.append(BrandCardBenefitResponse(
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
        
        return BrandCardBenefitListResponse(
            items=benefits,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="카드사 제휴 목록 조회 중 오류가 발생했습니다")


@router.put("/card-benefits/{benefit_id}", response_model=BrandCardBenefitResponse)
async def update_card_benefit(
    benefit_id: int,
    benefit_data: BrandCardBenefitUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 수정"""
    try:
        benefit = await service.update_card_benefit(
            benefit_id=benefit_id,
            card_partner=benefit_data.card_partner,
            cashback_rate=benefit_data.cashback_rate,
            title=benefit_data.title,
            description=benefit_data.description,
            valid_from=benefit_data.valid_from,
            valid_to=benefit_data.valid_to,
            is_active=benefit_data.is_active
        )
        
        return BrandCardBenefitResponse(
            id=benefit.id,
            discount_policy_id=benefit.discount_policy_id,
            card_partner=benefit.card_partner,
            cashback_rate=benefit.cashback_rate,
            title=benefit.title,
            description=benefit.description,
            valid_from=benefit.valid_from,
            valid_to=benefit.valid_to,
            is_active=benefit.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="카드사 제휴 수정 중 오류가 발생했습니다")


@router.delete("/card-benefits/{benefit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card_benefit(
    benefit_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 삭제"""
    try:
        success = await service.delete_card_benefit(benefit_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="카드사 제휴를 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="카드사 제휴 삭제 중 오류가 발생했습니다")


# ===== 일괄 처리 메서드 =====

@router.post("/card-benefits/bulk", response_model=List[BrandCardBenefitResponse], status_code=status.HTTP_201_CREATED)
async def create_card_benefits_bulk(
    benefits_data: List[BrandCardBenefitCreate],
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """카드사 제휴 일괄 생성"""
    try:
        benefits = []
        for benefit_data in benefits_data:
            benefit = await service.create_card_benefit(
                discount_policy_id=benefit_data.discount_policy_id,
                card_partner=benefit_data.card_partner,
                cashback_rate=benefit_data.cashback_rate,
                title=benefit_data.title,
                description=benefit_data.description,
                valid_from=benefit_data.valid_from,
                valid_to=benefit_data.valid_to,
                is_active=benefit_data.is_active
            )
            benefits.append(BrandCardBenefitResponse(
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
        
        return benefits
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="카드사 제휴 일괄 생성 중 오류가 발생했습니다")
