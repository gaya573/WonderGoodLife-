"""
Staging Data Management API - 승인 및 버전 관리
버전 단위 승인 시스템에 맞게 수정
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.repositories import (
    SQLAlchemyStagingBrandRepository,
    SQLAlchemyStagingVehicleLineRepository,
    SQLAlchemyStagingModelRepository,
    SQLAlchemyStagingTrimRepository,
    SQLAlchemyStagingOptionRepository
)
from app.domain.entities import User, ApprovalStatus
from ...schemas import (
    StagingBrandResponse, StagingBrandUpdate, StagingBrandCreate,
    StagingVehicleLineResponse, StagingVehicleLineUpdate, StagingVehicleLineCreate,
    StagingModelResponse, StagingModelUpdate, StagingModelCreate,
    StagingTrimResponse, StagingTrimUpdate, StagingTrimCreate,
    StagingOptionResponse, StagingOptionUpdate, StagingOptionCreate
)
from ...dependencies import get_current_user

router = APIRouter(prefix="/api/staging", tags=["staging"])


# ===== 승인 관리 =====
@router.post("/brands/{brand_id}/approve")
def approve_staging_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Staging 브랜드 승인"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        brand = brand_repo.find_by_id(brand_id)
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 승인 처리
        brand.approval_status = ApprovalStatus.APPROVED
        brand.approved_by = current_user.username
        brand.approved_at = datetime.utcnow()
        
        result = brand_repo.update(brand_id, brand)
        return {"message": "브랜드가 승인되었습니다", "brand": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 승인 실패: {str(e)}")


@router.post("/brands/{brand_id}/reject")
def reject_staging_brand(
    brand_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Staging 브랜드 거부"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        brand = brand_repo.find_by_id(brand_id)
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 거부 처리
        brand.approval_status = ApprovalStatus.REJECTED
        brand.rejected_by = current_user.username
        brand.rejected_at = datetime.utcnow()
        brand.rejection_reason = reason
        
        result = brand_repo.update(brand_id, brand)
        return {"message": "브랜드가 거부되었습니다", "brand": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 거부 실패: {str(e)}")


# ===== 버전별 승인 상태 조회 =====
@router.get("/version/{version_id}/approval-status")
def get_version_approval_status(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """버전별 승인 상태 조회"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        vehicle_line_repo = SQLAlchemyStagingVehicleLineRepository(db)
        model_repo = SQLAlchemyStagingModelRepository(db)
        trim_repo = SQLAlchemyStagingTrimRepository(db)
        option_repo = SQLAlchemyStagingOptionRepository(db)
        
        # 버전별 데이터 조회
        brands = brand_repo.find_all_by_version(version_id)
        
        status_summary = {
            "version_id": version_id,
            "brands": {
                "total": len(brands),
                "approved": 0,
                "rejected": 0,
                "pending": 0
            },
            "vehicle_lines": {"total": 0},
            "models": {"total": 0},
            "trims": {"total": 0},
            "options": {"total": 0}
        }
        
        # 승인 상태별 카운트
        for brand in brands:
            if brand.approval_status == ApprovalStatus.APPROVED:
                status_summary["brands"]["approved"] += 1
            elif brand.approval_status == ApprovalStatus.REJECTED:
                status_summary["brands"]["rejected"] += 1
            else:
                status_summary["brands"]["pending"] += 1
            
            # 하위 엔티티 수 계산
            vehicle_lines = vehicle_line_repo.find_all_by_brand(brand.id)
            status_summary["vehicle_lines"]["total"] += len(vehicle_lines)
            
            for vl in vehicle_lines:
                models = model_repo.find_all_by_vehicle_line(vl.id)
                status_summary["models"]["total"] += len(models)
                
                for model in models:
                    trims = trim_repo.find_all_by_model(model.id)
                    status_summary["trims"]["total"] += len(trims)
                    
                    for trim in trims:
                        options = option_repo.find_all_by_trim(trim.id)
                        status_summary["options"]["total"] += len(options)
        
        return status_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"승인 상태 조회 실패: {str(e)}")


