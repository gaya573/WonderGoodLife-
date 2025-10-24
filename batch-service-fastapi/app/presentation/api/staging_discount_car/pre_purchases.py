"""
선구매 할인 API 라우터 - 선구매 할인 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from ....application.discount_service import DiscountPolicyService
from ....presentation.dependencies import get_discount_policy_service, get_current_active_user
from ....presentation.schemas import (
    BrandPrePurchaseCreate,
    BrandPrePurchaseUpdate,
    BrandPrePurchaseResponse,
    BrandPrePurchaseListResponse,
    PrePurchaseFilterParams
)
from ....domain.entities import User, EventTypeForPrePurchase

router = APIRouter(prefix="/api/discount", tags=["선구매 할인"])


# ===== 선구매 할인 CRUD =====

@router.post("/pre-purchases/", response_model=BrandPrePurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_pre_purchase(
    pre_purchase_data: BrandPrePurchaseCreate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 생성"""
    try:
        pre_purchase = await service.create_pre_purchase(
            discount_policy_id=pre_purchase_data.discount_policy_id,
            event_type=pre_purchase_data.event_type.value,  # Enum을 문자열로 변환
            discount_rate=pre_purchase_data.discount_rate,
            discount_amount=pre_purchase_data.discount_amount,
            title=pre_purchase_data.title,
            description=pre_purchase_data.description,
            pre_purchase_start=pre_purchase_data.pre_purchase_start,
            valid_from=pre_purchase_data.valid_from,
            valid_to=pre_purchase_data.valid_to,
            is_active=pre_purchase_data.is_active
        )
        
        return BrandPrePurchaseResponse(
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
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="선구매 할인 생성 중 오류가 발생했습니다")


@router.get("/pre-purchases/{pre_purchase_id}", response_model=BrandPrePurchaseResponse)
async def get_pre_purchase(
    pre_purchase_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 단일 조회"""
    pre_purchase = await service.get_pre_purchase(pre_purchase_id)
    if not pre_purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="선구매 할인을 찾을 수 없습니다")
    
    return BrandPrePurchaseResponse(
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
    )


@router.get("/pre-purchases/", response_model=BrandPrePurchaseListResponse)
async def get_pre_purchases(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    event_type: Optional[EventTypeForPrePurchase] = Query(None, description="이벤트 유형"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 목록 조회 (페이지네이션)"""
    try:
        result = await service.get_pre_purchases(
            policy_id=policy_id,
            event_type=event_type.value if event_type else None,
            is_active=is_active,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # 응답 데이터 변환
        pre_purchases = []
        for pre_purchase in result["items"]:
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
        
        return BrandPrePurchaseListResponse(
            items=pre_purchases,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="선구매 할인 목록 조회 중 오류가 발생했습니다")


@router.put("/pre-purchases/{pre_purchase_id}", response_model=BrandPrePurchaseResponse)
async def update_pre_purchase(
    pre_purchase_id: int,
    pre_purchase_data: BrandPrePurchaseUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 수정"""
    try:
        pre_purchase = await service.update_pre_purchase(
            pre_purchase_id=pre_purchase_id,
            event_type=pre_purchase_data.event_type.value if pre_purchase_data.event_type else None,
            discount_rate=pre_purchase_data.discount_rate,
            discount_amount=pre_purchase_data.discount_amount,
            title=pre_purchase_data.title,
            description=pre_purchase_data.description,
            pre_purchase_start=pre_purchase_data.pre_purchase_start,
            valid_from=pre_purchase_data.valid_from,
            valid_to=pre_purchase_data.valid_to,
            is_active=pre_purchase_data.is_active
        )
        
        return BrandPrePurchaseResponse(
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
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="선구매 할인 수정 중 오류가 발생했습니다")


@router.delete("/pre-purchases/{pre_purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pre_purchase(
    pre_purchase_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 삭제"""
    try:
        success = await service.delete_pre_purchase(pre_purchase_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="선구매 할인을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="선구매 할인 삭제 중 오류가 발생했습니다")


# ===== 일괄 처리 메서드 =====

@router.post("/pre-purchases/bulk", response_model=List[BrandPrePurchaseResponse], status_code=status.HTTP_201_CREATED)
async def create_pre_purchases_bulk(
    pre_purchases_data: List[BrandPrePurchaseCreate],
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """선구매 할인 일괄 생성"""
    try:
        pre_purchases = []
        for pre_purchase_data in pre_purchases_data:
            pre_purchase = await service.create_pre_purchase(
                discount_policy_id=pre_purchase_data.discount_policy_id,
                event_type=pre_purchase_data.event_type.value,  # Enum을 문자열로 변환
                discount_rate=pre_purchase_data.discount_rate,
                discount_amount=pre_purchase_data.discount_amount,
                title=pre_purchase_data.title,
                description=pre_purchase_data.description,
                pre_purchase_start=pre_purchase_data.pre_purchase_start,
                valid_from=pre_purchase_data.valid_from,
                valid_to=pre_purchase_data.valid_to,
                is_active=pre_purchase_data.is_active
            )
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
        
        return pre_purchases
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="선구매 할인 일괄 생성 중 오류가 발생했습니다")
