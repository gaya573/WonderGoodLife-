"""
Version Management API - 버전 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import uuid
import os
import json
import zipfile
import io

from app.infrastructure.database import get_db
from app.infrastructure.repositories import SQLAlchemyStagingVersionRepository
from app.infrastructure.orm_models import BatchJobORM
from app.domain.entities import StagingVersion, JobStatus, JobType
from app.presentation.dependencies import get_current_user
from app.tasks.excel_tasks import process_excel_file

router = APIRouter(prefix="/api/versions", tags=["versions"])


@router.get("/")
def get_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="검색어 (버전명 또는 설명)"),
    approval_status: Optional[str] = Query(None, description="승인 상태 필터"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전 목록 조회 (검색 및 필터 지원)"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM,
            StagingVersionORM
        )
        
        # 쿼리 빌드
        query = db.query(StagingVersionORM)
        
        # 검색 조건 추가
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (StagingVersionORM.version_name.like(search_term)) |
                (StagingVersionORM.description.like(search_term))
            )
        
        # 상태 필터 추가
        if approval_status:
            query = query.filter(StagingVersionORM.approval_status == approval_status)
        
        # 총 개수 조회
        total_count = query.count()
        
        # 페이지네이션 적용
        versions = query.offset(skip).limit(limit).all()
        
        # 각 버전별로 통계 계산 (프론트엔드와 동일한 방식)
        version_items = []
        for version in versions:
            # 해당 버전의 브랜드 개수
            total_brands = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version.id).count()
            
            # 해당 버전의 모델 개수 (브랜드 -> 차량라인 -> 모델)
            total_models = db.query(StagingModelORM).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(StagingBrandORM.version_id == version.id).count()
            
            # 해당 버전의 트림 개수 (브랜드 -> 차량라인 -> 모델 -> 트림)
            total_trims = db.query(StagingTrimORM).join(
                StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
            ).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(StagingBrandORM.version_id == version.id).count()
            
            version_items.append({
                    "id": version.id,
                "version_name": version.version_name,
                    "description": version.description,
                "approval_status": version.approval_status.value if version.approval_status else None,
                    "created_by": version.created_by,
                    "created_at": version.created_at.isoformat() if version.created_at else None,
                "updated_at": version.updated_at.isoformat() if version.updated_at else None,
                "total_brands": total_brands,
                "total_models": total_models,
                "total_trims": total_trims
            })
        
        return {
            "items": version_items,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 목록 조회 실패: {str(e)}")


@router.get("/{version_id}")
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """특정 버전 조회"""
    try:
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        return {
            "id": version.id,
            "version_name": version.version_name,
            "description": version.description,
            "approval_status": version.approval_status.value if version.approval_status else None,
            "created_by": version.created_by,
            "created_at": version.created_at.isoformat() if version.created_at else None,
            "updated_at": version.updated_at.isoformat() if version.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 조회 실패: {str(e)}")


@router.post("/")
def create_version(
    version_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 버전 생성"""
    try:
        from app.infrastructure.orm_models import StagingVersionORM
        from app.domain.entities import ApprovalStatus
        
        # 프론트엔드에서 전송하는 필드명에 맞춰 데이터 추출
        version_name = version_data.get('name') or version_data.get('version_name')
        description = version_data.get('description')
        created_by = version_data.get('created_by') or current_user.get('username', 'admin')
        
        if not version_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="버전명은 필수입니다"
            )
        
        new_version = StagingVersionORM(
            version_name=version_name,
            description=description,
            approval_status=ApprovalStatus.PENDING,
            created_by=created_by
        )
        # 통계 필드는 동적으로 계산하므로 저장하지 않음
        
        version_repo = SQLAlchemyStagingVersionRepository(db)
        created_version = version_repo.save(new_version)
        
        return {
                "id": created_version.id,
            "version_name": created_version.version_name,
                "description": created_version.description,
            "approval_status": created_version.approval_status.value if created_version.approval_status else None,
            "created_by": created_version.created_by,
            "created_at": created_version.created_at.isoformat() if created_version.created_at else None,
            "updated_at": created_version.updated_at.isoformat() if created_version.updated_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 생성 실패: {str(e)}")


@router.put("/{version_id}")
def update_version(
    version_id: int,
    version_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전 수정"""
    try:
        version_repo = SQLAlchemyStagingVersionRepository(db)
        existing_version = version_repo.find_by_id(version_id)
        
        if not existing_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 버전 정보 업데이트
        if 'version_name' in version_data:
            existing_version.version_name = version_data['version_name']
        elif 'name' in version_data:  # 하위 호환성을 위해 유지
            existing_version.version_name = version_data['name']
        
        if 'description' in version_data:
            existing_version.description = version_data['description']
        
        # 승인 상태 업데이트 허용 (승인신청용)
        if 'approval_status' in version_data:
            from app.domain.entities import ApprovalStatus
            if version_data['approval_status'] == 'PENDING':
                existing_version.approval_status = ApprovalStatus.PENDING
        
        # updated_at은 자동으로 업데이트됨
        
        updated_version = version_repo.update(version_id, existing_version)
        
        return {
            "success": True,
            "message": "버전이 성공적으로 수정되었습니다",
            "version": {
                "id": updated_version.id,
                "version_name": updated_version.version_name,
                "description": updated_version.description,
                "approval_status": updated_version.approval_status.value if updated_version.approval_status else None,
                "created_by": updated_version.created_by,
                "created_at": updated_version.created_at.isoformat() if updated_version.created_at else None,
                "updated_at": updated_version.updated_at.isoformat() if updated_version.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 수정 실패: {str(e)}")


@router.delete("/{version_id}")
def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전 삭제"""
    try:
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        version_repo.delete(version_id)
        return {"message": "버전이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 삭제 실패: {str(e)}")




# 자동차 라인별 전체 데이터 조회 - 무한스크롤용 (각 자동차 라인의 모든 브랜드/모델/트림/옵션 포함)
@router.get("/{version_id}/vehicle-lines-with-full-data")
def get_vehicle_lines_with_full_data(
    version_id: int, 
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(1, ge=1, le=50, description="페이지당 자동차 라인 수"),
    db: Session = Depends(get_db)
):
    """자동차 라인별 전체 데이터 조회 - 무한스크롤용 (각 자동차 라인의 모든 브랜드/모델/트림/옵션 포함)"""
    try:
        print(f"[DEBUG] get_vehicle_lines_with_full_data called for version_id: {version_id}")
        
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        print(f"[DEBUG] Version found: {version}")
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )

        # 1. 먼저 해당 버전의 자동라인의 총 개수 조회 (브랜드를 통해 조회)
        total_vehicle_lines_count = db.query(StagingVehicleLineORM).join(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).count()

        # 2. 페이지네이션을 사용하여 자동차 라인 목록 가져오기 (브랜드를 통해 조회)
        skip = (page - 1) * limit
        vehicle_lines_list = db.query(StagingVehicleLineORM).join(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).offset(skip).limit(limit).all()
        
        # 페이지네이션 정보 계산
        total_pages = (total_vehicle_lines_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        print(f"[DEBUG] 버전 {version_id}의 자동라인 총 개수: {total_vehicle_lines_count}")
        print(f"[DEBUG] 현재 페이지: {page}/{total_pages}, 페이지당 {limit}개")
        print(f"[DEBUG] 현재 페이지 자동라인 개수: {len(vehicle_lines_list)}")
        
        if not vehicle_lines_list:
            return {
                "version": {
                    "id": version.id,
                    "name": version.version_name,
                    "description": version.description,
                    "total_brands": 0,
                    "total_vehicle_lines": 0,
                    "total_models": 0,
                    "total_trims": 0,
                    "total_options": 0
                },
                "vehicle_lines": [],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_count": total_vehicle_lines_count,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
        
        # 3. 각 자동차 라인의 브랜드, 모델, 트림, 옵션 데이터 가져오기
        print(f"[DEBUG] 자동라인 ID 목록: {[vl.id for vl in vehicle_lines_list]}")
        
        vehicle_lines_data = []
        total_brands = 0
        total_models = 0
        total_trims = 0
        total_options = 0
        
        for vehicle_line in vehicle_lines_list:
            # 자동차 라인 기본 정보
            vehicle_line_data = {
                "id": vehicle_line.id,
                "name": vehicle_line.name,
                "description": vehicle_line.description,
                "brand": None,  # 자동차 라인은 하나의 브랜드에만 속함
                "models": []
            }
            
            # 해당 자동차 라인의 브랜드 조회 (자동차 라인은 하나의 브랜드에만 속함)
            brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == vehicle_line.brand_id).first()
            
            if brand:
                vehicle_line_data["brand"] = {
                    "id": brand.id,
                    "name": brand.name,
                    "country": brand.country,
                    "logo_url": brand.logo_url,
                    "manager": brand.manager,
                    "created_by": brand.created_by,
                    "created_by_username": brand.created_by_username,
                    "created_by_email": brand.created_by_email,
                    "created_at": brand.created_at.isoformat() if brand.created_at else None,
                    "updated_by_username": brand.updated_by_username,
                    "updated_by_email": brand.updated_by_email,
                    "updated_at": brand.updated_at.isoformat() if brand.updated_at else None
                }
                total_brands += 1
            
            # 해당 자동차 라인의 모델들 조회
            models_list = db.query(StagingModelORM).filter(StagingModelORM.vehicle_line_id == vehicle_line.id).all()
           
            for model in models_list:
                model_data = {
                    "id": model.id,
                    "name": model.name,
                    "code": model.code,
                    "release_year": model.release_year,
                    "price": model.price,
                    "foreign": model.foreign,
                    "created_by": model.created_by,
                    "created_by_username": model.created_by_username,
                    "created_by_email": model.created_by_email,
                    "created_at": model.created_at.isoformat() if model.created_at else None,
                    "updated_by_username": model.updated_by_username,
                    "updated_by_email": model.updated_by_email,
                    "updated_at": model.updated_at.isoformat() if model.updated_at else None,
                    "trims": []
                }
                total_models += 1
                
                # 해당 모델의 트림들 조회
                trims_list = db.query(StagingTrimORM).filter(StagingTrimORM.model_id == model.id).all()
                
                for trim in trims_list:
                    trim_data = {
                        "id": trim.id,
                        "name": trim.name,
                        "description": trim.description,
                        "car_type": trim.car_type,
                        "fuel_name": trim.fuel_name,
                        "cc": trim.cc,
                        "base_price": trim.base_price,
                        "created_by": trim.created_by,
                        "created_by_username": trim.created_by_username,
                        "created_by_email": trim.created_by_email,
                        "created_at": trim.created_at.isoformat() if trim.created_at else None,
                        "updated_by_username": trim.updated_by_username,
                        "updated_by_email": trim.updated_by_email,
                        "updated_at": trim.updated_at.isoformat() if trim.updated_at else None,
                        "options": []
                    }
                    total_trims += 1
                    
                    # 해당 트림의 옵션들 조회
                    options_list = db.query(StagingOptionORM).filter(StagingOptionORM.trim_id == trim.id).all()

                    for option in options_list:
                        option_data = {
                            "id": option.id,
                            "name": option.name,
                            "code": option.code,
                            "description": option.description,
                            "category": option.category,
                            "price": option.price,
                            "discounted_price": option.discounted_price,
                            "created_by": option.created_by,
                            "created_by_username": option.created_by_username,
                            "created_by_email": option.created_by_email,
                            "created_at": option.created_at.isoformat() if option.created_at else None,
                            "updated_by_username": option.updated_by_username,
                            "updated_by_email": option.updated_by_email,
                            "updated_at": option.updated_at.isoformat() if option.updated_at else None
                        }
                        trim_data["options"].append(option_data)
                        total_options += 1
                    
                    model_data["trims"].append(trim_data)
                
                vehicle_line_data["models"].append(model_data)
            
            vehicle_lines_data.append(vehicle_line_data)
        
        print(f"[DEBUG] 데이터 통계 - 브랜드: {total_brands}, 모델: {total_models}, 트림: {total_trims}, 옵션: {total_options}")
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name,
                "description": version.description,
                "total_brands": total_brands,
                "total_vehicle_lines": len(vehicle_lines_data),
                "total_models": total_models,
                "total_trims": total_trims,
                "total_options": total_options
            },
            "vehicle_lines": vehicle_lines_data,
            "pagination": {
                "current_page": page,
            "total_pages": total_pages,
                "total_count": total_vehicle_lines_count,
            "has_next": has_next,
            "has_prev": has_prev
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] get_vehicle_lines_with_full_data: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")


# 브랜드별 전체 데이터 조회 (모델/트림/옵션 포함)
@router.get("/{version_id}/brands-with-full-data")
def get_brands_with_full_data(
    version_id: int,
    brand_name: Optional[str] = Query(None, description="브랜드명 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=50, description="페이지당 브랜드 수"),
    db: Session = Depends(get_db)
):
    """브랜드별 전체 데이터 조회 - 모델/트림/옵션 포함"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 브랜드 쿼리 구성
        brand_query = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id)
        
        # 브랜드명 필터 적용
        if brand_name:
            brand_query = brand_query.filter(StagingBrandORM.name.ilike(f"%{brand_name}%"))
        
        # 전체 브랜드 수 계산
        total_brands = brand_query.count()
        
        # 페이지네이션 적용
        offset = (page - 1) * limit
        brands = brand_query.offset(offset).limit(limit).all()
        
        brands_data = []
        for brand in brands:
            # 해당 브랜드의 모든 차량 라인 조회
            vehicle_lines = db.query(StagingVehicleLineORM).filter(
                StagingVehicleLineORM.brand_id == brand.id
            ).all()
            
            vehicle_lines_data = []
            for vehicle_line in vehicle_lines:
                # 해당 차량 라인의 모든 모델 조회
                models = db.query(StagingModelORM).filter(
                    StagingModelORM.vehicle_line_id == vehicle_line.id
                ).all()
                
                models_data = []
                for model in models:
                    # 해당 모델의 모든 트림 조회
                    trims = db.query(StagingTrimORM).filter(
                        StagingTrimORM.model_id == model.id
                    ).all()
                    
                    trims_data = []
                    for trim in trims:
                        # 해당 트림의 모든 옵션 조회
                        options = db.query(StagingOptionORM).filter(
                            StagingOptionORM.trim_id == trim.id
                        ).all()
                        
                        options_data = []
                        for option in options:
                            options_data.append({
                                "id": option.id,
                                "name": option.name,
                                "code": option.code,
                                "price": option.price,
                                "discounted_price": option.discounted_price,
                                "category": option.category,
                                "created_at": option.created_at.isoformat() if option.created_at else None
                            })
                        
                        trims_data.append({
                            "id": trim.id,
                            "name": trim.name,
                            "car_type": trim.car_type,
                            "fuel_name": trim.fuel_name,
                            "cc": trim.cc,
                            "base_price": trim.base_price,
                            "description": trim.description,
                            "options": options_data
                        })
                    
                    models_data.append({
                        "id": model.id,
                        "name": model.name,
                        "code": model.code,
                        "release_year": model.release_year,
                        "price": model.price,
                        "foreign": model.foreign,
                        "trims": trims_data
                    })
                
                vehicle_lines_data.append({
                    "id": vehicle_line.id,
                    "name": vehicle_line.name,
                    "description": vehicle_line.description,
                    "models": models_data
                })
            
            brands_data.append({
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "logo_url": brand.logo_url,
                "manager": brand.manager,
                "vehicle_lines": vehicle_lines_data,
                "created_at": brand.created_at.isoformat() if brand.created_at else None
            })
        
        # 페이지네이션 정보 계산
        total_pages = (total_brands + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name,
                "description": version.description
            },
            "brands": brands_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_brands,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 데이터 조회 실패: {str(e)}")

# 디버깅용: 버전의 모든 브랜드 목록 조회
@router.get("/{version_id}/brands-summary")
def get_brands_summary(
    version_id: int,
    db: Session = Depends(get_db)
):
    """디버깅용: 버전의 모든 브랜드 목록 조회"""
    try:
        from app.infrastructure.orm_models import StagingBrandORM
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 해당 버전의 모든 브랜드 조회
        brands = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).all()
        
        brands_summary = []
        for brand in brands:
            brands_summary.append({
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "manager": brand.manager,
                "created_at": brand.created_at.isoformat() if brand.created_at else None
            })
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name,
                "description": version.description
            },
            "brands": brands_summary,
            "total_brands": len(brands_summary)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 목록 조회 실패: {str(e)}")


# 간단한 브랜드 목록 API (할인 정책용)
@router.get("/{version_id}/brands-list")
def get_brands_list(
    version_id: int,
    db: Session = Depends(get_db)
):
    """버전의 브랜드 ID와 이름만 조회 (할인 정책 선택용)"""
    try:
        from app.infrastructure.orm_models import StagingBrandORM, StagingVersionORM
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 해당 버전의 모든 브랜드 조회
        brands = db.query(StagingBrandORM).filter(
            StagingBrandORM.version_id == version_id
        ).all()
        
        return {
            "version_id": version_id,
            "version_name": version.version_name,
            "brands": [
                {"id": b.id, "name": b.name, "country": b.country}
                for b in brands
            ],
            "total": len(brands)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브랜드 목록 조회 실패: {str(e)}")


# 브랜드별 Vehicle Line 목록 API (할인 정책용)
@router.get("/{version_id}/brands/{brand_id}/vehicle-lines")
def get_brand_vehicle_lines(
    version_id: int,
    brand_id: int,
    db: Session = Depends(get_db)
):
    """특정 브랜드의 모든 Vehicle Line 조회 (할인 정책 선택용)"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVersionORM,
            StagingVehicleLineORM
        )
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 브랜드 확인
        brand = db.query(StagingBrandORM).filter(
            StagingBrandORM.id == brand_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 해당 브랜드의 모든 Vehicle Line 조회
        vehicle_lines = db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.brand_id == brand_id
        ).all()
        
        return {
            "version_id": version_id,
            "brand_id": brand_id,
            "brand_name": brand.name,
            "vehicle_lines": [
                {"id": vl.id, "name": vl.name, "description": vl.description}
                for vl in vehicle_lines
            ],
            "total": len(vehicle_lines)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vehicle Line 목록 조회 실패: {str(e)}")


# 브랜드별 트림 목록 API (할인 정책용)
@router.get("/{version_id}/brands/{brand_id}/trims")
def get_brand_trims(
    version_id: int,
    brand_id: int,
    db: Session = Depends(get_db)
):
    """특정 브랜드의 모든 트림 조회 (할인 정책 선택용)"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVersionORM,
            StagingVehicleLineORM, StagingModelORM, StagingTrimORM
        )
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 브랜드 확인
        brand = db.query(StagingBrandORM).filter(
            StagingBrandORM.id == brand_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 해당 브랜드의 모든 트림 조회 (JOIN with model)
        trims_data = db.query(StagingTrimORM, StagingModelORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingBrandORM.version_id == version_id,
            StagingBrandORM.id == brand_id
        ).all()
        
        # 트림 데이터 구성
        trims_result = []
        for trim, model in trims_data:
            trims_result.append({
                "id": trim.id,
                "name": trim.name,
                "model_name": model.name if model else None,
                "car_type": trim.car_type.value if hasattr(trim.car_type, 'value') else str(trim.car_type),
                "fuel_name": trim.fuel_name,
                "base_price": trim.base_price
            })
        
        return {
            "version_id": version_id,
            "version_name": version.version_name,
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "country": brand.country
            },
            "trims": trims_result,
            "total": len(trims_result)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 트림 목록 조회 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"트림 목록 조회 실패: {str(e)}")


# Vehicle Line별 트림 목록 API (할인 정책용)
@router.get("/{version_id}/brands/{brand_id}/vehicle-lines/{vehicle_line_id}/trims")
def get_vehicle_line_trims(
    version_id: int,
    brand_id: int,
    vehicle_line_id: int,
    db: Session = Depends(get_db)
):
    """특정 Vehicle Line의 모든 트림 조회 (할인 정책 선택용)"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVersionORM,
            StagingVehicleLineORM, StagingModelORM, StagingTrimORM
        )
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 브랜드 확인
        brand = db.query(StagingBrandORM).filter(
            StagingBrandORM.id == brand_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # Vehicle Line 확인
        vehicle_line = db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.id == vehicle_line_id,
            StagingVehicleLineORM.brand_id == brand_id
        ).first()
        
        if not vehicle_line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle Line을 찾을 수 없습니다"
            )
        
        # 해당 Vehicle Line의 모든 트림 조회 (JOIN with model)
        trims_data = db.query(StagingTrimORM, StagingModelORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).filter(
            StagingModelORM.vehicle_line_id == vehicle_line_id
        ).all()
        
        # 트림 데이터 구성
        trims_result = []
        for trim, model in trims_data:
            trims_result.append({
                "id": trim.id,
                "name": trim.name,
                "model_name": model.name if model else None,
                "car_type": trim.car_type.value if hasattr(trim.car_type, 'value') else str(trim.car_type),
                "fuel_name": trim.fuel_name,
                "base_price": trim.base_price
            })
        
        return {
            "version_id": version_id,
            "version_name": version.version_name,
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "country": brand.country
            },
            "vehicle_line": {
                "id": vehicle_line.id,
                "name": vehicle_line.name
            },
            "trims": trims_result,
            "total": len(trims_result)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Vehicle Line 트림 목록 조회 실패: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Vehicle Line 트림 목록 조회 실패: {str(e)}")