# ===== 대량 승인/거부 =====
@router.post("/version/{version_id}/approve-all")
def approve_all_staging_data(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """버전의 모든 스테이징 데이터 승인"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        brands = brand_repo.find_all_by_version(version_id)
        
        approved_count = 0
        for brand in brands:
            if brand.approval_status != ApprovalStatus.APPROVED:
                brand.approval_status = ApprovalStatus.APPROVED
                brand.approved_by = current_user.username
                brand.approved_at = datetime.utcnow()
                brand_repo.update(brand.id, brand)
                approved_count += 1
        
        return {
            "message": f"{approved_count}개의 브랜드가 승인되었습니다",
            "approved_count": approved_count,
            "total_count": len(brands)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대량 승인 실패: {str(e)}")


@router.post("/version/{version_id}/reject-all")
def reject_all_staging_data(
    version_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """버전의 모든 스테이징 데이터 거부"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        brands = brand_repo.find_all_by_version(version_id)
        
        rejected_count = 0
        for brand in brands:
            if brand.approval_status != ApprovalStatus.REJECTED:
                brand.approval_status = ApprovalStatus.REJECTED
                brand.rejected_by = current_user.username
                brand.rejected_at = datetime.utcnow()
                brand.rejection_reason = reason
                brand_repo.update(brand.id, brand)
                rejected_count += 1
        
        return {
            "message": f"{rejected_count}개의 브랜드가 거부되었습니다",
            "rejected_count": rejected_count,
            "total_count": len(brands)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대량 거부 실패: {str(e)}")


# ===== 스테이징 데이터 요약 정보 =====
@router.get("/summary")
def get_staging_summary(
    version_id: Optional[int] = Query(None, description="버전 ID 필터링"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """스테이징 데이터 요약 정보"""
    try:
        brand_repo = SQLAlchemyStagingBrandRepository(db)
        vehicle_line_repo = SQLAlchemyStagingVehicleLineRepository(db)
        model_repo = SQLAlchemyStagingModelRepository(db)
        trim_repo = SQLAlchemyStagingTrimRepository(db)
        option_repo = SQLAlchemyStagingOptionRepository(db)
        
        if version_id:
            brands = brand_repo.find_all_by_version(version_id)
            brand_count = len(brands)
            
            vehicle_line_count = 0
            model_count = 0
            trim_count = 0
            option_count = 0
            
            for brand in brands:
                vehicle_lines = vehicle_line_repo.find_all_by_brand(brand.id)
                vehicle_line_count += len(vehicle_lines)
                
                for vehicle_line in vehicle_lines:
                    models = model_repo.find_all_by_vehicle_line(vehicle_line.id)
                    model_count += len(models)
                    
                    for model in models:
                        trims = trim_repo.find_all_by_model(model.id)
                        trim_count += len(trims)
                        
                        for trim in trims:
                            options = option_repo.find_all_by_trim(trim.id)
                            option_count += len(options)
        else:
            # 전체 시스템의 각 테이블별 개수 조회
            brand_count = brand_repo.count()
            vehicle_line_count = vehicle_line_repo.count()
            model_count = model_repo.count()
            trim_count = trim_repo.count()
            option_count = option_repo.count()
            
            print(f"[DEBUG] 전체 시스템 통계 - 브랜드: {brand_count}, 모델: {model_count}, 트림: {trim_count}, 옵션: {option_count}")
        
        # 전체 시스템 데이터 합계
        total_system_items = brand_count + vehicle_line_count + model_count + trim_count + option_count
        
        return {
            "summary": {
                "brand_count": brand_count,
                "brands": brand_count,
                "vehicle_lines": vehicle_line_count,
                "models": model_count,
                "trims": trim_count,
                "options": option_count,
                "total_items": total_system_items,
                "total_system_data": total_system_items  # 전체 시스템 데이터 수
            },
            "debug_info": {
                "brand_count": brand_count,
                "model_count": model_count,
                "trim_count": trim_count,
                "option_count": option_count,
                "total_count": total_system_items
            },
            "note": "계층 구조에서 버전 단위로 승인 관리됩니다. 개별 엔티티별 승인은 지원하지 않습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 정보 조회 실패: {str(e)}")