"""
Staging Brands CRUD API
브랜드 관련 CRUD 작업을 처리하는 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import StagingBrandORM
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/staging/brands", tags=["staging-brands"])


@router.get("/")
def get_staging_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    version_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 브랜드 목록 조회"""
    try:
        query = db.query(StagingBrandORM)
        
        if version_id:
            query = query.filter(StagingBrandORM.version_id == version_id)
        
        total_count = query.count()
        brands = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": brand.id,
                    "name": brand.name,
                    "country": brand.country,
                    "logo_url": brand.logo_url,
                    "manager": brand.manager,
                    "version_id": brand.version_id,
                    "created_by": brand.created_by,
                    "created_by_username": brand.created_by_username,
                    "created_by_email": brand.created_by_email,
                    "created_at": brand.created_at.isoformat() if brand.created_at else None,
                    "updated_at": brand.updated_at.isoformat() if brand.updated_at else None
                }
                for brand in brands
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 목록 조회 실패: {str(e)}")


@router.get("/{brand_id}")
def get_staging_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 브랜드 상세 조회"""
    try:
        brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == brand_id).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        return {
            "id": brand.id,
            "name": brand.name,
            "country": brand.country,
            "logo_url": brand.logo_url,
            "manager": brand.manager,
            "version_id": brand.version_id,
            "created_by": brand.created_by,
            "created_by_username": brand.created_by_username,
            "created_by_email": brand.created_by_email,
            "created_at": brand.created_at.isoformat() if brand.created_at else None,
            "updated_at": brand.updated_at.isoformat() if brand.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 조회 실패: {str(e)}")


@router.post("/")
def create_staging_brand(
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 스테이징 브랜드 생성"""
    try:
        new_brand = StagingBrandORM(
            name=brand_data.get('name'),
            country=brand_data.get('country'),
            logo_url=brand_data.get('logo_url'),
            manager=brand_data.get('manager'),
            version_id=brand_data.get('version_id'),
            created_by=getattr(current_user, 'username', 'admin'),
            created_by_username=getattr(current_user, 'username', 'admin'),
            created_by_email=getattr(current_user, 'email', 'admin@example.com')
        )
        
        db.add(new_brand)
        db.commit()
        db.refresh(new_brand)
        
        return {
            "success": True,
            "message": "브랜드가 성공적으로 생성되었습니다",
            "brand": {
                "id": new_brand.id,
                "name": new_brand.name,
                "country": new_brand.country,
                "logo_url": new_brand.logo_url,
                "manager": new_brand.manager,
                "version_id": new_brand.version_id
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 생성 실패: {str(e)}")


@router.put("/{brand_id}")
def update_staging_brand(
    brand_id: int,
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 브랜드 수정"""
    try:
        brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == brand_id).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 브랜드 정보 업데이트
        if 'name' in brand_data:
            brand.name = brand_data['name']
        if 'country' in brand_data:
            brand.country = brand_data['country']
        if 'logo_url' in brand_data:
            brand.logo_url = brand_data['logo_url']
        if 'manager' in brand_data:
            brand.manager = brand_data['manager']
        
        brand.updated_by_username = getattr(current_user, 'username', 'admin')
        brand.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        brand.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(brand)
        
        return {
            "success": True,
            "message": "브랜드가 성공적으로 수정되었습니다",
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "logo_url": brand.logo_url,
                "manager": brand.manager,
                "version_id": brand.version_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"브랜드 수정 에러: {str(e)}")
        print(f"브랜드 데이터: {brand_data}")
        print(f"브랜드 ID: {brand_id}")
        raise HTTPException(status_code=500, detail=f"브랜드 수정 실패: {str(e)}")


@router.delete("/{brand_id}")
def delete_staging_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 브랜드 삭제"""
    try:
        brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == brand_id).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        db.delete(brand)
        db.commit()
        
        return {
            "success": True,
            "message": "브랜드가 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 삭제 실패: {str(e)}")
