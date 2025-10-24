"""
Main DB 카드사 제휴 API 라우터 - 카드사 제휴 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...dependencies import get_db, get_current_user
from app.infrastructure.orm_models import (
    BrandCardBenefitORM, DiscountPolicyORM
)

router = APIRouter(prefix="/api/main-db/discount", tags=["Main DB 카드사 제휴"])


# ===== 카드사 제휴 CRUD =====

@router.post("/card-benefits/", status_code=status.HTTP_201_CREATED)
def create_card_benefit(
    policy_id: int,
    card_name: str,
    discount_type: str,
    discount_value: float,
    min_amount: Optional[int] = None,
    max_discount: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """카드사 제휴 생성"""
    try:
        # 정책 존재 확인
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        # 카드사 제휴 생성
        new_benefit = BrandCardBenefitORM(
            policy_id=policy_id,
            card_name=card_name,
            discount_type=discount_type,
            discount_value=discount_value,
            min_amount=min_amount,
            max_discount=max_discount
        )
        
        db.add(new_benefit)
        db.commit()
        db.refresh(new_benefit)
        
        return {
            "id": new_benefit.id,
            "message": "카드사 제휴가 생성되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"카드사 제휴 생성 실패: {str(e)}")


@router.get("/card-benefits/{benefit_id}")
def get_card_benefit(
    benefit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """카드사 제휴 단일 조회"""
    try:
        benefit = db.query(BrandCardBenefitORM).filter(BrandCardBenefitORM.id == benefit_id).first()
        
        if not benefit:
            raise HTTPException(status_code=404, detail="카드사 제휴를 찾을 수 없습니다")
        
        return {
            "id": benefit.id,
            "policy_id": benefit.policy_id,
            "card_name": benefit.card_name,
            "discount_type": benefit.discount_type,
            "discount_value": benefit.discount_value,
            "min_amount": benefit.min_amount,
            "max_discount": benefit.max_discount
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카드사 제휴 조회 실패: {str(e)}")


@router.get("/card-benefits/")
def get_card_benefits(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    card_name: Optional[str] = Query(None, description="카드사명"),
    discount_type: Optional[str] = Query(None, description="할인 유형"),
    search: Optional[str] = Query(None, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("id", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """카드사 제휴 목록 조회 (페이지네이션 및 검색)"""
    try:
        from sqlalchemy import or_, desc, asc
        
        # 기본 쿼리
        query = db.query(BrandCardBenefitORM)
        
        # 필터 적용
        if policy_id:
            query = query.filter(BrandCardBenefitORM.policy_id == policy_id)
        if card_name:
            query = query.filter(BrandCardBenefitORM.card_name.like(f"%{card_name}%"))
        if discount_type:
            query = query.filter(BrandCardBenefitORM.discount_type == discount_type)
        
        # 검색어 적용
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    BrandCardBenefitORM.card_name.like(search_pattern),
                    BrandCardBenefitORM.discount_type.like(search_pattern)
                )
            )
        
        # 정렬
        if hasattr(BrandCardBenefitORM, sort_by):
            sort_column = getattr(BrandCardBenefitORM, sort_by)
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * limit
        benefits = query.offset(offset).limit(limit).all()
        
        # 데이터 변환
        benefits_data = []
        for benefit in benefits:
            benefits_data.append({
                "id": benefit.id,
                "policy_id": benefit.policy_id,
                "card_name": benefit.card_name,
                "discount_type": benefit.discount_type,
                "discount_value": benefit.discount_value,
                "min_amount": benefit.min_amount,
                "max_discount": benefit.max_discount
            })
        
        return {
            "items": benefits_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카드사 제휴 목록 조회 실패: {str(e)}")


@router.put("/card-benefits/{benefit_id}")
def update_card_benefit(
    benefit_id: int,
    card_name: Optional[str] = None,
    discount_type: Optional[str] = None,
    discount_value: Optional[float] = None,
    min_amount: Optional[int] = None,
    max_discount: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """카드사 제휴 수정"""
    try:
        benefit = db.query(BrandCardBenefitORM).filter(BrandCardBenefitORM.id == benefit_id).first()
        
        if not benefit:
            raise HTTPException(status_code=404, detail="카드사 제휴를 찾을 수 없습니다")
        
        # 업데이트
        if card_name is not None:
            benefit.card_name = card_name
        if discount_type is not None:
            benefit.discount_type = discount_type
        if discount_value is not None:
            benefit.discount_value = discount_value
        if min_amount is not None:
            benefit.min_amount = min_amount
        if max_discount is not None:
            benefit.max_discount = max_discount
        
        db.commit()
        db.refresh(benefit)
        
        return {
            "id": benefit.id,
            "message": "카드사 제휴가 수정되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"카드사 제휴 수정 실패: {str(e)}")


@router.delete("/card-benefits/{benefit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card_benefit(
    benefit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """카드사 제휴 삭제"""
    try:
        benefit = db.query(BrandCardBenefitORM).filter(BrandCardBenefitORM.id == benefit_id).first()
        
        if not benefit:
            raise HTTPException(status_code=404, detail="카드사 제휴를 찾을 수 없습니다")
        
        db.delete(benefit)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"카드사 제휴 삭제 실패: {str(e)}")

