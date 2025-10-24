"""
Main DB 브랜드 프로모션 API 라우터 - 브랜드 프로모션 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from ...dependencies import get_db, get_current_user
from app.infrastructure.orm_models import (
    BrandPromoORM, DiscountPolicyORM
)

router = APIRouter(prefix="/api/main-db/discount", tags=["Main DB 브랜드 프로모션"])


# ===== 브랜드 프로모션 CRUD =====

@router.post("/promos/", status_code=status.HTTP_201_CREATED)
def create_promo(
    policy_id: int,
    promo_name: str,
    discount_type: str,
    discount_value: float,
    promo_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 프로모션 생성"""
    try:
        # 정책 존재 확인
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        # 브랜드 프로모션 생성
        new_promo = BrandPromoORM(
            policy_id=policy_id,
            promo_name=promo_name,
            discount_type=discount_type,
            discount_value=discount_value,
            promo_code=promo_code
        )
        
        db.add(new_promo)
        db.commit()
        db.refresh(new_promo)
        
        return {
            "id": new_promo.id,
            "message": "브랜드 프로모션이 생성되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 프로모션 생성 실패: {str(e)}")


@router.get("/promos/{promo_id}")
def get_promo(
    promo_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 프로모션 단일 조회"""
    try:
        promo = db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        
        if not promo:
            raise HTTPException(status_code=404, detail="브랜드 프로모션을 찾을 수 없습니다")
        
        return {
            "id": promo.id,
            "policy_id": promo.policy_id,
            "promo_name": promo.promo_name,
            "discount_type": promo.discount_type,
            "discount_value": promo.discount_value,
            "promo_code": promo.promo_code
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 프로모션 조회 실패: {str(e)}")


@router.get("/promos/")
def get_promos(
    policy_id: Optional[int] = Query(None, description="정책 ID"),
    promo_name: Optional[str] = Query(None, description="프로모션명"),
    search: Optional[str] = Query(None, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("id", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 프로모션 목록 조회 (페이지네이션 및 검색)"""
    try:
        from sqlalchemy import or_, desc, asc
        
        # 기본 쿼리
        query = db.query(BrandPromoORM)
        
        # 필터 적용
        if policy_id:
            query = query.filter(BrandPromoORM.policy_id == policy_id)
        if promo_name:
            query = query.filter(BrandPromoORM.promo_name.like(f"%{promo_name}%"))
        
        # 검색어 적용
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    BrandPromoORM.promo_name.like(search_pattern),
                    BrandPromoORM.promo_code.like(search_pattern)
                )
            )
        
        # 정렬
        if hasattr(BrandPromoORM, sort_by):
            sort_column = getattr(BrandPromoORM, sort_by)
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * limit
        promos = query.offset(offset).limit(limit).all()
        
        # 데이터 변환
        promos_data = []
        for promo in promos:
            promos_data.append({
                "id": promo.id,
                "policy_id": promo.policy_id,
                "promo_name": promo.promo_name,
                "discount_type": promo.discount_type,
                "discount_value": promo.discount_value,
                "promo_code": promo.promo_code
            })
        
        return {
            "items": promos_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 프로모션 목록 조회 실패: {str(e)}")


@router.put("/promos/{promo_id}")
def update_promo(
    promo_id: int,
    promo_name: Optional[str] = None,
    discount_type: Optional[str] = None,
    discount_value: Optional[float] = None,
    promo_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 프로모션 수정"""
    try:
        promo = db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        
        if not promo:
            raise HTTPException(status_code=404, detail="브랜드 프로모션을 찾을 수 없습니다")
        
        # 업데이트
        if promo_name is not None:
            promo.promo_name = promo_name
        if discount_type is not None:
            promo.discount_type = discount_type
        if discount_value is not None:
            promo.discount_value = discount_value
        if promo_code is not None:
            promo.promo_code = promo_code
        
        db.commit()
        db.refresh(promo)
        
        return {
            "id": promo.id,
            "message": "브랜드 프로모션이 수정되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 프로모션 수정 실패: {str(e)}")


@router.delete("/promos/{promo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promo(
    promo_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 프로모션 삭제"""
    try:
        promo = db.query(BrandPromoORM).filter(BrandPromoORM.id == promo_id).first()
        
        if not promo:
            raise HTTPException(status_code=404, detail="브랜드 프로모션을 찾을 수 없습니다")
        
        db.delete(promo)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 프로모션 삭제 실패: {str(e)}")

