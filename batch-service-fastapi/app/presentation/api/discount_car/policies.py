"""
Main DB 할인 정책 API 라우터 - 기본 할인 정책 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...dependencies import get_db, get_current_user
from app.infrastructure.orm_models import (
    DiscountPolicyORM, BrandORM, VehicleLineORM, TrimORM,
    PolicyType
)

router = APIRouter(prefix="/api/main-db/discount", tags=["Main DB 할인 정책"])


# ===== 할인 정책 CRUD =====

@router.post("/policies/", status_code=status.HTTP_201_CREATED)
def create_discount_policy(
    brand_id: int,
    vehicle_line_id: int,
    trim_id: int,
    policy_type: PolicyType,
    title: str,
    description: Optional[str] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """할인 정책 생성"""
    try:
        # 외래키 검증
        brand = db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
        
        vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == vehicle_line_id).first()
        if not vehicle_line:
            raise HTTPException(status_code=404, detail="차량 라인을 찾을 수 없습니다")
        
        trim = db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        if not trim:
            raise HTTPException(status_code=404, detail="트림을 찾을 수 없습니다")
        
        # 할인 정책 생성
        new_policy = DiscountPolicyORM(
            brand_id=brand_id,
            vehicle_line_id=vehicle_line_id,
            trim_id=trim_id,
            policy_type=policy_type,
            title=title,
            description=description,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to,
            is_active=is_active
        )
        
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        
        return {
            "id": new_policy.id,
            "message": "할인 정책이 생성되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"할인 정책 생성 실패: {str(e)}")


@router.get("/policies/{policy_id}")
def get_discount_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """할인 정책 단일 조회"""
    try:
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        # 브랜드, 차량 라인, 트림 정보 조회
        brand = db.query(BrandORM).filter(BrandORM.id == policy.brand_id).first()
        vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == policy.vehicle_line_id).first()
        trim = db.query(TrimORM).filter(TrimORM.id == policy.trim_id).first()
        
        policy_type_str = policy.policy_type.value if hasattr(policy.policy_type, 'value') else str(policy.policy_type)
        
        return {
            "id": policy.id,
            "brand_id": policy.brand_id,
            "brand_name": brand.name if brand else None,
            "vehicle_line_id": policy.vehicle_line_id,
            "vehicle_line_name": vehicle_line.name if vehicle_line else None,
            "trim_id": policy.trim_id,
            "trim_name": trim.name if trim else None,
            "policy_type": policy_type_str,
            "title": policy.title,
            "description": policy.description,
            "valid_from": policy.valid_from.isoformat() if policy.valid_from else None,
            "valid_to": policy.valid_to.isoformat() if policy.valid_to else None,
            "is_active": policy.is_active,
            "created_at": policy.created_at.isoformat() if policy.created_at else None,
            "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 조회 실패: {str(e)}")


@router.get("/policies/")
def get_discount_policies(
    brand_id: Optional[int] = Query(None, description="브랜드 ID"),
    vehicle_line_id: Optional[int] = Query(None, description="차량 라인 ID"),
    trim_id: Optional[int] = Query(None, description="트림 ID"),
    policy_type: Optional[PolicyType] = Query(None, description="정책 유형"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    search: Optional[str] = Query(None, description="검색어 (제목, 설명)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """할인 정책 목록 조회 (페이지네이션 및 검색)"""
    try:
        from sqlalchemy import or_, desc, asc
        
        # 기본 쿼리
        query = db.query(DiscountPolicyORM)
        
        # 필터 적용
        if brand_id:
            query = query.filter(DiscountPolicyORM.brand_id == brand_id)
        if vehicle_line_id:
            query = query.filter(DiscountPolicyORM.vehicle_line_id == vehicle_line_id)
        if trim_id:
            query = query.filter(DiscountPolicyORM.trim_id == trim_id)
        if policy_type:
            query = query.filter(DiscountPolicyORM.policy_type == policy_type)
        if is_active is not None:
            query = query.filter(DiscountPolicyORM.is_active == is_active)
        
        # 검색어 적용
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    DiscountPolicyORM.title.like(search_pattern),
                    DiscountPolicyORM.description.like(search_pattern)
                )
            )
        
        # 정렬
        if hasattr(DiscountPolicyORM, sort_by):
            sort_column = getattr(DiscountPolicyORM, sort_by)
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션
        offset = (page - 1) * limit
        policies = query.offset(offset).limit(limit).all()
        
        # 데이터 변환
        policies_data = []
        for policy in policies:
            brand = db.query(BrandORM).filter(BrandORM.id == policy.brand_id).first()
            vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == policy.vehicle_line_id).first()
            trim = db.query(TrimORM).filter(TrimORM.id == policy.trim_id).first()
            
            policy_type_str = policy.policy_type.value if hasattr(policy.policy_type, 'value') else str(policy.policy_type)
            
            policies_data.append({
                "id": policy.id,
                "brand_id": policy.brand_id,
                "brand_name": brand.name if brand else None,
                "vehicle_line_id": policy.vehicle_line_id,
                "vehicle_line_name": vehicle_line.name if vehicle_line else None,
                "trim_id": policy.trim_id,
                "trim_name": trim.name if trim else None,
                "policy_type": policy_type_str,
                "title": policy.title,
                "description": policy.description,
                "valid_from": policy.valid_from.isoformat() if policy.valid_from else None,
                "valid_to": policy.valid_to.isoformat() if policy.valid_to else None,
                "is_active": policy.is_active,
                "created_at": policy.created_at.isoformat() if policy.created_at else None,
                "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
            })
        
        return {
            "items": policies_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"할인 정책 목록 조회 실패: {str(e)}")


@router.put("/policies/{policy_id}")
def update_discount_policy(
    policy_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """할인 정책 수정"""
    try:
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        # 업데이트
        if title is not None:
            policy.title = title
        if description is not None:
            policy.description = description
        if valid_from is not None:
            policy.valid_from = valid_from
        if valid_to is not None:
            policy.valid_to = valid_to
        if is_active is not None:
            policy.is_active = is_active
        
        policy.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(policy)
        
        return {
            "id": policy.id,
            "message": "할인 정책이 수정되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"할인 정책 수정 실패: {str(e)}")


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discount_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """할인 정책 삭제"""
    try:
        policy = db.query(DiscountPolicyORM).filter(DiscountPolicyORM.id == policy_id).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="할인 정책을 찾을 수 없습니다")
        
        db.delete(policy)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"할인 정책 삭제 실패: {str(e)}")

