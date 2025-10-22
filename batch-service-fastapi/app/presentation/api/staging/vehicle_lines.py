"""
Staging Vehicle Lines CRUD API
자동차 라인 관련 CRUD 작업을 처리하는 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import StagingVehicleLineORM
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/staging/vehicle-lines", tags=["staging-vehicle-lines"])


@router.get("/")
def get_staging_vehicle_lines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    brand_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 자동차 라인 목록 조회"""
    try:
        query = db.query(StagingVehicleLineORM)
        
        if brand_id:
            query = query.filter(StagingVehicleLineORM.brand_id == brand_id)
        
        total_count = query.count()
        vehicle_lines = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": vehicle_line.id,
                    "name": vehicle_line.name,
                    "description": vehicle_line.description,
                    "brand_id": vehicle_line.brand_id,
                    "created_by": vehicle_line.created_by,
                    "created_by_username": vehicle_line.created_by_username,
                    "created_by_email": vehicle_line.created_by_email,
                    "created_at": vehicle_line.created_at.isoformat() if vehicle_line.created_at else None,
                    "updated_at": vehicle_line.updated_at.isoformat() if vehicle_line.updated_at else None
                }
                for vehicle_line in vehicle_lines
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동차 라인 목록 조회 실패: {str(e)}")


@router.get("/{vehicle_line_id}")
def get_staging_vehicle_line(
    vehicle_line_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 자동차 라인 상세 조회"""
    try:
        vehicle_line = db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.id == vehicle_line_id
        ).first()
        
        if not vehicle_line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="자동차 라인을 찾을 수 없습니다"
            )
        
        return {
            "id": vehicle_line.id,
            "name": vehicle_line.name,
            "description": vehicle_line.description,
            "brand_id": vehicle_line.brand_id,
            "created_by": vehicle_line.created_by,
            "created_by_username": vehicle_line.created_by_username,
            "created_by_email": vehicle_line.created_by_email,
            "created_at": vehicle_line.created_at.isoformat() if vehicle_line.created_at else None,
            "updated_at": vehicle_line.updated_at.isoformat() if vehicle_line.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동차 라인 조회 실패: {str(e)}")


@router.post("/")
def create_staging_vehicle_line(
    vehicle_line_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 스테이징 자동차 라인 생성"""
    try:
        new_vehicle_line = StagingVehicleLineORM(
            name=vehicle_line_data.get('name'),
            description=vehicle_line_data.get('description'),
            brand_id=vehicle_line_data.get('brand_id'),
            created_by=getattr(current_user, 'username', 'admin'),
            created_by_username=getattr(current_user, 'username', 'admin'),
            created_by_email=getattr(current_user, 'email', 'admin@example.com')
        )
        
        db.add(new_vehicle_line)
        db.commit()
        db.refresh(new_vehicle_line)
        
        return {
            "success": True,
            "message": "자동차 라인이 성공적으로 생성되었습니다",
            "vehicle_line": {
                "id": new_vehicle_line.id,
                "name": new_vehicle_line.name,
                "description": new_vehicle_line.description,
                "brand_id": new_vehicle_line.brand_id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"자동차 라인 생성 에러: {str(e)}")
        print(f"자동차 라인 데이터: {vehicle_line_data}")
        raise HTTPException(status_code=500, detail=f"자동차 라인 생성 실패: {str(e)}")


@router.put("/{vehicle_line_id}")
def update_staging_vehicle_line(
    vehicle_line_id: int,
    vehicle_line_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 자동차 라인 수정"""
    try:
        vehicle_line = db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.id == vehicle_line_id
        ).first()
        
        if not vehicle_line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="자동차 라인을 찾을 수 없습니다"
            )
        
        # 필드 업데이트
        if 'name' in vehicle_line_data:
            vehicle_line.name = vehicle_line_data['name']
        if 'description' in vehicle_line_data:
            vehicle_line.description = vehicle_line_data['description']
        
        vehicle_line.updated_by_username = getattr(current_user, 'username', 'admin')
        vehicle_line.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        vehicle_line.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle_line)
        
        return {
            "success": True,
            "message": "자동차 라인이 성공적으로 수정되었습니다",
            "vehicle_line": {
                "id": vehicle_line.id,
                "name": vehicle_line.name,
                "description": vehicle_line.description,
                "brand_id": vehicle_line.brand_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"자동차 라인 수정 에러: {str(e)}")
        print(f"자동차 라인 데이터: {vehicle_line_data}")
        print(f"자동차 라인 ID: {vehicle_line_id}")
        raise HTTPException(status_code=500, detail=f"자동차 라인 수정 실패: {str(e)}")


@router.delete("/{vehicle_line_id}")
def delete_staging_vehicle_line(
    vehicle_line_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 자동차 라인 삭제"""
    try:
        vehicle_line = db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.id == vehicle_line_id
        ).first()
        
        if not vehicle_line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="자동차 라인을 찾을 수 없습니다"
            )
        
        db.delete(vehicle_line)
        db.commit()
        
        return {
            "success": True,
            "message": "자동차 라인이 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"자동차 라인 삭제 실패: {str(e)}")