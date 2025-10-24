"""
Main DB 재고 할인 API 라우터 - 재고 할인 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from ...dependencies import get_db, get_current_user
from app.infrastructure.orm_models import (
    BrandInventoryDiscountORM, DiscountPolicyORM
)

router = APIRouter(prefix="/api/main-db/discount", tags=["Main DB 재고 할인"])


# ===== 재고 할인 CRUD =====

@router.post("/inventory-discounts/", status_code=status.HTTP_201_CREATED)
def create_inventory_discount(
    policy_id: int,
    discount_type: str,
    discount_value: float,
    min_stock: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """재고 할인 생성"""
    try:
        # 정책 존재 확인
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        # 재고 할인 생성
        new_discount = BrandInventoryDiscountORM(
            policy_id=policy_id,
            discount_type=discount_type,
            discount_value=discount_value,
            min_stock=min_stock
        )
        
        db.add(new_discount)
        db.commit()
        db.refresh(new_discount)
        
        return {
            "id": new_discount.id,
            "message": "재고 할인이 생성되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"재고 할인 생성 실패: {str(e)}")


@router.get("/inventory-discounts/{discount_id}")
def get_inventory_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """재고 할인 단일 조회"""
    try:
        discount = db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        
        if not discount:
            raise HTTPException(status_code=404, detail="재고 할인을 찾을 수 없습니다")
        
        return {
            "id": discount.id,
            "policy_id": discount.policy_id,
            "discount_type": discount.discount_type,
            "discount_value": discount.discount_value,
            "min_stock": discount.min_stock
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재고 할인 조회 실패: {str(e)}")


@router.get("/inventory-discounts/")
def get_inventory_discounts(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    discount_type: Optional[str] = Query(None, description="할인 유형"),
    search: Optional[str] = Query(None, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("id", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """재고 할인 목록 조회 (페이지네이션 및 검색)"""
    try:
        from sqlalchemy import or_, desc, asc
        
        # 기본 쿼리
        query = db.query(BrandInventoryDiscountORM)
        
        # 필터 적용
        if policy_id:
            query = query.filter(BrandInventoryDiscountORM.policy_id == policy_id)
        if discount_type:
            query = query.filter(BrandInventoryDiscountORM.discount_type == discount_type)
        
        # 검색어 적용
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                BrandInventoryDiscountORM.discount_type.like(search_pattern)
            )
        
        # 정렬
        if hasattr(BrandInventoryDiscountORM, sort_by):
            sort_column = getattr(BrandInventoryDiscountORM, sort_by)
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * limit
        discounts = query.offset(offset).limit(limit).all()
        
        # 데이터 변환
        discounts_data = []
        for discount in discounts:
            discounts_data.append({
                "id": discount.id,
                "policy_id": discount.policy_id,
                "discount_type": discount.discount_type,
                "discount_value": discount.discount_value,
                "min_stock": discount.min_stock
            })
        
        return {
            "items": discounts_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재고 할인 목록 조회 실패: {str(e)}")


@router.put("/inventory-discounts/{discount_id}")
def update_inventory_discount(
    discount_id: int,
    discount_type: Optional[str] = None,
    discount_value: Optional[float] = None,
    min_stock: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """재고 할인 수정"""
    try:
        discount = db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        
        if not discount:
            raise HTTPException(status_code=404, detail="재고 할인을 찾을 수 없습니다")
        
        # 업데이트
        if discount_type is not None:
            discount.discount_type = discount_type
        if discount_value is not None:
            discount.discount_value = discount_value
        if min_stock is not None:
            discount.min_stock = min_stock
        
        db.commit()
        db.refresh(discount)
        
        return {
            "id": discount.id,
            "message": "재고 할인이 수정되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"재고 할인 수정 실패: {str(e)}")


@router.delete("/inventory-discounts/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """재고 할인 삭제"""
    try:
        discount = db.query(BrandInventoryDiscountORM).filter(BrandInventoryDiscountORM.id == discount_id).first()
        
        if not discount:
            raise HTTPException(status_code=404, detail="재고 할인을 찾을 수 없습니다")
        
        db.delete(discount)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"재고 할인 삭제 실패: {str(e)}")

