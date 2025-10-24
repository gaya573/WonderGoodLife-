# 할인 정책 시스템 수정 사항

## 🚨 현재 문제 상황

### 1. API 엔드포인트 누락 (404 오류)
**문제**: `GET /api/versions/{version_id}/brands/{brand_id}/vehicle-lines/{vehicle_line_id}/trims` 엔드포인트가 없음

**에러 로그**:
```
INFO: GET /api/versions/5/brands/26/vehicle-lines/401/trims HTTP/1.1" 404 Not Found
INFO: GET /api/versions/5/brands/26/vehicle-lines/400/trims HTTP/1.1" 404 Not Found
```

**원인**: `versions.py` 파일에 해당 함수가 구현되지 않음

### 2. policies.py에서 vehicle_line_id 누락
**문제**: `get_discount_policy` 함수의 응답에 `vehicle_line_id`가 포함되지 않음

**위치**: `batch-service-fastapi/app/presentation/api/discount/policies.py` 81-92줄

---

## 📝 수정 필요 사항

### 1. versions.py 파일 수정

**파일 위치**: `batch-service-fastapi/app/presentation/api/staging/versions.py`

**추가 위치**: 845줄 (빈 줄에 추가)

**추가할 코드**:
```python
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
            "brand_id": brand_id,
            "brand_name": brand.name,
            "vehicle_line_id": vehicle_line_id,
            "vehicle_line_name": vehicle_line.name,
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
```

### 2. policies.py 파일 수정

**파일 위치**: `batch-service-fastapi/app/presentation/api/discount/policies.py`

**수정 위치**: 81-92줄의 `get_discount_policy` 함수

**현재 코드**:
```python
@router.get("/policies/{policy_id}", response_model=DiscountPolicyResponse)
async def get_discount_policy(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 단일 조회"""
    policy = await service.get_discount_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
    
    return DiscountPolicyResponse(
        id=policy.id,
        brand_id=policy.brand_id,
        trim_id=policy.trim_id,  # vehicle_line_id 누락
        version_id=policy.version_id,
        policy_type=policy.policy_type,
        title=policy.title,
        description=policy.description,
        valid_from=policy.valid_from,
        valid_to=policy.valid_to,
        is_active=policy.is_active
    )
```

**수정 후 코드**:
```python
@router.get("/policies/{policy_id}", response_model=DiscountPolicyResponse)
async def get_discount_policy(
    policy_id: int,
    current_user: User = Depends(get_current_active_user),
    service: DiscountPolicyService = Depends(get_discount_policy_service)
):
    """할인 정책 단일 조회"""
    policy = await service.get_discount_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할인 정책을 찾을 수 없습니다")
    
    return DiscountPolicyResponse(
        id=policy.id,
        brand_id=policy.brand_id,
        vehicle_line_id=policy.vehicle_line_id,  # 추가됨
        trim_id=policy.trim_id,
        version_id=policy.version_id,
        policy_type=policy.policy_type,
        title=policy.title,
        description=policy.description,
        valid_from=policy.valid_from,
        valid_to=policy.valid_to,
        is_active=policy.is_active
    )
```

**또한 수정해야 할 부분**:
- 126-137줄: `get_discount_policies` 함수의 응답에도 `vehicle_line_id` 추가
- 165-176줄: `update_discount_policy` 함수의 응답에도 `vehicle_line_id` 추가

---

## ✅ 수정 완료 후 확인 사항

1. 백엔드 서버 재시작 확인
2. API 엔드포인트 테스트
   ```bash
   curl http://localhost:8000/api/versions/5/brands/26/vehicle-lines/401/trims
   ```
3. 프론트엔드에서 브랜드 → Vehicle Line → 트림 선택이 정상 작동하는지 확인

---

## 📌 참고 사항

- Vehicle Line은 Brand와 Trim 사이의 중간 계층입니다
- 할인 정책은 Brand → Vehicle Line → Trim 계층 구조를 따릅니다
- 기존 `get_brand_trims` API는 브랜드의 모든 트림을 반환하지만, 새로운 API는 특정 Vehicle Line의 트림만 반환합니다