@router.get("/{version_id}/filtered-data")
def get_filtered_data(
    version_id: int,
    brand: str = Query(None, description="브랜드명"),
    model: str = Query(None, description="모델명"),
    trim: str = Query(None, description="트림명"),
    db: Session = Depends(get_db)
):
    """필터링된 브랜드 데이터 조회 (파라미터 분리)"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM,
            StagingVersionORM
        )
        from sqlalchemy import text
        import logging
        logger = logging.getLogger(__name__)
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 파라미터 로깅
        logger.info(f"[DEBUG] 필터 파라미터 - brand: {brand}, model: {model}, trim: {trim}")
        
        # 파라미터 검증
        if not any([brand, model, trim]):
            return {
                "version": {
                    "id": version.id,
                    "name": version.version_name
                },
                "brands": [],
                "total_count": 0,
                "filtered_by_search": True,
                "message": "필터 파라미터가 없습니다"
            }
        
        # 검색 쿼리로 매칭되는 브랜드 ID들 찾기
        search_query = text("""
            SELECT DISTINCT sb.id as brand_id
            FROM staging_brand sb
            LEFT JOIN staging_vehicle_line svl ON sb.id = svl.brand_id
            LEFT JOIN staging_model sm ON svl.id = sm.vehicle_line_id
            LEFT JOIN staging_trim st ON sm.id = st.model_id
            WHERE sb.version_id = :version_id
            AND (
                (:brand IS NULL OR sb.name LIKE :brand_term)
                OR (:model IS NULL OR sm.name LIKE :model_term)
                OR (:trim IS NULL OR st.name LIKE :trim_term)
            )
        """)
        
        brand_term = f"%{brand}%" if brand else None
        model_term = f"%{model}%" if model else None
        trim_term = f"%{trim}%" if trim else None
        result = db.execute(search_query, {
            "version_id": version_id,
            "brand": brand,
            "model": model,
            "trim": trim,
            "brand_term": brand_term,
            "model_term": model_term,
            "trim_term": trim_term
        })
        
        matching_brand_ids = [row.brand_id for row in result.fetchall()]
        
        if not matching_brand_ids:
            return {
                "version": {
                    "id": version.id,
                    "name": version.version_name
                },
                "brands": [],
                "total_count": 0,
                "filtered_by_search": True,
                "filters": {"brand": brand, "model": model, "trim": trim}
            }
        
        logger.info(f"[DEBUG] 매칭된 브랜드 ID들: {matching_brand_ids}")
        
        # 매칭된 브랜드들의 전체 데이터 조회
        brands_query = text("""
            SELECT 
                sb.id as brand_id,
                sb.name as brand_name,
                sb.country as brand_country,
                sb.logo_url as brand_logo_url,
                sb.created_by as brand_created_by,
                sb.created_by_username as brand_created_by_username,
                sb.created_by_email as brand_created_by_email,
                sb.created_at as brand_created_at,
                sb.updated_by_username as brand_updated_by_username,
                sb.updated_by_email as brand_updated_by_email,
                sb.updated_at as brand_updated_at
            FROM staging_brand sb
            WHERE sb.id IN :brand_ids
            ORDER BY sb.name
        """)
        
        brands_result = db.execute(brands_query, {"brand_ids": tuple(matching_brand_ids)})
        brands_data = []
        
        for brand_row in brands_result.fetchall():
            # 각 브랜드의 차량라인, 모델, 트림, 옵션 데이터 조회
            vehicle_lines_query = text("""
                SELECT 
                    svl.id as vehicle_line_id,
                    svl.name as vehicle_line_name,
                    svl.created_by as vehicle_line_created_by,
                    svl.created_by_username as vehicle_line_created_by_username,
                    svl.created_by_email as vehicle_line_created_by_email,
                    svl.created_at as vehicle_line_created_at,
                    svl.updated_by_username as vehicle_line_updated_by_username,
                    svl.updated_by_email as vehicle_line_updated_by_email,
                    svl.updated_at as vehicle_line_updated_at
                FROM staging_vehicle_line svl
                WHERE svl.brand_id = :brand_id
                ORDER BY svl.name
            """)
            
            vehicle_lines_result = db.execute(vehicle_lines_query, {"brand_id": brand_row.brand_id})
            vehicle_lines_data = []
            
            for vl_row in vehicle_lines_result.fetchall():
                # 각 차량라인의 모델 데이터 조회
                models_query = text("""
                    SELECT 
                        sm.id as model_id,
                        sm.name as model_name,
                        sm.code as model_code,
                        sm.price as model_price,
                        sm.foreign as model_foreign,
                        sm.created_by as model_created_by,
                        sm.created_by_username as model_created_by_username,
                        sm.created_by_email as model_created_by_email,
                        sm.created_at as model_created_at,
                        sm.updated_by_username as model_updated_by_username,
                        sm.updated_by_email as model_updated_by_email,
                        sm.updated_at as model_updated_at
                    FROM staging_model sm
                    WHERE sm.vehicle_line_id = :vehicle_line_id
                    ORDER BY sm.name
                """)
                
                models_result = db.execute(models_query, {"vehicle_line_id": vl_row.vehicle_line_id})
                models_data = []
                
                for model_row in models_result.fetchall():
                    # 각 모델의 트림 데이터 조회
                    trims_query = text("""
                        SELECT 
                            st.id as trim_id,
                            st.name as trim_name,
                            st.car_type as trim_car_type,
                            st.fuel_name as trim_fuel_name,
                            st.cc as trim_cc,
                            st.base_price as trim_base_price,
                            st.created_by as trim_created_by,
                            st.created_by_username as trim_created_by_username,
                            st.created_by_email as trim_created_by_email,
                            st.created_at as trim_created_at,
                            st.updated_by_username as trim_updated_by_username,
                            st.updated_by_email as trim_updated_by_email,
                            st.updated_at as trim_updated_at
                        FROM staging_trim st
                        WHERE st.model_id = :model_id
                        ORDER BY st.name
                    """)
                    
                    trims_result = db.execute(trims_query, {"model_id": model_row.model_id})
                    trims_data = []
                    
                    for trim_row in trims_result.fetchall():
                        # 각 트림의 옵션 데이터 조회
                        options_query = text("""
                            SELECT 
                                so.id as option_id,
                                so.name as option_name,
                                so.code as option_code,
                                so.description as option_description,
                                so.category as option_category,
                                so.price as option_price,
                                so.discounted_price as option_discounted_price,
                                so.created_by as option_created_by,
                                so.created_by_username as option_created_by_username,
                                so.created_by_email as option_created_by_email,
                                so.created_at as option_created_at,
                                so.updated_by_username as option_updated_by_username,
                                so.updated_by_email as option_updated_by_email,
                                so.updated_at as option_updated_at
                            FROM staging_option so
                            WHERE so.trim_id = :trim_id
                            ORDER BY so.name
                        """)
                        
                        options_result = db.execute(options_query, {"trim_id": trim_row.trim_id})
                        options_data = []
                        
                        for option_row in options_result.fetchall():
                            options_data.append({
                                "id": option_row.option_id,
                                "name": option_row.option_name,
                                "code": option_row.option_code,
                                "description": option_row.option_description,
                                "category": option_row.option_category,
                                "price": option_row.option_price,
                                "discounted_price": option_row.option_discounted_price,
                                "created_by": option_row.option_created_by,
                                "created_by_username": option_row.option_created_by_username,
                                "created_by_email": option_row.option_created_by_email,
                                "created_at": option_row.option_created_at.isoformat() if option_row.option_created_at else None,
                                "updated_by_username": option_row.option_updated_by_username,
                                "updated_by_email": option_row.option_updated_by_email,
                                "updated_at": option_row.option_updated_at.isoformat() if option_row.option_updated_at else None
                            })
                        
                        trims_data.append({
                            "id": trim_row.trim_id,
                            "name": trim_row.trim_name,
                            "car_type": trim_row.trim_car_type,
                            "fuel_name": trim_row.trim_fuel_name,
                            "cc": trim_row.trim_cc,
                            "base_price": trim_row.trim_base_price,
                            "created_by": trim_row.trim_created_by,
                            "created_by_username": trim_row.trim_created_by_username,
                            "created_by_email": trim_row.trim_created_by_email,
                            "created_at": trim_row.trim_created_at.isoformat() if trim_row.trim_created_at else None,
                            "updated_by_username": trim_row.trim_updated_by_username,
                            "updated_by_email": trim_row.trim_updated_by_email,
                            "updated_at": trim_row.trim_updated_at.isoformat() if trim_row.trim_updated_at else None,
                            "options": options_data
                        })
                    
                    models_data.append({
                        "id": model_row.model_id,
                        "name": model_row.model_name,
                        "code": model_row.model_code,
                        "price": model_row.model_price,
                        "foreign": model_row.model_foreign,
                        "created_by": model_row.model_created_by,
                        "created_by_username": model_row.model_created_by_username,
                        "created_by_email": model_row.model_created_by_email,
                        "created_at": model_row.model_created_at.isoformat() if model_row.model_created_at else None,
                        "updated_by_username": model_row.model_updated_by_username,
                        "updated_by_email": model_row.model_updated_by_email,
                        "updated_at": model_row.model_updated_at.isoformat() if model_row.model_updated_at else None,
                        "trims": trims_data
                    })
                
                vehicle_lines_data.append({
                    "id": vl_row.vehicle_line_id,
                    "name": vl_row.vehicle_line_name,
                    "created_by": vl_row.vehicle_line_created_by,
                    "created_by_username": vl_row.vehicle_line_created_by_username,
                    "created_by_email": vl_row.vehicle_line_created_by_email,
                    "created_at": vl_row.vehicle_line_created_at.isoformat() if vl_row.vehicle_line_created_at else None,
                    "updated_by_username": vl_row.vehicle_line_updated_by_username,
                    "updated_by_email": vl_row.vehicle_line_updated_by_email,
                    "updated_at": vl_row.vehicle_line_updated_at.isoformat() if vl_row.vehicle_line_updated_at else None,
                    "models": models_data
                })
            
            brands_data.append({
                "id": brand_row.brand_id,
                "name": brand_row.brand_name,
                "country": brand_row.brand_country,
                "logo_url": brand_row.brand_logo_url,
                "created_by": brand_row.brand_created_by,
                "created_by_username": brand_row.brand_created_by_username,
                "created_by_email": brand_row.brand_created_by_email,
                "created_at": brand_row.brand_created_at.isoformat() if brand_row.brand_created_at else None,
                "updated_by_username": brand_row.brand_updated_by_username,
                "updated_by_email": brand_row.brand_updated_by_email,
                "updated_at": brand_row.brand_updated_at.isoformat() if brand_row.brand_updated_at else None,
                "vehicle_lines": vehicle_lines_data
            })
        
        logger.info(f"[DEBUG] 반환할 브랜드 수: {len(brands_data)}")
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name
            },
            "brands": brands_data,
            "total_count": len(brands_data),
            "filtered_by_search": True,
            "filters": {"brand": brand, "model": model, "trim": trim}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] get_filtered_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"필터링 실패: {str(e)}")


@router.get("/{version_id}/search")
def search_version_data(
    version_id: int,
    query: str = Query(..., description="검색어"),
    limit: int = Query(20, description="검색 결과 개수 제한"),
    db: Session = Depends(get_db)
):
    """버전 데이터 검색 - URL 인코딩 자동 처리"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        print(f"[DEBUG] 검색 시작 - version_id: {version_id}, query: '{query}'")
        print(f"[DEBUG] 검색어 타입: {type(query)}, 길이: {len(query)}")
        print(f"[DEBUG] 검색어 바이트: {query.encode('utf-8')}")
        
        # URL 디코딩 (완전한 처리)
        import urllib.parse
        
        decoded_query = query
        
        try:
            # 1차: FastAPI 자동 디코딩 (이미 처리됨)
            # 2차: 수동 디코딩으로 확실히 처리
            decoded_query = urllib.parse.unquote_plus(query)
            
            # 3차: 특수 문자 수동 변환 (완전 보장)
            decoded_query = decoded_query.replace('%3A', ':')
            decoded_query = decoded_query.replace('%20', ' ')
            decoded_query = decoded_query.replace('%2B', '+')
            decoded_query = decoded_query.replace('%2F', '/')
            decoded_query = decoded_query.replace('%3F', '?')
            decoded_query = decoded_query.replace('%26', '&')
            decoded_query = decoded_query.replace('%3D', '=')
            
            # 4차: 한글 인코딩 문제 해결
            try:
                decoded_query = decoded_query.encode('utf-8').decode('utf-8')
            except:
                pass
            
            print(f"[DEBUG] 원본 쿼리: '{query}'")
            print(f"[DEBUG] 디코딩된 쿼리: '{decoded_query}'")
            print(f"[DEBUG] 디코딩 성공!")
            
        except Exception as e:
            print(f"[ERROR] URL 디코딩 실패: {e}")
            # 원본 쿼리에서 특수 문자만 수동 변환
            decoded_query = query.replace('%3A', ':').replace('%20', ' ')
            print(f"[DEBUG] 수동 변환된 쿼리: '{decoded_query}'")
        
        # 검색어 파싱 (brand:현대, model:아반떼, trim:1.6L 형태 처리)
        try:
            search_parts = decoded_query.split()
            brand_name = None
            model_name = None
            trim_name = None
            vehicle_line_name = None
            
            for part in search_parts:
                if part.startswith('brand:'):
                    brand_name = part.replace('brand:', '')
                elif part.startswith('model:'):
                    model_name = part.replace('model:', '')
                elif part.startswith('trim:'):
                    trim_name = part.replace('trim:', '')
                elif part.startswith('vehicle_line:'):
                    vehicle_line_name = part.replace('vehicle_line:', '')
            
            print(f"[DEBUG] 파싱된 검색어 - brand: {brand_name}, model: {model_name}, trim: {trim_name}, vehicle_line: {vehicle_line_name}")
            
        except Exception as e:
            print(f"[ERROR] 검색어 파싱 실패: {e}")
            brand_name = None
            model_name = None
            trim_name = None
            vehicle_line_name = None
        
        results = []
        
        # 1. 브랜드 검색
        try:
            if brand_name:
                # 특정 브랜드 검색
                print(f"[DEBUG] 특정 브랜드 검색: '{brand_name}'")
                brand_term = f"%{brand_name}%"
                brands = db.query(StagingBrandORM).filter(
                    StagingBrandORM.version_id == version_id,
                    StagingBrandORM.name.like(brand_term)
                ).limit(limit).all()
            else:
                # 일반 검색어로 브랜드 검색
                search_term = f"%{decoded_query}%"
                print(f"[DEBUG] 일반 브랜드 검색 - search_term: '{search_term}'")
                brands = db.query(StagingBrandORM).filter(
                    StagingBrandORM.version_id == version_id,
                    StagingBrandORM.name.like(search_term)
                ).limit(limit).all()
        except Exception as e:
            print(f"[ERROR] 브랜드 검색 실패: {e}")
            brands = []
        
        print(f"[DEBUG] 브랜드 검색 쿼리 결과: {len(brands)}개")
        for brand in brands:
            print(f"[DEBUG] 브랜드 발견: {brand.name} (ID: {brand.id})")
            results.append({
                "id": brand.id,
                "name": brand.name,
                "type": "brand",
                "match_score": 100,
                "brand_id": brand.id,
                "brand_name": brand.name
            })
        
        print(f"[DEBUG] 브랜드 검색 결과: {len(brands)}개")
        
        # 2. 모델 검색 (브랜드와 조인)
        if model_name or brand_name:
            # 특정 모델 또는 브랜드의 모델 검색
            query = db.query(StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(
                StagingBrandORM.version_id == version_id
            )
            
            if model_name:
                model_term = f"%{model_name}%"
                query = query.filter(StagingModelORM.name.like(model_term))
                print(f"[DEBUG] 특정 모델 검색: '{model_name}'")
            
            if brand_name:
                brand_term = f"%{brand_name}%"
                query = query.filter(StagingBrandORM.name.like(brand_term))
                print(f"[DEBUG] 특정 브랜드의 모델 검색: '{brand_name}'")
            
            models = query.limit(limit).all()
        else:
            # 일반 검색어로 모델 검색
            search_term = f"%{decoded_query}%"
            print(f"[DEBUG] 일반 모델 검색 - search_term: '{search_term}'")
            models = db.query(StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(
                StagingBrandORM.version_id == version_id,
                StagingModelORM.name.like(search_term)
            ).limit(limit).all()
        
        for model, brand, vehicle_line in models:
            results.append({
                "id": model.id,
                "name": model.name,
                "type": "model",
                "match_score": 80,
                "brand_id": brand.id,
                "brand_name": brand.name,
                "vehicle_line_id": vehicle_line.id,
                "vehicle_line_name": vehicle_line.name
            })
        
        print(f"[DEBUG] 모델 검색 결과: {len(models)}개")
        
        # 3. 트림 검색 (모델과 조인)
        if trim_name or model_name or brand_name:
            # 특정 트림, 모델 또는 브랜드의 트림 검색
            query = db.query(StagingTrimORM, StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
            ).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(
                StagingBrandORM.version_id == version_id
            )
            
            if trim_name:
                trim_term = f"%{trim_name}%"
                query = query.filter(StagingTrimORM.name.like(trim_term))
                print(f"[DEBUG] 특정 트림 검색: '{trim_name}'")
            
            if model_name:
                model_term = f"%{model_name}%"
                query = query.filter(StagingModelORM.name.like(model_term))
                print(f"[DEBUG] 특정 모델의 트림 검색: '{model_name}'")
            
            if brand_name:
                brand_term = f"%{brand_name}%"
                query = query.filter(StagingBrandORM.name.like(brand_term))
                print(f"[DEBUG] 특정 브랜드의 트림 검색: '{brand_name}'")
            
            trims = query.limit(limit).all()
        else:
            # 일반 검색어로 트림 검색
            search_term = f"%{decoded_query}%"
            print(f"[DEBUG] 일반 트림 검색 - search_term: '{search_term}'")
            trims = db.query(StagingTrimORM, StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
            ).join(
                StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
            ).join(
                StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
            ).filter(
                StagingBrandORM.version_id == version_id,
                StagingTrimORM.name.like(search_term)
            ).limit(limit).all()
        
        for trim, model, brand, vehicle_line in trims:
            results.append({
                "id": trim.id,
                "name": trim.name,
                "type": "trim",
                "match_score": 70,
                "model_id": model.id,
                "model_name": model.name,
                "brand_id": brand.id,
                "brand_name": brand.name,
                "vehicle_line_id": vehicle_line.id,
                "vehicle_line_name": vehicle_line.name
            })
        
        print(f"[DEBUG] 트림 검색 결과: {len(trims)}개")
        
        # 4. 옵션 검색 (트림과 조인) - 옵션은 검색하지 않음 (너무 많은 결과)
        # 옵션 검색은 제외하고 브랜드, 모델, 트림만 검색
        print(f"[DEBUG] 옵션 검색은 제외됨 (너무 많은 결과)")
        
        # 결과 정렬 (점수 높은 순)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 제한된 개수만 반환
        final_results = results[:limit]
        
        print(f"[DEBUG] 최종 검색 결과: {len(final_results)}개")
        
        # 검색 결과에 포함된 브랜드 ID들 추출
        brand_ids = set()
        for result in final_results:
            if result['type'] == 'brand':
                brand_ids.add(result['id'])
            elif result['type'] in ['model', 'trim'] and 'brand_id' in result:
                brand_ids.add(result['brand_id'])
        
        # 특정 브랜드 검색인 경우 해당 브랜드만 필터링
        if brand_name and brand_ids:
            # 특정 브랜드 검색 시 해당 브랜드만 반환
            print(f"[DEBUG] 특정 브랜드 검색 - 브랜드 ID들: {list(brand_ids)}")
            brands = db.query(StagingBrandORM).filter(
                StagingBrandORM.version_id == version_id,
                StagingBrandORM.id.in_(brand_ids)
            ).all()
        elif brand_ids:
            # 일반 검색 결과의 브랜드들
            print(f"[DEBUG] 일반 검색 결과 브랜드 ID들: {list(brand_ids)}")
            brands = db.query(StagingBrandORM).filter(
                StagingBrandORM.version_id == version_id,
                StagingBrandORM.id.in_(brand_ids)
            ).all()
        else:
            brands = []
        
        # 검색 결과에 포함된 브랜드들의 전체 데이터 조회
        brands_data = []
        if brands:
            
            # 각 브랜드의 전체 계층 구조 데이터 조회
            for brand in brands:
                brand_data = {
                    "id": brand.id,
                    "name": brand.name,
                    "vehicle_lines": []
                }
                
                # 차량라인 조회
                vehicle_lines = db.query(StagingVehicleLineORM).filter(
                    StagingVehicleLineORM.brand_id == brand.id
                ).all()
                
                for vl in vehicle_lines:
                    vl_data = {
                        "id": vl.id,
                        "name": vl.name,
                        "models": []
                    }
                    
                    # 모델 조회
                    models = db.query(StagingModelORM).filter(
                        StagingModelORM.vehicle_line_id == vl.id
                    ).all()
                    
                    for model in models:
                        model_data = {
                            "id": model.id,
                            "name": model.name,
                            "trims": []
                        }
                        
                        # 트림 조회
                        trims = db.query(StagingTrimORM).filter(
                            StagingTrimORM.model_id == model.id
                        ).all()
                        
                        for trim in trims:
                            trim_data = {
                                "id": trim.id,
                                "name": trim.name,
                                "base_price": trim.base_price,
                                "options": []
                            }
                            
                            # 옵션 조회
                            options = db.query(StagingOptionORM).filter(
                                StagingOptionORM.trim_id == trim.id
                            ).all()
                            
                            for option in options:
                                option_data = {
                                    "id": option.id,
                                    "name": option.name,
                                    "price": option.price
                                }
                                trim_data["options"].append(option_data)
                            
                            model_data["trims"].append(trim_data)
                        
                        vl_data["models"].append(model_data)
                    
                    brand_data["vehicle_lines"].append(vl_data)
                
                brands_data.append(brand_data)
        
        print(f"[DEBUG] 검색 필터링된 브랜드 데이터: {len(brands_data)}개")
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name
            },
            "query": query,
            "decoded_query": decoded_query,
            "parsed_filters": {
                "brand": brand_name,
                "model": model_name,
                "trim": trim_name,
                "vehicle_line": vehicle_line_name
            },
            "results": final_results,
            "total_count": len(final_results),
            "limit": limit,
            "brands": brands_data,  # 검색 결과에 맞는 브랜드들의 전체 데이터
            "filtered_by_search": True,
            "search_query": decoded_query  # 프론트엔드에서 사용할 검색어
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 검색 API 오류 상세:")
        print(f"[ERROR] 오류 메시지: {str(e)}")
        print(f"[ERROR] 오류 타입: {type(e)}")
        print(f"[ERROR] 스택 트레이스: {error_details}")
        print(f"[ERROR] 입력 파라미터: version_id={version_id}, query='{query}', limit={limit}")
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")


@router.get("/{version_id}/search-filtered-data")
def get_search_filtered_data(
    version_id: int,
    query: str = Query(..., description="검색어"),
    db: Session = Depends(get_db)
):
    """검색 결과에 따른 필터링된 브랜드 데이터 조회"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM,
            StagingVersionORM
        )
        from sqlalchemy import text
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # URL 디코딩
        import urllib.parse
        import logging
        logger = logging.getLogger(__name__)
        
        decoded_query = urllib.parse.unquote(query)
        logger.info(f"[DEBUG] 원본 쿼리: {query}")
        logger.info(f"[DEBUG] 디코딩된 쿼리: {decoded_query}")
        
        # 검색어 파싱 (brand:기아 형태 처리)
        search_parts = decoded_query.split()
        brand_name = None
        model_name = None
        trim_name = None
        
        for part in search_parts:
            if part.startswith('brand:'):
                brand_name = part.replace('brand:', '')
            elif part.startswith('model:'):
                model_name = part.replace('model:', '')
            elif part.startswith('trim:'):
                trim_name = part.replace('trim:', '')
        
        logger.info(f"[DEBUG] 파싱된 검색어 - brand: {brand_name}, model: {model_name}, trim: {trim_name}")
        
        # 검색 쿼리로 매칭되는 브랜드 ID들 찾기
        search_query = text("""
            SELECT DISTINCT sb.id as brand_id
            FROM staging_brand sb
            LEFT JOIN staging_vehicle_line svl ON sb.id = svl.brand_id
            LEFT JOIN staging_model sm ON svl.id = sm.vehicle_line_id
            LEFT JOIN staging_trim st ON sm.id = st.model_id
            WHERE sb.version_id = :version_id
            AND (
                (:brand_name IS NULL OR sb.name LIKE :brand_term)
                OR (:model_name IS NULL OR sm.name LIKE :model_term)
                OR (:trim_name IS NULL OR st.name LIKE :trim_term)
            )
        """)
        
        brand_term = f"%{brand_name}%" if brand_name else None
        model_term = f"%{model_name}%" if model_name else None
        trim_term = f"%{trim_name}%" if trim_name else None
        result = db.execute(search_query, {
            "version_id": version_id,
            "brand_name": brand_name,
            "model_name": model_name,
            "trim_name": trim_name,
            "brand_term": brand_term,
            "model_term": model_term,
            "trim_term": trim_term
        })
        
        matching_brand_ids = [row.brand_id for row in result.fetchall()]
        
        if not matching_brand_ids:
            return {
                "version": {
                    "id": version.id,
                    "name": version.version_name
                },
                "brands": [],
                "total_count": 0,
                "filtered_by_search": True,
                "search_query": query
            }
        
        # 매칭되는 브랜드들의 전체 데이터 조회
        brands = db.query(StagingBrandORM).filter(
            StagingBrandORM.version_id == version_id,
            StagingBrandORM.id.in_(matching_brand_ids)
        ).all()
        
        # 각 브랜드의 전체 계층 구조 데이터 조회
        result_brands = []
        for brand in brands:
            brand_data = {
                "id": brand.id,
                "name": brand.name,
                "vehicle_lines": []
            }
            
            # 차량라인 조회
            vehicle_lines = db.query(StagingVehicleLineORM).filter(
                StagingVehicleLineORM.brand_id == brand.id
            ).all()
            
            for vl in vehicle_lines:
                vl_data = {
                    "id": vl.id,
                    "name": vl.name,
                    "models": []
                }
                
                # 모델 조회
                models = db.query(StagingModelORM).filter(
                    StagingModelORM.vehicle_line_id == vl.id
                ).all()
                
                for model in models:
                    model_data = {
                        "id": model.id,
                        "name": model.name,
                        "trims": []
                    }
                    
                    # 트림 조회
                    trims = db.query(StagingTrimORM).filter(
                        StagingTrimORM.model_id == model.id
                    ).all()
                    
                    for trim in trims:
                        trim_data = {
                            "id": trim.id,
                            "name": trim.name,
                            "options": []
                        }
                        
                        # 옵션 조회
                        options = db.query(StagingOptionORM).filter(
                            StagingOptionORM.trim_id == trim.id
                        ).all()
                        
                        for option in options:
                            option_data = {
                                "id": option.id,
                                "name": option.name
                            }
                            trim_data["options"].append(option_data)
                        
                        model_data["trims"].append(trim_data)
                    
                    vl_data["models"].append(model_data)
                
                brand_data["vehicle_lines"].append(vl_data)
            
            result_brands.append(brand_data)
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name
            },
            "brands": result_brands,
            "total_count": len(result_brands),
            "filtered_by_search": True,
            "search_query": query,
            "matching_brand_ids": matching_brand_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"필터링된 데이터 조회 실패: {str(e)}")



@router.get("/search-performance-info")
def get_search_performance_info(db: Session = Depends(get_db)):
    """검색 성능 정보 조회"""
    try:
        from sqlalchemy import text
        
        # 인덱스 정보 조회
        index_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename LIKE 'staging_%'
            AND indexname LIKE '%search%'
            ORDER BY tablename, indexname
        """)
        
        result = db.execute(index_query)
        indexes = [dict(row) for row in result.fetchall()]
        
        # 테이블별 행 수 조회
        table_stats_query = text("""
            SELECT 
                'staging_brand' as table_name,
                COUNT(*) as row_count
            FROM staging_brand
            UNION ALL
            SELECT 
                'staging_vehicle_line' as table_name,
                COUNT(*) as row_count
            FROM staging_vehicle_line
            UNION ALL
            SELECT 
                'staging_model' as table_name,
                COUNT(*) as row_count
            FROM staging_model
            UNION ALL
            SELECT 
                'staging_trim' as table_name,
                COUNT(*) as row_count
            FROM staging_trim
            UNION ALL
            SELECT 
                'staging_option' as table_name,
                COUNT(*) as row_count
            FROM staging_option
        """)
        
        stats_result = db.execute(table_stats_query)
        table_stats = [dict(row) for row in stats_result.fetchall()]
        
        return {
            "indexes": indexes,
            "table_stats": table_stats,
            "total_indexes": len(indexes),
            "search_optimized": len(indexes) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 정보 조회 실패: {str(e)}")


@router.get("/{version_id}/all-data-summary")
def get_all_data_summary(
    version_id: int,
    db: Session = Depends(get_db)
):
    """버전의 전체 데이터 요약"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 각 테이블별 개수 조회
        brands_count = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).count()
        
        # 차량라인 개수 (해당 버전의 브랜드들에 속한)
        vehicle_lines_count = db.query(StagingVehicleLineORM).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).count()
        
        # 모델 개수
        models_count = db.query(StagingModelORM).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).count()
        
        # 트림 개수
        trims_count = db.query(StagingTrimORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).count()
        
        # 옵션 개수
        options_count = db.query(StagingOptionORM).join(
            StagingTrimORM, StagingOptionORM.trim_id == StagingTrimORM.id
        ).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).count()
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name,
                "description": version.description
            },
            "summary": {
                "brands": brands_count,
                "vehicle_lines": vehicle_lines_count,
                "models": models_count,
                "trims": trims_count,
                "options": options_count,
                "total_items": brands_count + vehicle_lines_count + models_count + trims_count + options_count
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 정보 조회 실패: {str(e)}")


@router.post("/{version_id}/upload-excel")
async def upload_excel_to_version(
    version_id: int,
    file: UploadFile = File(...),
    country: str = Query("KR", description="브랜드 국가"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전별 엑셀 파일 업로드 및 비동기 처리"""
    try:
        print(f"[DEBUG] Starting upload for version {version_id}")
        print(f"[DEBUG] File: {file.filename}, Country: {country}")
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        print(f"[DEBUG] Version found: {version}")
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 버전 상태 확인 (PENDING 상태만 업로드 가능)
        if version.approval_status.value != 'PENDING':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PENDING 상태의 버전만 엑셀 업로드가 가능합니다"
            )
        
        # 파일 검증
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일이 없습니다"
            )
        
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="엑셀 파일만 업로드 가능합니다 (.xlsx, .xls)"
            )
        
        # 파일 크기 검증 (10MB 제한)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일 크기는 10MB를 초과할 수 없습니다"
            )
        
        # Job 레코드 생성 (id는 자동 증가, task_id는 나중에 설정)
        print(f"[DEBUG] Creating job for version {version_id}")
        
        job = BatchJobORM(
            job_type=JobType.EXCEL_IMPORT.value,
            status=JobStatus.PENDING.value,
            task_id="",  # 임시로 빈 문자열, 나중에 Celery Task ID로 설정
            created_at=datetime.utcnow()
        )
        
        print(f"[DEBUG] Job object created: {job}")
        db.add(job)
        print(f"[DEBUG] Job added to session")
        db.commit()
        print(f"[DEBUG] Job committed to database, job.id: {job.id}")
        
        # Celery Task 실행 (job.id를 사용)
        task = process_excel_file.delay(contents, job.id, version_id, country)
        
        # Celery Task ID 업데이트
        job.task_id = task.id
        db.commit()
        print(f"[DEBUG] Celery Task ID updated: {task.id}")
        
        return {
            "success": True,
            "message": "엑셀 파일 업로드가 시작되었습니다",
            "job_id": job.id,  # 데이터베이스에서 생성된 정수 ID
            "task_id": task.id,  # Celery Task ID (UUID)
            "version_id": version_id,
            "version_name": version.version_name,
            "status": "PENDING",
            "filename": file.filename,
            "country": country
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Excel upload failed: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"엑셀 업로드 실패: {str(e)}"
        )


