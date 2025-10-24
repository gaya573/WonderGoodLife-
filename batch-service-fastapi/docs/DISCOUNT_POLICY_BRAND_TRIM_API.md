# 할인 정책 추가 시 브랜드/트림 선택 API 문서

## 문제점
현재 할인 정책 추가 페이지에서 브랜드/트림 선택 드롭다운이 비어있음. 버전의 브랜드와 트림 목록을 가져오는 API가 필요함.

## 기존 API 엔드포인트

### 1. 브랜드 요약 API (추천)
**엔드포인트**: `GET /api/versions/{version_id}/brands-summary`

**설명**: 버전의 모든 브랜드 목록을 간단하게 조회

**응답 예시**:
```json
{
  "version": {
    "id": 1,
    "name": "v1.0.0",
    "description": "첫 번째 버전"
  },
  "brands": [
    {
      "id": 1,
      "name": "현대",
      "country": "KR",
      "manager": "김철수",
      "created_at": "2025-01-01T00:00:00"
    },
    {
      "id": 2,
      "name": "기아",
      "country": "KR",
      "manager": "이영희",
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "total_brands": 2
}
```

**장점**: 
- 빠른 응답 속도
- 간단한 구조
- 브랜드 목록만 필요한 경우에 적합

**단점**:
- 트림 정보가 포함되지 않음

---

### 2. 브랜드 전체 데이터 API (현재 사용 중)
**엔드포인트**: `GET /api/versions/{version_id}/brands-with-full-data`

**설명**: 브랜드, 모델, 트림, 옵션을 포함한 전체 데이터 조회

**파라미터**:
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 브랜드 수 (기본값: 10, 최대: 50)
- `brand_name`: 브랜드명 필터 (선택)

**응답 예시**:
```json
{
  "version": {
    "id": 1,
    "name": "v1.0.0",
    "description": "첫 번째 버전"
  },
  "brands": [
    {
      "id": 1,
      "name": "현대",
      "country": "KR",
      "manager": "김철수",
      "vehicle_lines": [
        {
          "id": 1,
          "name": "승용차",
          "models": [
            {
              "id": 1,
              "name": "소나타",
              "code": "SONATA",
              "trims": [
                {
                  "id": 1,
                  "name": "가솔린 2.0",
                  "car_type": "SEDAN",
                  "fuel_name": "가솔린",
                  "base_price": 30000000
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "total_brands": 1,
  "page": 1,
  "limit": 10,
  "has_next": false,
  "has_prev": false
}
```

**장점**:
- 모든 트림 정보 포함
- 한 번의 API 호출로 모든 데이터 조회 가능

**단점**:
- 응답 크기가 큼
- 데이터가 중첩되어 파싱이 복잡함

---

## 권장 해결 방법

### 방법 1: 브랜드 요약 API 사용 (간단함)
```javascript
// 브랜드 목록만 가져오기
const response = await versionAPI.getBrandsSummary(versionId);
const brands = response.data.brands;

// 브랜드 선택 시 해당 브랜드의 트림만 가져오기
const brandResponse = await versionAPI.getBrandsWithFullData(versionId, { 
  brand_name: selectedBrand.name 
});
const trims = brandResponse.data.brands[0].vehicle_lines[0].models[0].trims;
```

### 방법 2: 새로운 간단한 API 엔드포인트 추가 (권장)

**엔드포인트**: `GET /api/versions/{version_id}/brands-list`

**설명**: 브랜드 ID와 이름만 조회

**응답 예시**:
```json
{
  "brands": [
    { "id": 1, "name": "현대" },
    { "id": 2, "name": "기아" }
  ]
}
```

**엔드포인트**: `GET /api/versions/{version_id}/brands/{brand_id}/trims`

**설명**: 특정 브랜드의 모든 트림 조회

**응답 예시**:
```json
{
  "brand": {
    "id": 1,
    "name": "현대"
  },
  "trims": [
    {
      "id": 1,
      "name": "소나타 가솔린 2.0",
      "model_name": "소나타",
      "base_price": 30000000
    },
    {
      "id": 2,
      "name": "아반떼 가솔린 1.6",
      "model_name": "아반떼",
      "base_price": 20000000
    }
  ],
  "total_trims": 2
}
```

---

## 백엔드 구현 필요 사항

### 1. 간단한 브랜드 목록 API
```python
@router.get("/{version_id}/brands-list")
def get_brands_list(
    version_id: int,
    db: Session = Depends(get_db)
):
    """버전의 브랜드 ID와 이름만 조회"""
    brands = db.query(StagingBrandORM).filter(
        StagingBrandORM.version_id == version_id
    ).all()
    
    return {
        "brands": [
            {"id": b.id, "name": b.name} 
            for b in brands
        ]
    }
```

### 2. 브랜드별 트림 목록 API
```python
@router.get("/{version_id}/brands/{brand_id}/trims")
def get_brand_trims(
    version_id: int,
    brand_id: int,
    db: Session = Depends(get_db)
):
    """특정 브랜드의 모든 트림 조회"""
    # 브랜드 확인
    brand = db.query(StagingBrandORM).filter(
        StagingBrandORM.id == brand_id,
        StagingBrandORM.version_id == version_id
    ).first()
    
    if not brand:
        raise HTTPException(404, "브랜드를 찾을 수 없습니다")
    
    # 트림 조회 (브랜드 -> 차량라인 -> 모델 -> 트림)
    trims = db.query(StagingTrimORM).join(
        StagingModelORM, StagingTrimORM.model_id == StagingModelORM.id
    ).join(
        StagingVehicleLineORM, StagingModelORM.vehicle_line_id == StagingVehicleLineORM.id
    ).filter(
        StagingVehicleLineORM.brand_id == brand_id
    ).all()
    
    return {
        "brand": {"id": brand.id, "name": brand.name},
        "trims": [
            {
                "id": t.id,
                "name": t.name,
                "model_name": t.model.name,
                "base_price": t.base_price
            }
            for t in trims
        ]
    }
```

---

## 프론트엔드 수정 방안

### 현재 코드 문제점
```javascript
// 현재: getBrandsWithFullData 사용
const response = await versionAPI.getBrandsWithFullData(versionId, { page: 1, limit: 100 });
```

### 개선된 코드
```javascript
// 방법 1: 간단한 API 사용
const brandsResponse = await versionAPI.getBrandsList(versionId);
const brands = brandsResponse.data.brands;

// 브랜드 선택 시
const handleBrandChange = async (brandId) => {
  const trimsResponse = await versionAPI.getBrandTrims(versionId, brandId);
  const trims = trimsResponse.data.trims;
  setTrims(trims);
};
```

---

## 결론

**단기 해결책**: 기존 `brands-summary` API를 사용하여 브랜드 목록을 가져오고, 브랜드 선택 시 `brands-with-full-data` API를 호출하여 트림 정보를 가져옴.

**장기 해결책**: 위에서 제안한 새로운 간단한 API 엔드포인트 2개를 추가하여 네트워크 부하를 줄이고 코드를 단순화.
