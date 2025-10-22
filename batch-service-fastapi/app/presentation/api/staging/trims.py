"""
Staging Trims CRUD API
트림 관련 CRUD 작업을 처리하는 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import StagingTrimORM
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/staging/trims", tags=["staging-trims"])


@router.get("/")
def get_staging_trims(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 트림 목록 조회"""
    try:
        query = db.query(StagingTrimORM)
        
        if model_id:
            query = query.filter(StagingTrimORM.model_id == model_id)
        
        total_count = query.count()
        trims = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": trim.id,
                    "name": trim.name,
                    "car_type": trim.car_type,
                    "fuel_name": trim.fuel_name,
                    "cc": trim.cc,
                    "base_price": trim.base_price,
                    "model_id": trim.model_id,
                    "created_by": trim.created_by,
                    "created_by_username": trim.created_by_username,
                    "created_by_email": trim.created_by_email,
                    "created_at": trim.created_at.isoformat() if trim.created_at else None,
                    "updated_at": trim.updated_at.isoformat() if trim.updated_at else None
                }
                for trim in trims
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트림 목록 조회 실패: {str(e)}")


@router.get("/{trim_id}")
def get_staging_trim(
    trim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 트림 상세 조회"""
    try:
        trim = db.query(StagingTrimORM).filter(StagingTrimORM.id == trim_id).first()
        
        if not trim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="트림을 찾을 수 없습니다"
            )
        
        return {
            "id": trim.id,
            "name": trim.name,
            "car_type": trim.car_type,
            "fuel_name": trim.fuel_name,
            "cc": trim.cc,
            "base_price": trim.base_price,
            "model_id": trim.model_id,
            "created_by": trim.created_by,
            "created_by_username": trim.created_by_username,
            "created_by_email": trim.created_by_email,
            "created_at": trim.created_at.isoformat() if trim.created_at else None,
            "updated_at": trim.updated_at.isoformat() if trim.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트림 조회 실패: {str(e)}")


@router.post("/")
def create_staging_trim(
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 스테이징 트림 생성"""
    try:
        # 빈 문자열을 None으로 변환
        base_price = trim_data.get('base_price')
        base_price_value = int(base_price) if base_price and base_price.strip() else None
        
        new_trim = StagingTrimORM(
            name=trim_data.get('name'),
            car_type=trim_data.get('car_type'),
            fuel_name=trim_data.get('fuel_name'),
            cc=trim_data.get('cc'),
            base_price=base_price_value,
            model_id=trim_data.get('model_id'),
            created_by=getattr(current_user, 'username', 'admin'),
            created_by_username=getattr(current_user, 'username', 'admin'),
            created_by_email=getattr(current_user, 'email', 'admin@example.com')
        )
        
        db.add(new_trim)
        db.commit()
        db.refresh(new_trim)
        
        return {
            "success": True,
            "message": "트림이 성공적으로 생성되었습니다",
            "trim": {
                "id": new_trim.id,
                "name": new_trim.name,
                "car_type": new_trim.car_type,
                "fuel_name": new_trim.fuel_name,
                "cc": new_trim.cc,
                "base_price": new_trim.base_price,
                "model_id": new_trim.model_id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"트림 생성 에러: {str(e)}")
        print(f"트림 데이터: {trim_data}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"트림 생성 실패: {str(e)}")


@router.put("/{trim_id}")
def update_staging_trim(
    trim_id: int,
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 트림 수정"""
    try:
        trim = db.query(StagingTrimORM).filter(StagingTrimORM.id == trim_id).first()
        
        if not trim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="트림을 찾을 수 없습니다"
            )
        
        # 트림 정보 업데이트
        if 'name' in trim_data:
            trim.name = trim_data['name']
        if 'car_type' in trim_data:
            trim.car_type = trim_data['car_type']
        if 'fuel_name' in trim_data:
            trim.fuel_name = trim_data['fuel_name']
        if 'cc' in trim_data:
            trim.cc = trim_data['cc']
        if 'base_price' in trim_data:
            # 빈 문자열을 None으로 변환
            base_price = trim_data['base_price']
            if base_price is None or base_price == '':
                trim.base_price = None
            elif isinstance(base_price, (int, float)):
                trim.base_price = int(base_price)
            elif isinstance(base_price, str) and base_price.strip():
                trim.base_price = int(base_price)
            else:
                trim.base_price = None
        
        trim.updated_by_username = getattr(current_user, 'username', 'admin')
        trim.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        trim.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(trim)
        
        return {
            "success": True,
            "message": "트림이 성공적으로 수정되었습니다",
            "trim": {
                "id": trim.id,
                "name": trim.name,
                "car_type": trim.car_type,
                "fuel_name": trim.fuel_name,
                "cc": trim.cc,
                "base_price": trim.base_price,
                "model_id": trim.model_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 수정 실패: {str(e)}")


@router.delete("/{trim_id}")
def delete_staging_trim(
    trim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 트림 삭제"""
    try:
        trim = db.query(StagingTrimORM).filter(StagingTrimORM.id == trim_id).first()
        
        if not trim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="트림을 찾을 수 없습니다"
            )
        
        db.delete(trim)
        db.commit()
        
        return {
            "success": True,
            "message": "트림이 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 삭제 실패: {str(e)}")
