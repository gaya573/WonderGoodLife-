"""
재고 할인 API 라우터 - 재고 할인 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

from ....application.discount_service import DiscountPolicyService
from ....presentation.dependencies import get_discount_policy_service, get_current_active_user
from ....presentation.schemas import (
    BrandInventoryDiscountCreate,
    BrandInventoryDiscountUpdate,
    BrandInventoryDiscountResponse,
    BrandInventoryDiscountListResponse,
    InventoryDiscountFilterParams
)
from ....domain.entities import User

router = APIRouter(prefix="/api/discount", tags=["재고 할인"])


# ===== 재고 할인 CRUD =====

@router.post("/inventory-discounts/", response_model=BrandInventoryDiscountResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_discount(
    discount_data: BrandInventoryDiscountCreate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 생성"""
    try:
        discount = await service.create_inventory_discount(
            discount_policy_id=discount_data.discount_policy_id,
            inventory_level_threshold=discount_data.inventory_level_threshold,
            discount_rate=discount_data.discount_rate,
            title=discount_data.title,
            description=discount_data.description,
            valid_from=discount_data.valid_from,
            valid_to=discount_data.valid_to,
            is_active=discount_data.is_active
        )
        
        return BrandInventoryDiscountResponse(
            id=discount.id,
            discount_policy_id=discount.discount_policy_id,
            inventory_level_threshold=discount.inventory_level_threshold,
            discount_rate=discount.discount_rate,
            title=discount.title,
            description=discount.description,
            valid_from=discount.valid_from,
            valid_to=discount.valid_to,
            is_active=discount.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="재고 할인 생성 중 오류가 발생했습니다")


@router.get("/inventory-discounts/{discount_id}", response_model=BrandInventoryDiscountResponse)
async def get_inventory_discount(
    discount_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 단일 조회"""
    discount = await service.get_inventory_discount(discount_id)
    if not discount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="재고 할인을 찾을 수 없습니다")
    
    return BrandInventoryDiscountResponse(
        id=discount.id,
        discount_policy_id=discount.discount_policy_id,
        inventory_level_threshold=discount.inventory_level_threshold,
        discount_rate=discount.discount_rate,
        title=discount.title,
        description=discount.description,
        valid_from=discount.valid_from,
        valid_to=discount.valid_to,
        is_active=discount.is_active
    )


@router.get("/inventory-discounts/", response_model=BrandInventoryDiscountListResponse)
async def get_inventory_discounts(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 목록 조회 (페이지네이션)"""
    try:
        result = await service.get_inventory_discounts(
            policy_id=policy_id,
            is_active=is_active,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # 응답 데이터 변환
        discounts = []
        for discount in result["items"]:
            discounts.append(BrandInventoryDiscountResponse(
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
        
        return BrandInventoryDiscountListResponse(
            items=discounts,
            pagination=result["pagination"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="재고 할인 목록 조회 중 오류가 발생했습니다")


@router.put("/inventory-discounts/{discount_id}", response_model=BrandInventoryDiscountResponse)
async def update_inventory_discount(
    discount_id: int,
    discount_data: BrandInventoryDiscountUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 수정"""
    try:
        discount = await service.update_inventory_discount(
            discount_id=discount_id,
            inventory_level_threshold=discount_data.inventory_level_threshold,
            discount_rate=discount_data.discount_rate,
            title=discount_data.title,
            description=discount_data.description,
            valid_from=discount_data.valid_from,
            valid_to=discount_data.valid_to,
            is_active=discount_data.is_active
        )
        
        return BrandInventoryDiscountResponse(
            id=discount.id,
            discount_policy_id=discount.discount_policy_id,
            inventory_level_threshold=discount.inventory_level_threshold,
            discount_rate=discount.discount_rate,
            title=discount.title,
            description=discount.description,
            valid_from=discount.valid_from,
            valid_to=discount.valid_to,
            is_active=discount.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="재고 할인 수정 중 오류가 발생했습니다")


@router.delete("/inventory-discounts/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_discount(
    discount_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 삭제"""
    try:
        success = await service.delete_inventory_discount(discount_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="재고 할인을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="재고 할인 삭제 중 오류가 발생했습니다")


# ===== 일괄 처리 메서드 =====

@router.post("/inventory-discounts/bulk", response_model=List[BrandInventoryDiscountResponse], status_code=status.HTTP_201_CREATED)
async def create_inventory_discounts_bulk(
    discounts_data: List[BrandInventoryDiscountCreate],
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """재고 할인 일괄 생성"""
    try:
        discounts = []
        for discount_data in discounts_data:
            discount = await service.create_inventory_discount(
                discount_policy_id=discount_data.discount_policy_id,
                inventory_level_threshold=discount_data.inventory_level_threshold,
                discount_rate=discount_data.discount_rate,
                title=discount_data.title,
                description=discount_data.description,
                valid_from=discount_data.valid_from,
                valid_to=discount_data.valid_to,
                is_active=discount_data.is_active
            )
            discounts.append(BrandInventoryDiscountResponse(
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
        
        return discounts
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="재고 할인 일괄 생성 중 오류가 발생했습니다")
