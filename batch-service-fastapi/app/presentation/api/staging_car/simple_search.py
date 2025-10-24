"""
간단한 검색 API - 안정적인 버전
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import urllib.parse

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import (
    StagingBrandORM, StagingVehicleLineORM, 
    StagingModelORM, StagingTrimORM, StagingOptionORM,
    StagingVersionORM
)

router = APIRouter(prefix="/api/versions", tags=["simple-search"])


@router.get("/{version_id}/simple-search")
def simple_search(
    version_id: int,
    query: str = Query(..., description="검색어"),
    limit: int = Query(20, description="검색 결과 개수 제한"),
    db: Session = Depends(get_db)
):
    """간단한 검색 API - 안정적인 버전"""
    try:
        print(f"[DEBUG] 간단한 검색 시작 - version_id: {version_id}, query: '{query}'")
        
        # 버전 존재 확인
        version = db.query(StagingVersionORM).filter(StagingVersionORM.id == version_id).first()
        if not version:
            raise HTTPException(
                status_code=404,
                detail="버전을 찾을 수 없습니다"
            )
        
        # URL 디코딩
        try:
            decoded_query = urllib.parse.unquote_plus(query)
            # 특수 문자 수동 변환
            decoded_query = decoded_query.replace('%3A', ':')
            decoded_query = decoded_query.replace('%20', ' ')
            print(f"[DEBUG] 디코딩된 쿼리: '{decoded_query}'")
        except Exception as e:
            print(f"[ERROR] URL 디코딩 실패: {e}")
            decoded_query = query
        
        # 검색어 파싱 (복합 검색 지원)
        brand_name = None
        model_name = None
        trim_name = None
        general_search_terms = []
        
        # 공백으로 분리하여 각 부분 처리
        search_parts = decoded_query.split()
        
        for part in search_parts:
            if ':' in part:
                # 타입 지정 검색 (brand:기아, model:레이 등)
                type_parts = part.split(':')
                if len(type_parts) >= 2:
                    search_type = type_parts[0].lower()
                    search_value = type_parts[1].strip()
                    
                    if search_type == 'brand':
                        brand_name = search_value
                        print(f"[DEBUG] 브랜드 검색: '{brand_name}'")
                    elif search_type == 'model':
                        model_name = search_value
                        print(f"[DEBUG] 모델 검색: '{model_name}'")
                    elif search_type == 'trim':
                        trim_name = search_value
                        print(f"[DEBUG] 트림 검색: '{trim_name}'")
            else:
                # 일반 검색어 (EV, 전기 등)
                general_search_terms.append(part)
                print(f"[DEBUG] 일반 검색어: '{part}'")
        
        print(f"[DEBUG] 파싱된 검색어 - brand: {brand_name}, model: {model_name}, trim: {trim_name}, 일반: {general_search_terms}")
        
        results = []
        
        # 간단한 검색 로직 - 모든 검색어를 하나의 문자열로 합쳐서 검색
        if brand_name or model_name or trim_name or general_search_terms:
            # 모든 검색어를 하나로 합치기
            all_search_terms = []
            if brand_name:
                all_search_terms.append(brand_name)
            if model_name:
                all_search_terms.append(model_name)
            if trim_name:
                all_search_terms.append(trim_name)
            if general_search_terms:
                all_search_terms.extend(general_search_terms)
            
            # 중복 제거를 위한 Set 사용
            seen_model_ids = set()
            
            # 각 검색어로 모델 검색
            for search_term in all_search_terms:
                print(f"[DEBUG] 검색어로 모델 검색: '{search_term}'")
                
                # 모델 검색 (브랜드와 조인)
                models = db.query(StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                    StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
                ).join(
                    StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
                ).filter(
                    StagingBrandORM.version_id == version_id,
                    StagingModelORM.name.like(f"%{search_term}%")
                ).limit(limit).all()
                
                for model, brand, vehicle_line in models:
                    # 중복 제거 (Set 사용)
                    if model.id not in seen_model_ids:
                        seen_model_ids.add(model.id)
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
                        print(f"[DEBUG] 모델 추가: {model.name} (ID: {model.id})")
                
                # 트림 검색 (모델과 조인)
                trims = db.query(StagingTrimORM, StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                    StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
                ).join(
                    StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
                ).join(
                    StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
                ).filter(
                    StagingBrandORM.version_id == version_id,
                    StagingTrimORM.name.like(f"%{search_term}%")
                ).limit(limit).all()
                
                for trim, model, brand, vehicle_line in trims:
                    # 중복 제거 (Set 사용)
                    if model.id not in seen_model_ids:
                        seen_model_ids.add(model.id)
                        results.append({
                            "id": model.id,
                            "name": model.name,
                            "type": "model",
                            "match_score": 70,
                            "brand_id": brand.id,
                            "brand_name": brand.name,
                            "vehicle_line_id": vehicle_line.id,
                            "vehicle_line_name": vehicle_line.name
                        })
                        print(f"[DEBUG] 트림에서 모델 추가: {model.name} (ID: {model.id})")
        
        else:
            # 일반 검색 - 브랜드, 모델, 트림 모두 검색
            search_term = f"%{decoded_query}%"
            
            # 브랜드 검색
            brands = db.query(StagingBrandORM).filter(
                StagingBrandORM.version_id == version_id,
                StagingBrandORM.name.like(search_term)
            ).limit(limit).all()
            
            for brand in brands:
                results.append({
                    "id": brand.id,
                    "name": brand.name,
                    "type": "brand",
                    "match_score": 100,
                    "brand_id": brand.id,
                    "brand_name": brand.name
                })
            
            # 모델 검색 (브랜드와 조인)
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
            
            # 트림 검색 (모델과 조인)
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
        
        print(f"[DEBUG] 검색 결과: {len(results)}개")
        
        # 검색 결과에 맞는 모델 중심 데이터 조회
        models_data = []
        if results:
            # 검색 결과에서 관련된 브랜드 ID들 추출
            brand_ids = set()
            model_ids = set()
            
            for result in results:
                if result['type'] == 'brand':
                    brand_ids.add(result['id'])
                elif result['type'] == 'model':
                    brand_ids.add(result['brand_id'])
                    model_ids.add(result['id'])
                elif result['type'] == 'trim':
                    brand_ids.add(result['brand_id'])
                    model_ids.add(result['model_id'])
            
            # 관련된 모델들 조회 (모델 중심)
            if model_ids:
                models = db.query(StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                    StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
                ).join(
                    StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
                ).filter(
                    StagingModelORM.id.in_(model_ids)
                ).all()
                
                for model, brand, vehicle_line in models:
                    model_data = {
                        "id": model.id,
                        "name": model.name,
                        "code": model.code,
                        "price": model.price,
                        "foreign": model.foreign,
                        "brand_id": brand.id,
                        "brand_name": brand.name,
                        "vehicle_line_id": vehicle_line.id,
                        "vehicle_line_name": vehicle_line.name,
                        "trims": []
                    }
                    
                    # 해당 모델의 트림들 조회
                    trims = db.query(StagingTrimORM).filter(
                        StagingTrimORM.model_id == model.id
                    ).all()
                    
                    for trim in trims:
                        trim_data = {
                            "id": trim.id,
                            "name": trim.name,
                            "base_price": trim.base_price,
                            "car_type": trim.car_type,
                            "fuel_name": trim.fuel_name,
                            "cc": trim.cc,
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
                    
                    models_data.append(model_data)
            
            # 브랜드만 검색된 경우 해당 브랜드의 모든 모델 조회
            elif brand_ids:
                models = db.query(StagingModelORM, StagingBrandORM, StagingVehicleLineORM).join(
                    StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
                ).join(
                    StagingBrandORM, StagingVehicleLineORM.brand_id == StagingBrandORM.id
                ).filter(
                    StagingBrandORM.id.in_(brand_ids)
                ).all()
                
                for model, brand, vehicle_line in models:
                    model_data = {
                        "id": model.id,
                        "name": model.name,
                        "code": model.code,
                        "price": model.price,
                        "foreign": model.foreign,
                        "brand_id": brand.id,
                        "brand_name": brand.name,
                        "vehicle_line_id": vehicle_line.id,
                        "vehicle_line_name": vehicle_line.name,
                        "trims": []
                    }
                    
                    # 해당 모델의 트림들 조회
                    trims = db.query(StagingTrimORM).filter(
                        StagingTrimORM.model_id == model.id
                    ).all()
                    
                    for trim in trims:
                        trim_data = {
                            "id": trim.id,
                            "name": trim.name,
                            "base_price": trim.base_price,
                            "car_type": trim.car_type,
                            "fuel_name": trim.fuel_name,
                            "cc": trim.cc,
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
                    
                    models_data.append(model_data)
        
        return {
            "version": {
                "id": version.id,
                "name": version.version_name
            },
            "query": query,
            "decoded_query": decoded_query,
            "results": results,
            "total_count": len(results),
            "limit": limit,
            "models": models_data,  # 모델 중심으로 변경
            "filtered_by_search": True,
            "search_query": decoded_query
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 간단한 검색 API 오류:")
        print(f"[ERROR] 오류 메시지: {str(e)}")
        print(f"[ERROR] 스택 트레이스: {error_details}")
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")
