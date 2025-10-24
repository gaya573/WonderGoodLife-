"""
브랜드 프로모션 API 라우터 - 브랜드 프로모션 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from ....application.discount_service import DiscountPolicyService
from ....presentation.dependencies import get_discount_policy_service, get_current_active_user
from ....presentation.schemas import (
    BrandPromoCreate,
    BrandPromoUpdate,
    BrandPromoResponse,
    BrandPromoListResponse,
    PromoFilterParams
)
from ....domain.entities import User

router = APIRouter(prefix="/api/discount", tags=["브랜드 프로모션"])


# ===== 브랜드 프로모션 CRUD =====

@router.post("/promos/", response_model=BrandPromoResponse, status_code=status.HTTP_201_CREATED)
async def create_promo(
    promo_data: BrandPromoCreate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 생성"""
    try:
        promo = await service.create_promo(
            discount_policy_id=promo_data.discount_policy_id,
            discount_rate=promo_data.discount_rate,
            discount_amount=promo_data.discount_amount,
            title=promo_data.title,
            description=promo_data.description,
            valid_from=promo_data.valid_from,
            valid_to=promo_data.valid_to,
            is_active=promo_data.is_active
        )
        
        return BrandPromoResponse(
            id=promo.id,
            discount_policy_id=promo.discount_policy_id,
            discount_rate=promo.discount_rate,
            discount_amount=promo.discount_amount,
            title=promo.title,
            description=promo.description,
            valid_from=promo.valid_from,
            valid_to=promo.valid_to,
            is_active=promo.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="브랜드 프로모션 생성 중 오류가 발생했습니다")


@router.get("/promos/{promo_id}", response_model=BrandPromoResponse)
async def get_promo(
    promo_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 단일 조회"""
    promo = await service.get_promo(promo_id)
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="브랜드 프로모션을 찾을 수 없습니다")
    
    return BrandPromoResponse(
        id=promo.id,
        discount_policy_id=promo.discount_policy_id,
        discount_rate=promo.discount_rate,
        discount_amount=promo.discount_amount,
        title=promo.title,
        description=promo.description,
        valid_from=promo.valid_from,
        valid_to=promo.valid_to,
        is_active=promo.is_active
    )


@router.get("/promos/", response_model=BrandPromoListResponse)
async def get_promos(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 목록 조회 (페이지네이션)"""
    try:
        result = await service.get_promos(
            policy_id=policy_id,
            is_active=is_active,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # 응답 데이터 변환
        promos = []
        for promo in result["items"]:
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
        
        return BrandPromoListResponse(
            items=promos,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="브랜드 프로모션 목록 조회 중 오류가 발생했습니다")


@router.put("/promos/{promo_id}", response_model=BrandPromoResponse)
async def update_promo(
    promo_id: int,
    promo_data: BrandPromoUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 수정"""
    try:
        promo = await service.update_promo(
            promo_id=promo_id,
            discount_rate=promo_data.discount_rate,
            discount_amount=promo_data.discount_amount,
            title=promo_data.title,
            description=promo_data.description,
            valid_from=promo_data.valid_from,
            valid_to=promo_data.valid_to,
            is_active=promo_data.is_active
        )
        
        return BrandPromoResponse(
            id=promo.id,
            discount_policy_id=promo.discount_policy_id,
            discount_rate=promo.discount_rate,
            discount_amount=promo.discount_amount,
            title=promo.title,
            description=promo.description,
            valid_from=promo.valid_from,
            valid_to=promo.valid_to,
            is_active=promo.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="브랜드 프로모션 수정 중 오류가 발생했습니다")


@router.delete("/promos/{promo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promo(
    promo_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 삭제"""
    try:
        success = await service.delete_promo(promo_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="브랜드 프로모션을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="브랜드 프로모션 삭제 중 오류가 발생했습니다")


# ===== 일괄 처리 메서드 =====

@router.post("/promos/bulk", response_model=List[BrandPromoResponse], status_code=status.HTTP_201_CREATED)
async def create_promos_bulk(
    promos_data: List[BrandPromoCreate],
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """브랜드 프로모션 일괄 생성"""
    try:
        promos = []
        for promo_data in promos_data:
            promo = await service.create_promo(
                discount_policy_id=promo_data.discount_policy_id,
                discount_rate=promo_data.discount_rate,
                discount_amount=promo_data.discount_amount,
                title=promo_data.title,
                description=promo_data.description,
                valid_from=promo_data.valid_from,
                valid_to=promo_data.valid_to,
                is_active=promo_data.is_active
            )
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
        
        return promos
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="브랜드 프로모션 일괄 생성 중 오류가 발생했습니다")