@router.get("/{version_id}/job-status/{job_id}")
def get_job_status(
    version_id: int,
    job_id: int,  # 정수 ID로 변경
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """작업 상태 조회"""
    try:
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # Job 상태 조회
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="작업을 찾을 수 없습니다"
            )
        
        return {
            "id": job.id,
            "status": job.status,
            "job_type": job.job_type,
            "version_id": version_id,
            "version_name": version.version_name,
            "total_rows": job.total_rows or 0,
            "processed_rows": job.processed_rows or 0,
            "error_message": job.error_message,
            "result_data": job.result_data,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작업 상태 조회 실패: {str(e)}"
        )


@router.get("/{version_id}/debug-prices")
def debug_prices(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """가격 정보 디버그용 API"""
    try:
        from app.infrastructure.orm_models import (
            StagingBrandORM, StagingVehicleLineORM, 
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 해당 버전의 모든 트림과 옵션 가격 정보 조회
        trims = db.query(StagingTrimORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).all()
        
        options = db.query(StagingOptionORM).join(
            StagingTrimORM, StagingOptionORM.trim_id == StagingTrimORM.id
        ).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(StagingBrandORM.version_id == version_id).all()
        
        trim_prices = []
        for trim in trims:
            trim_prices.append({
                "id": trim.id,
                "name": trim.name,
                "base_price": trim.base_price,
                "base_price_type": type(trim.base_price).__name__
            })
        
        option_prices = []
        for option in options:
            option_prices.append({
                "id": option.id,
                "name": option.name,
                "price": option.price,
                "price_type": type(option.price).__name__
            })
        
        return {
            "version_id": version_id,
            "version_name": version.version_name,
            "trim_count": len(trims),
            "option_count": len(options),
            "trim_prices": trim_prices[:10],  # 처음 10개만
            "option_prices": option_prices[:10]  # 처음 10개만
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] debug_prices: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가격 정보 조회 실패: {str(e)}"
        )


# ==================== CRUD API 엔드포인트들 ====================

# 브랜드 CRUD
@router.post("/{version_id}/brands")
def create_brand(
    version_id: int,
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새 브랜드 생성"""
    try:
        from app.infrastructure.orm_models import StagingBrandORM
        
        # 버전 존재 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="버전을 찾을 수 없습니다"
            )
        
        # 브랜드 생성
        new_brand = StagingBrandORM(
            version_id=version_id,
            name=brand_data.get('name'),
            country=brand_data.get('country', 'KR'),
            logo_url=brand_data.get('logo_url'),
            manager=brand_data.get('manager'),
            created_by=current_user.get('username', 'admin'),
            created_by_username=current_user.get('username', 'admin'),
            created_by_email=current_user.get('email', 'admin@example.com')
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
                "manager": new_brand.manager
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 생성 실패: {str(e)}")


@router.put("/{version_id}/brands/{brand_id}")
def update_brand(
    version_id: int,
    brand_id: int,
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 수정"""
    try:
        from app.infrastructure.orm_models import StagingBrandORM
        
        # 브랜드 조회
        brand = db.query(StagingBrandORM).filter(
            StagingBrandORM.id == brand_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
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
        
        brand.updated_by_username = current_user.get('username', 'admin')
        brand.updated_by_email = current_user.get('email', 'admin@example.com')
        
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
                "manager": brand.manager
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 수정 실패: {str(e)}")


@router.delete("/{version_id}/brands/{brand_id}")
def delete_brand(
    version_id: int,
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 삭제"""
    try:
        from app.infrastructure.orm_models import StagingBrandORM
        
        # 브랜드 조회
        brand = db.query(StagingBrandORM).filter(
            StagingBrandORM.id == brand_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="브랜드를 찾을 수 없습니다"
            )
        
        # 브랜드 삭제 (CASCADE로 관련 데이터도 함께 삭제됨)
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


# 모델 CRUD
@router.post("/{version_id}/models")
def create_model(
    version_id: int,
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새 모델 생성"""
    try:
        from app.infrastructure.orm_models import StagingModelORM
        
        # 차량 라인 존재 확인
        vehicle_line_id = model_data.get('vehicle_line_id')
        if not vehicle_line_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="차량 라인 ID가 필요합니다"
            )
        
        # 모델 생성
        new_model = StagingModelORM(
            vehicle_line_id=vehicle_line_id,
            name=model_data.get('name'),
            code=model_data.get('code'),
            release_year=model_data.get('release_year'),
            price=model_data.get('price'),
            foreign=model_data.get('foreign', False),
            created_by=current_user.get('username', 'admin'),
            created_by_username=current_user.get('username', 'admin'),
            created_by_email=current_user.get('email', 'admin@example.com')
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
                "release_year": new_model.release_year,
                "price": new_model.price,
                "foreign": new_model.foreign
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"모델 생성 실패: {str(e)}")


@router.put("/{version_id}/models/{model_id}")
def update_model(
    version_id: int,
    model_id: int,
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """모델 수정"""
    try:
        from app.infrastructure.orm_models import StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 모델 조회 (버전 확인 포함)
        model = db.query(StagingModelORM).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingModelORM.id == model_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
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
        if 'release_year' in model_data:
            model.release_year = model_data['release_year']
        if 'price' in model_data:
            model.price = model_data['price']
        if 'foreign' in model_data:
            model.foreign = model_data['foreign']
        
        model.updated_by_username = current_user.get('username', 'admin')
        model.updated_by_email = current_user.get('email', 'admin@example.com')
        
        db.commit()
        db.refresh(model)
        
        return {
            "success": True,
            "message": "모델이 성공적으로 수정되었습니다",
            "model": {
                "id": model.id,
                "name": model.name,
                "code": model.code,
                "release_year": model.release_year,
                "price": model.price,
                "foreign": model.foreign
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"모델 수정 실패: {str(e)}")


@router.delete("/{version_id}/models/{model_id}")
def delete_model(
    version_id: int,
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """모델 삭제"""
    try:
        from app.infrastructure.orm_models import StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 모델 조회 (버전 확인 포함)
        model = db.query(StagingModelORM).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingModelORM.id == model_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="모델을 찾을 수 없습니다"
            )
        
        # 모델 삭제 (CASCADE로 관련 데이터도 함께 삭제됨)
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


# 트림 CRUD
@router.post("/{version_id}/trims")
def create_trim(
    version_id: int,
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새 트림 생성"""
    try:
        from app.infrastructure.orm_models import StagingTrimORM
        
        # 모델 존재 확인
        model_id = trim_data.get('model_id')
        if not model_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="모델 ID가 필요합니다"
            )
        
        # 트림 생성
        new_trim = StagingTrimORM(
            model_id=model_id,
            name=trim_data.get('name'),
            car_type=trim_data.get('car_type'),
            fuel_name=trim_data.get('fuel_name'),
            cc=trim_data.get('cc'),
            base_price=trim_data.get('base_price'),
            description=trim_data.get('description'),
            created_by=current_user.get('username', 'admin'),
            created_by_username=current_user.get('username', 'admin'),
            created_by_email=current_user.get('email', 'admin@example.com')
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
                "description": new_trim.description
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 생성 실패: {str(e)}")


@router.put("/{version_id}/trims/{trim_id}")
def update_trim(
    version_id: int,
    trim_id: int,
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """트림 수정"""
    try:
        from app.infrastructure.orm_models import StagingTrimORM, StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 트림 조회 (버전 확인 포함)
        trim = db.query(StagingTrimORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingTrimORM.id == trim_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
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
            trim.base_price = trim_data['base_price']
        if 'description' in trim_data:
            trim.description = trim_data['description']
        
        trim.updated_by_username = current_user.get('username', 'admin')
        trim.updated_by_email = current_user.get('email', 'admin@example.com')
        
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
                "description": trim.description
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 수정 실패: {str(e)}")


@router.delete("/{version_id}/trims/{trim_id}")
def delete_trim(
    version_id: int,
    trim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """트림 삭제"""
    try:
        from app.infrastructure.orm_models import StagingTrimORM, StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 트림 조회 (버전 확인 포함)
        trim = db.query(StagingTrimORM).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingTrimORM.id == trim_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not trim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="트림을 찾을 수 없습니다"
            )
        
        # 트림 삭제 (CASCADE로 관련 데이터도 함께 삭제됨)
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


# 옵션 CRUD
@router.post("/{version_id}/options")
def create_option(
    version_id: int,
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새 옵션 생성"""
    try:
        from app.infrastructure.orm_models import StagingOptionORM
        
        # 트림 존재 확인
        trim_id = option_data.get('trim_id')
        if not trim_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="트림 ID가 필요합니다"
            )
        
        # 옵션 생성
        new_option = StagingOptionORM(
            trim_id=trim_id,
            name=option_data.get('name'),
            code=option_data.get('code'),
            description=option_data.get('description'),
            category=option_data.get('category'),
            price=option_data.get('price'),
            discounted_price=option_data.get('discounted_price'),
            created_by=current_user.get('username', 'admin'),
            created_by_username=current_user.get('username', 'admin'),
            created_by_email=current_user.get('email', 'admin@example.com')
        )
        
        db.add(new_option)
        db.commit()
        db.refresh(new_option)
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 생성되었습니다",
            "option": {
                "id": new_option.id,
                "name": new_option.name,
                "code": new_option.code,
                "description": new_option.description,
                "category": new_option.category,
                "price": new_option.price,
                "discounted_price": new_option.discounted_price
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 생성 실패: {str(e)}")


@router.put("/{version_id}/options/{option_id}")
def update_option(
    version_id: int,
    option_id: int,
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """옵션 수정"""
    try:
        from app.infrastructure.orm_models import StagingOptionORM, StagingTrimORM, StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 옵션 조회 (버전 확인 포함)
        option = db.query(StagingOptionORM).join(
            StagingTrimORM, StagingOptionORM.trim_id == StagingTrimORM.id
        ).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingOptionORM.id == option_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="옵션을 찾을 수 없습니다"
            )
        
        # 옵션 정보 업데이트
        if 'name' in option_data:
            option.name = option_data['name']
        if 'code' in option_data:
            option.code = option_data['code']
        if 'description' in option_data:
            option.description = option_data['description']
        if 'category' in option_data:
            option.category = option_data['category']
        if 'price' in option_data:
            option.price = option_data['price']
        if 'discounted_price' in option_data:
            option.discounted_price = option_data['discounted_price']
        
        option.updated_by_username = current_user.get('username', 'admin')
        option.updated_by_email = current_user.get('email', 'admin@example.com')
        
        db.commit()
        db.refresh(option)
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 수정되었습니다",
            "option": {
                "id": option.id,
                "name": option.name,
                "code": option.code,
                "description": option.description,
                "category": option.category,
                "price": option.price,
                "discounted_price": option.discounted_price
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 수정 실패: {str(e)}")


@router.delete("/{version_id}/options/{option_id}")
def delete_option(
    version_id: int,
    option_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """옵션 삭제"""
    try:
        from app.infrastructure.orm_models import StagingOptionORM, StagingTrimORM, StagingModelORM, StagingVehicleLineORM, StagingBrandORM
        
        # 옵션 조회 (버전 확인 포함)
        option = db.query(StagingOptionORM).join(
            StagingTrimORM, StagingOptionORM.trim_id == StagingTrimORM.id
        ).join(
            StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
        ).join(
            StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
        ).join(
            StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
        ).filter(
            StagingOptionORM.id == option_id,
            StagingBrandORM.version_id == version_id
        ).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="옵션을 찾을 수 없습니다"
            )
        
        # 옵션 삭제
        db.delete(option)
        db.commit()
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 삭제 실패: {str(e)}")


@router.post("/{version_id}/upload-to-main")
def upload_version_to_main(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전을 메인서버에 업로드"""
    try:
        from app.infrastructure.orm_models import (
            StagingVersionORM, StagingBrandORM, StagingVehicleLineORM,
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        # 버전 조회
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        # 승인된 버전만 푸시 가능
        if version.approval_status != ApprovalStatus.APPROVED:
            raise HTTPException(
                status_code=400, 
                detail=f"승인된 버전만 메인 DB로 푸시할 수 있습니다. 현재 상태: {version.approval_status.value}"
            )
        
        # 버전의 모든 데이터 조회
        brands = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).all()
        
        version_data = {
            "version": {
                "id": version.id,
                "version_name": version.version_name,
                "description": version.description,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "created_by": version.created_by
            },
            "brands": []
        }
        
        for brand in brands:
            # 브랜드의 모든 데이터 조회
            vehicle_lines = db.query(StagingVehicleLineORM).filter(
                StagingVehicleLineORM.brand_id == brand.id
            ).all()
            
            brand_data = {
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "logo_url": brand.logo_url,
                "manager": brand.manager,
                "vehicle_lines": []
            }
            
            for vehicle_line in vehicle_lines:
                models = db.query(StagingModelORM).filter(
                    StagingModelORM.vehicle_line_id == vehicle_line.id
                ).all()
                
                vehicle_line_data = {
                    "id": vehicle_line.id,
                    "name": vehicle_line.name,
                    "models": []
                }
                
                for model in models:
                    trims = db.query(StagingTrimORM).filter(
                        StagingTrimORM.model_id == model.id
                    ).all()
                    
                    model_data = {
                        "id": model.id,
                        "name": model.name,
                        "code": model.code,
                        "release_year": model.release_year,
                        "price": model.price,
                        "foreign": model.foreign,
                        "trims": []
                    }
                    
                    for trim in trims:
                        options = db.query(StagingOptionORM).filter(
                            StagingOptionORM.trim_id == trim.id
                        ).all()
                        
                        trim_data = {
                            "id": trim.id,
                            "name": trim.name,
                            "car_type": trim.car_type,
                            "fuel_name": trim.fuel_name,
                            "cc": trim.cc,
                            "base_price": trim.base_price,
                            "description": trim.description,
                            "options": []
                        }
                        
                        for option in options:
                            option_data = {
                                "id": option.id,
                                "name": option.name,
                                "code": option.code,
                                "price": option.price,
                                "discounted_price": option.discounted_price,
                                "category": option.category
                            }
                            trim_data["options"].append(option_data)
                        
                        model_data["trims"].append(trim_data)
                    
                    vehicle_line_data["models"].append(model_data)
                
                brand_data["vehicle_lines"].append(vehicle_line_data)
            
            version_data["brands"].append(brand_data)
        
        # 실제 메인 DB로 데이터 푸시
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM
        )
        
        # 기존 메인 DB 데이터 완전 삭제 (덮어쓰기)
        try:
            # 모든 옵션 삭제
            db.query(OptionORM).delete()
            # 모든 트림 삭제
            db.query(TrimORM).delete()
            # 모든 모델 삭제
            db.query(ModelORM).delete()
            # 모든 차량 라인 삭제
            db.query(VehicleLineORM).delete()
            # 모든 브랜드 삭제
            db.query(BrandORM).delete()
            
            db.flush()  # 삭제 작업 커밋
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"기존 메인 DB 삭제 실패: {str(e)}")
        
        pushed_counts = {
            "brands": 0,
            "vehicle_lines": 0,
            "models": 0,
            "trims": 0,
            "options": 0
        }
        
        # 트랜잭션으로 안전하게 처리
        try:
            for brand_data in version_data["brands"]:
                # 새 브랜드 생성 (기존 데이터는 이미 삭제됨)
                brand = BrandORM(
                    name=brand_data["name"],
                    country=brand_data["country"],
                    logo_url=brand_data["logo_url"],
                    manager=brand_data["manager"]
                )
                db.add(brand)
                
                db.flush()  # ID 생성
                pushed_counts["brands"] += 1
                
                # 차량 라인 처리
                for vehicle_line_data in brand_data["vehicle_lines"]:
                    vehicle_line = VehicleLineORM(
                        name=vehicle_line_data["name"],
                        brand_id=brand.id
                    )
                    db.add(vehicle_line)
                    
                    db.flush()
                    pushed_counts["vehicle_lines"] += 1
                    
                    # 모델 처리
                    for model_data in vehicle_line_data["models"]:
                        model = ModelORM(
                            name=model_data["name"],
                            code=model_data["code"],
                            vehicle_line_id=vehicle_line.id,
                            release_year=model_data["release_year"],
                            price=model_data["price"],
                            foreign=model_data["foreign"]
                        )
                        db.add(model)
                        
                        db.flush()
                        pushed_counts["models"] += 1
                        
                        # 트림 처리
                        for trim_data in model_data["trims"]:
                            trim = TrimORM(
                                name=trim_data["name"],
                                car_type=trim_data["car_type"],
                                fuel_name=trim_data["fuel_name"],
                                cc=trim_data["cc"],
                                base_price=trim_data["base_price"],
                                description=trim_data["description"],
                                model_id=model.id
                            )
                            db.add(trim)
                            
                            db.flush()
                            pushed_counts["trims"] += 1
                            
                            # 옵션 처리
                            for option_data in trim_data["options"]:
                                if option_data["price"]:
                                    option = OptionORM(
                                        name=option_data.get("name", ""),
                                        code=option_data.get("code"),
                                        description=option_data.get("description"),
                                        price=option_data["price"],
                                        discounted_price=option_data.get("discounted_price"),
                                        category=option_data.get("category"),
                                        trim_id=trim.id
                                    )
                                    db.add(option)
                                    pushed_counts["options"] += 1
            
            db.commit()
            
            return {
                "message": f"버전 '{version.version_name}'이 메인 DB에 성공적으로 푸시되었습니다.",
                "version_id": version_id,
                "uploaded_at": datetime.now().isoformat(),
                "pushed_data": pushed_counts
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"메인 DB 푸시 실패: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메인서버 업로드 실패: {str(e)}")


@router.post("/{version_id}/download-from-main")
def download_version_from_main(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """메인서버에서 버전으로 다운로드"""
    try:
        from app.infrastructure.orm_models import StagingVersionORM
        
        # 버전 조회
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        # 실제 메인 DB에서 데이터 풀
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM,
            StagingBrandORM, StagingVehicleLineORM, StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        
        pulled_counts = {
            "brands": 0,
            "vehicle_lines": 0,
            "models": 0,
            "trims": 0,
            "options": 0
        }
        
        # 트랜잭션으로 안전하게 처리
        try:
            # 버전 상태를 PENDING으로 변경 (승인 대기 상태)
            from app.domain.entities import ApprovalStatus
            version.approval_status = ApprovalStatus.PENDING
            version.approved_by = None
            version.approved_at = None
            version.rejected_by = None
            version.rejected_at = None
            version.rejection_reason = None
            
            # 기존 버전의 모든 데이터 삭제 (단계별로 안전하게 삭제)
            # 1. 브랜드 조회 후 관련 데이터 삭제
            staging_brands = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).all()
            
            for brand in staging_brands:
                # 브랜드의 모든 차량 라인 조회 후 삭제
                vehicle_lines = db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.brand_id == brand.id).all()
                for vehicle_line in vehicle_lines:
                    # 차량 라인의 모든 모델 조회 후 삭제
                    models = db.query(StagingModelORM).filter(StagingModelORM.vehicle_line_id == vehicle_line.id).all()
                    for model in models:
                        # 모델의 모든 트림 조회 후 삭제
                        trims = db.query(StagingTrimORM).filter(StagingTrimORM.model_id == model.id).all()
                        for trim in trims:
                            # 트림의 모든 옵션 삭제
                            db.query(StagingOptionORM).filter(StagingOptionORM.trim_id == trim.id).delete()
                            # 트림 삭제
                            db.delete(trim)
                        # 모델 삭제
                        db.delete(model)
                    # 차량 라인 삭제
                    db.delete(vehicle_line)
                # 브랜드 삭제
                db.delete(brand)
            
            # 메인 DB에서 모든 데이터 조회
            main_brands = db.query(BrandORM).all()
            
            for main_brand in main_brands:
                # Staging 브랜드 생성
                staging_brand = StagingBrandORM(
                    name=main_brand.name,
                    country=main_brand.country,
                    logo_url=main_brand.logo_url,
                    manager=main_brand.manager,
                    version_id=version_id,
                    created_by=current_user.get('username', 'admin'),
                    created_by_email=current_user.get('email', 'admin@example.com')
                )
                db.add(staging_brand)
                db.flush()
                pulled_counts["brands"] += 1
                
                # 차량 라인 처리
                for main_vehicle_line in main_brand.vehicle_lines:
                    staging_vehicle_line = StagingVehicleLineORM(
                        name=main_vehicle_line.name,
                        brand_id=staging_brand.id,
                        created_by=current_user.get('username', 'admin'),
                        created_by_email=current_user.get('email', 'admin@example.com')
                    )
                    db.add(staging_vehicle_line)
                    db.flush()
                    pulled_counts["vehicle_lines"] += 1
                    
                    # 모델 처리
                    for main_model in main_vehicle_line.models:
                        staging_model = StagingModelORM(
                            name=main_model.name,
                            code=main_model.code,
                            vehicle_line_id=staging_vehicle_line.id,
                            release_year=main_model.release_year,
                            price=main_model.price,
                            foreign=main_model.foreign,
                            created_by=current_user.get('username', 'admin'),
                            created_by_email=current_user.get('email', 'admin@example.com')
                        )
                        db.add(staging_model)
                        db.flush()
                        pulled_counts["models"] += 1
                        
                        # 트림 처리
                        for main_trim in main_model.trims:
                            staging_trim = StagingTrimORM(
                                name=main_trim.name,
                                car_type=main_trim.car_type,
                                fuel_name=main_trim.fuel_name,
                                cc=main_trim.cc,
                                base_price=main_trim.base_price,
                                description=main_trim.description,
                                model_id=staging_model.id,
                                created_by=current_user.get('username', 'admin'),
                                created_by_email=current_user.get('email', 'admin@example.com')
                            )
                            db.add(staging_trim)
                            db.flush()
                            pulled_counts["trims"] += 1
                            
                            # 옵션 처리
                            for main_option_title in main_trim.option_titles:
                                staging_option = StagingOptionORM(
                                    name=main_option_title.name,
                                    code=main_option_title.name,  # 코드가 없으면 이름 사용
                                    trim_id=staging_trim.id,
                                    created_by=current_user.get('username', 'admin'),
                                    created_by_email=current_user.get('email', 'admin@example.com')
                                )
                                db.add(staging_option)
                                
                                # 옵션 가격 처리
                                if main_option_title.option_prices:
                                    main_price = main_option_title.option_prices[0]  # 첫 번째 가격 사용
                                    staging_option.price = main_price.price
                                    staging_option.discounted_price = main_price.discounted_price
                                
                                pulled_counts["options"] += 1
            
            db.commit()
            
            return {
                "message": f"메인 DB에서 버전 '{version.version_name}'으로 데이터가 성공적으로 풀되었습니다.",
                "version_id": version_id,
                "downloaded_at": datetime.now().isoformat(),
                "pulled_data": pulled_counts
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"메인 DB 풀 실패: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메인서버 다운로드 실패: {str(e)}")


@router.get("/navigation")
def get_version_navigation(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """버전 네비게이션 정보 조회"""
    try:
        from app.infrastructure.orm_models import StagingVersionORM
        
        # 모든 버전 조회 (최신순)
        versions = db.query(StagingVersionORM).order_by(
            StagingVersionORM.created_at.desc()
        ).all()
        
        navigation_data = {
            "current_version": None,
            "available_versions": [],
            "main_server_status": "connected"  # TODO: 실제 메인서버 연결 상태 확인
        }
        
        for version in versions:
            version_info = {
                "id": version.id,
                "version_name": version.version_name,
                "description": version.description,
                "status": version.approval_status,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "created_by": version.created_by,
                "is_active": version.approval_status == "MIGRATED"  # 마이그레이션된 버전이 활성 버전
            }
            
            navigation_data["available_versions"].append(version_info)
            
            # 현재 활성 버전 설정
            if version.approval_status == "MIGRATED" and not navigation_data["current_version"]:
                navigation_data["current_version"] = version_info
        
        return navigation_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 네비게이션 조회 실패: {str(e)}")


@router.post("/{version_id}/approve")
def approve_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """버전 승인 (관리자, 매니저, 대표만 가능)"""
    try:
        from app.infrastructure.orm_models import (
            StagingVersionORM, StagingBrandORM, StagingVehicleLineORM,
            StagingModelORM, StagingTrimORM, StagingOptionORM
        )
        from app.domain.entities import ApprovalStatus
        from app.presentation.permission_checker import check_user_permission
        
        # 권한 체크: 관리자, 매니저, 대표만 승인 가능
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        user_position = current_user.position.value if hasattr(current_user.position, 'value') else current_user.position
        
        if not (user_role == 'ADMIN' or user_position in ['MANAGER', 'CEO']):
            raise HTTPException(
                status_code=403, 
                detail="승인 권한이 없습니다. 관리자, 매니저, 대표만 승인할 수 있습니다."
            )
        
        # 버전 조회
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        # 이미 승인된 버전인지 확인
        if version.approval_status == ApprovalStatus.APPROVED:
            raise HTTPException(status_code=400, detail="이미 승인된 버전입니다.")
        
        # 버전 승인 처리
        version.approval_status = ApprovalStatus.APPROVED
        version.approved_by = current_user.username if hasattr(current_user, 'username') else 'admin'
        version.approved_at = datetime.now()
        version.rejected_by = None
        version.rejected_at = None
        version.rejection_reason = None
        
        db.commit()
        
        # 승인 후 자동으로 메인 DB로 푸시
        try:
            # 버전의 모든 데이터 조회
            brands = db.query(StagingBrandORM).filter(StagingBrandORM.version_id == version_id).all()
            
            version_data = {
                "version": {
                    "id": version.id,
                    "version_name": version.version_name,
                    "description": version.description,
                    "created_at": version.created_at.isoformat() if version.created_at else None,
                    "created_by": version.created_by
                },
                "brands": []
            }
            
            for brand in brands:
                brand_data = {
                    "name": brand.name,
                    "country": brand.country,
                    "logo_url": brand.logo_url,
                    "manager": brand.manager,
                    "vehicle_lines": []
                }
                
                # 차량 라인 조회
                vehicle_lines = db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.brand_id == brand.id).all()
                for vehicle_line in vehicle_lines:
                    vehicle_line_data = {
                        "name": vehicle_line.name,
                        "models": []
                    }
                    
                    # 모델 조회
                    models = db.query(StagingModelORM).filter(StagingModelORM.vehicle_line_id == vehicle_line.id).all()
                    for model in models:
                        model_data = {
                            "name": model.name,
                            "code": model.code,
                            "release_year": model.release_year,
                            "price": model.price,
                            "foreign": model.foreign,
                            "trims": []
                        }
                        
                        # 트림 조회
                        trims = db.query(StagingTrimORM).filter(StagingTrimORM.model_id == model.id).all()
                        for trim in trims:
                            trim_data = {
                                "name": trim.name,
                                "car_type": trim.car_type,
                                "fuel_name": trim.fuel_name,
                                "cc": trim.cc,
                                "base_price": trim.base_price,
                                "description": trim.description,
                                "options": []
                            }
                            
                            # 옵션 조회
                            options = db.query(StagingOptionORM).filter(StagingOptionORM.trim_id == trim.id).all()
                            for option in options:
                                option_data = {
                                    "name": option.name,
                                    "price": option.price,
                                    "discounted_price": option.discounted_price
                                }
                                trim_data["options"].append(option_data)
                            
                            model_data["trims"].append(trim_data)
                        
                        vehicle_line_data["models"].append(model_data)
                    
                    brand_data["vehicle_lines"].append(vehicle_line_data)
                
                version_data["brands"].append(brand_data)
            
            # 메인 DB로 푸시
            from app.infrastructure.orm_models import (
                BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM
            )
            
            # 기존 메인 DB 데이터 완전 삭제 (덮어쓰기)
            db.query(OptionORM).delete()
            db.query(TrimORM).delete()
            db.query(ModelORM).delete()
            db.query(VehicleLineORM).delete()
            db.query(BrandORM).delete()
            db.flush()
            
            pushed_counts = {
                "brands": 0,
                "vehicle_lines": 0,
                "models": 0,
                "trims": 0,
                "options": 0
            }
            
            # 새 데이터 추가
            for brand_data in version_data["brands"]:
                brand = BrandORM(
                    name=brand_data["name"],
                    country=brand_data["country"],
                    logo_url=brand_data["logo_url"],
                    manager=brand_data["manager"]
                )
                db.add(brand)
                db.flush()
                pushed_counts["brands"] += 1
                
                # 차량 라인 처리
                for vehicle_line_data in brand_data["vehicle_lines"]:
                    vehicle_line = VehicleLineORM(
                        name=vehicle_line_data["name"],
                        brand_id=brand.id
                    )
                    db.add(vehicle_line)
                    db.flush()
                    pushed_counts["vehicle_lines"] += 1
                    
                    # 모델 처리
                    for model_data in vehicle_line_data["models"]:
                        model = ModelORM(
                            name=model_data["name"],
                            code=model_data["code"],
                            vehicle_line_id=vehicle_line.id,
                            release_year=model_data["release_year"],
                            price=model_data["price"],
                            foreign=model_data["foreign"]
                        )
                        db.add(model)
                        db.flush()
                        pushed_counts["models"] += 1
                        
                        # 트림 처리
                        for trim_data in model_data["trims"]:
                            trim = TrimORM(
                                name=trim_data["name"],
                                car_type=trim_data["car_type"],
                                fuel_name=trim_data["fuel_name"],
                                cc=trim_data["cc"],
                                base_price=trim_data["base_price"],
                                description=trim_data["description"],
                                model_id=model.id
                            )
                            db.add(trim)
                            db.flush()
                            pushed_counts["trims"] += 1
                            
                            # 옵션 처리
                            for option_data in trim_data["options"]:
                                if option_data["price"]:
                                    option = OptionORM(
                                        name=option_data.get("name", ""),
                                        code=option_data.get("code"),
                                        description=option_data.get("description"),
                                        price=option_data["price"],
                                        discounted_price=option_data.get("discounted_price"),
                                        category=option_data.get("category"),
                                        trim_id=trim.id
                                    )
                                    db.add(option)
                                    pushed_counts["options"] += 1
            
            db.commit()
            
            return {
                "message": f"버전 '{version.version_name}'이 승인되었고 메인 DB에 성공적으로 푸시되었습니다.",
                "version_id": version_id,
                "approved_by": version.approved_by,
                "approved_at": version.approved_at.isoformat(),
                "status": "APPROVED",
                "pushed_data": pushed_counts
            }
            
        except Exception as push_error:
            db.rollback()
            # 승인은 완료되었지만 푸시 실패
            return {
                "message": f"버전 '{version.version_name}'이 승인되었지만 메인 DB 푸시에 실패했습니다.",
                "version_id": version_id,
                "approved_by": version.approved_by,
                "approved_at": version.approved_at.isoformat(),
                "status": "APPROVED",
                "push_error": str(push_error)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 승인 실패: {str(e)}")


@router.post("/{version_id}/reject")
def reject_version(
    version_id: int,
    rejection_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """버전 거부 (관리자, 매니저, 대표만 가능)"""
    try:
        from app.infrastructure.orm_models import StagingVersionORM
        from app.domain.entities import ApprovalStatus
        
        # 권한 체크: 관리자, 매니저, 대표만 거부 가능
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        user_position = current_user.position.value if hasattr(current_user.position, 'value') else current_user.position
        
        if not (user_role == 'ADMIN' or user_position in ['MANAGER', 'CEO']):
            raise HTTPException(
                status_code=403, 
                detail="거부 권한이 없습니다. 관리자, 매니저, 대표만 거부할 수 있습니다."
            )
        
        # 버전 조회
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        # 이미 거부된 버전인지 확인
        if version.approval_status == ApprovalStatus.REJECTED:
            raise HTTPException(status_code=400, detail="이미 거부된 버전입니다.")
        
        # 거부 사유 추출
        rejection_reason = rejection_data.get('reason', '거부 사유가 제공되지 않았습니다.')
        
        # 버전 거부 처리
        version.approval_status = ApprovalStatus.REJECTED
        version.rejected_by = current_user.username if hasattr(current_user, 'username') else 'admin'
        version.rejected_at = datetime.now()
        version.rejection_reason = rejection_reason
        version.approved_by = None
        version.approved_at = None
        
        db.commit()
        
        return {
            "message": f"버전 '{version.version_name}'이 거부되었습니다.",
            "version_id": version_id,
            "rejected_by": version.rejected_by,
            "rejected_at": version.rejected_at.isoformat(),
            "rejection_reason": rejection_reason,
            "status": "REJECTED"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 거부 실패: {str(e)}")


@router.post("/switch-version/{version_id}")
def switch_to_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """특정 버전으로 전환"""
    try:
        from app.infrastructure.orm_models import StagingVersionORM
        
        # 버전 조회
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        # TODO: 실제 버전 전환 로직 구현
        # 여기서는 시뮬레이션으로 성공 응답 반환
        
        return {
            "message": f"버전 '{version.version_name}'으로 성공적으로 전환되었습니다.",
            "version_id": version_id,
            "switched_at": datetime.now().isoformat(),
            "new_version": {
                "id": version.id,
                "version_name": version.version_name,
                "description": version.description,
                "status": version.approval_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 전환 실패: {str(e)}")


@router.get("/main-db/status")
def get_main_db_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """메인 DB 현황 조회"""
    try:
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionTitleORM
        )
        
        # 메인 DB 통계 조회
        brands_count = db.query(BrandORM).count()
        vehicle_lines_count = db.query(VehicleLineORM).count()
        models_count = db.query(ModelORM).count()
        trims_count = db.query(TrimORM).count()
        options_count = db.query(OptionTitleORM).count()
        
        # 브랜드별 상세 정보 조회
        brands = db.query(BrandORM).all()
        brands_data = []
        
        for brand in brands:
            vehicle_lines = db.query(VehicleLineORM).filter(VehicleLineORM.brand_id == brand.id).all()
            models_count_for_brand = 0
            
            for vehicle_line in vehicle_lines:
                models_count_for_brand += db.query(ModelORM).filter(ModelORM.vehicle_line_id == vehicle_line.id).count()
            
            brands_data.append({
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "manager": brand.manager,
                "vehicle_lines_count": len(vehicle_lines),
                "models_count": models_count_for_brand
            })
        
        # 데이터가 없는 경우 빈 상태 응답
        if brands_count == 0:
            return {
                "stats": {
                    "brands": 0,
                    "vehicle_lines": 0,
                    "models": 0,
                    "trims": 0,
                    "options": 0
                },
                "brands": [],
                "last_updated": datetime.now().isoformat(),
                "database_status": "connected",
                "is_empty": True,
                "message": "메인 DB에 데이터가 없습니다."
            }
        
        return {
            "stats": {
                "brands": brands_count,
                "vehicle_lines": vehicle_lines_count,
                "models": models_count,
                "trims": trims_count,
                "options": options_count
            },
            "brands": brands_data,
            "last_updated": datetime.now().isoformat(),
            "database_status": "connected",
            "is_empty": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메인 DB 현황 조회 실패: {str(e)}")