"""
Staging Models CRUD API
모델 관련 CRUD 작업을 처리하는 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import StagingModelORM
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/staging/models", tags=["staging-models"])


@router.get("/")
def get_staging_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_line_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 모델 목록 조회"""
    try:
        query = db.query(StagingModelORM)
        
        if vehicle_line_id:
            query = query.filter(StagingModelORM.vehicle_line_id == vehicle_line_id)
        
        total_count = query.count()
        models = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": model.id,
                    "name": model.name,
                    "code": model.code,
                    "price": model.price,
                    "foreign": model.foreign,
                    "vehicle_line_id": model.vehicle_line_id,
                    "brand_id": model.brand_id,
                    "created_by": model.created_by,
                    "created_by_username": model.created_by_username,
                    "created_by_email": model.created_by_email,
                    "created_at": model.created_at.isoformat() if model.created_at else None,
                    "updated_at": model.updated_at.isoformat() if model.updated_at else None
                }
                for model in models
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 목록 조회 실패: {str(e)}")


@router.get("/{model_id}")
def get_staging_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 모델 상세 조회"""
    try:
        model = db.query(StagingModelORM).filter(StagingModelORM.id == model_id).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="모델을 찾을 수 없습니다"
            )
        
        return {
            "id": model.id,
            "name": model.name,
            "code": model.code,
            "price": model.price,
            "foreign": model.foreign,
            "vehicle_line_id": model.vehicle_line_id,
            "brand_id": model.brand_id,
            "created_by": model.created_by,
            "created_by_username": model.created_by_username,
            "created_by_email": model.created_by_email,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 조회 실패: {str(e)}")


@router.post("/")
def create_staging_model(
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 스테이징 모델 생성"""
    try:
        # 빈 문자열을 None으로 변환
        price = model_data.get('price')
        price_value = int(price) if price and price.strip() else None
        
        new_model = StagingModelORM(
            name=model_data.get('name'),
            code=model_data.get('code'),
            price=price_value,
            foreign=model_data.get('foreign', False),
            vehicle_line_id=model_data.get('vehicle_line_id'),
            brand_id=model_data.get('brand_id'),
            created_by=getattr(current_user, 'username', 'admin'),
            created_by_username=getattr(current_user, 'username', 'admin'),
            created_by_email=getattr(current_user, 'email', 'admin@example.com')
        )
        
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        
        return {
            "success": True,
            "message": "모델이 성공적으로 생성되었습니다",
            "model": {
                "id": new_model.id,
                "name": new_model.name,
                "code": new_model.code,
                "price": new_model.price,
                "foreign": new_model.foreign,
                "vehicle_line_id": new_model.vehicle_line_id,
                "brand_id": new_model.brand_id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"모델 생성 에러: {str(e)}")
        print(f"모델 데이터: {model_data}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"모델 생성 실패: {str(e)}")


@router.put("/{model_id}")
def update_staging_model(
    model_id: int,
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 모델 수정"""
    try:
        model = db.query(StagingModelORM).filter(StagingModelORM.id == model_id).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="모델을 찾을 수 없습니다"
            )
        
        # 모델 정보 업데이트
        if 'name' in model_data:
            model.name = model_data['name']
        if 'code' in model_data:
            model.code = model_data['code']
        if 'price' in model_data:
            # 빈 문자열을 None으로 변환
            price = model_data['price']
            if price is None or price == '':
                model.price = None
            elif isinstance(price, (int, float)):
                model.price = int(price)
            elif isinstance(price, str) and price.strip():
                model.price = int(price)
            else:
                model.price = None
        if 'foreign' in model_data:
            model.foreign = model_data['foreign']
        
        model.updated_by_username = getattr(current_user, 'username', 'admin')
        model.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        model.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(model)
        
        return {
            "success": True,
            "message": "모델이 성공적으로 수정되었습니다",
            "model": {
                "id": model.id,
                "name": model.name,
                "code": model.code,
                "price": model.price,
                "foreign": model.foreign,
                "vehicle_line_id": model.vehicle_line_id,
                "brand_id": model.brand_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"모델 수정 에러: {str(e)}")
        print(f"모델 데이터: {model_data}")
        print(f"모델 ID: {model_id}")
        raise HTTPException(status_code=500, detail=f"모델 수정 실패: {str(e)}")


@router.delete("/{model_id}")
def delete_staging_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 모델 삭제"""
    try:
        model = db.query(StagingModelORM).filter(StagingModelORM.id == model_id).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="모델을 찾을 수 없습니다"
            )
        
        db.delete(model)
        db.commit()
        
        return {
            "success": True,
            "message": "모델이 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"모델 삭제 실패: {str(e)}")
