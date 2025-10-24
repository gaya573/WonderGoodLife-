# 🎯 할인 정책 API 설계 문서

## 📋 목차
1. [API 구조 개요](#api-구조-개요)
2. [할인 정책 등록 API](#할인-정책-등록-api)
3. [카드사 제휴 등록 API](#카드사-제휴-등록-api)
4. [브랜드별 혜택 등록 API](#브랜드별-혜택-등록-api)
5. [재고보유 할인 등록 API](#재고보유-할인-등록-api)
6. [선구매 할인 등록 API](#선구매-할인-등록-api)
7. [통합 등록 API](#통합-등록-api)
8. [조회 API](#조회-api)
9. [사용 예시](#사용-예시)

---

## 🏗️ API 구조 개요

### 핵심 개념
**버전 기반으로 할인 정책을 등록하고, 각 정책 유형별로 세부 정보를 관리합니다.**

```
POST /api/discount/policies/                    # 할인 정책 생성
POST /api/discount/card-benefits/               # 카드사 제휴 등록
POST /api/discount/promos/                      # 브랜드별 혜택 등록
POST /api/discount/inventory-discounts/         # 재고보유 할인 등록
POST /api/discount/pre-purchases/               # 선구매 할인 등록
POST /api/discount/bulk-register/               # 통합 등록 (한번에 여러 유형)
```

### 데이터 흐름
```
1. 할인 정책 생성 (discount_policy)
   ↓
2. 정책 유형별 세부 정보 등록
   - 카드사 제휴 (brand_card_benefit)
   - 브랜드 프로모션 (brand_promo)
   - 재고 할인 (brand_inventory_discount)
   - 선구매 할인 (brand_pre_purchase)
   ↓
3. 정책 활성화 및 관리
```

---

## 📝 할인 정책 등록 API

### 1. 기본 할인 정책 생성
```http
POST /api/discount/policies/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "brand_id": 1,
  "trim_id": 5,
  "version_id": 10,
  "policy_type": "CARD_BENEFIT",
  "title": "삼성카드 제휴 할인 정책",
  "description": "삼성카드로 결제 시 다양한 혜택 제공",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "brand_id": 1,
  "trim_id": 5,
  "version_id": 10,
  "policy_type": "CARD_BENEFIT",
  "title": "삼성카드 제휴 할인 정책",
  "description": "삼성카드로 결제 시 다양한 혜택 제공",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

---

## 💳 카드사 제휴 등록 API

### 2. 카드사 제휴 할인 등록
```http
POST /api/discount/card-benefits/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "card_partner": "삼성카드",
  "cashback_rate": 5.00,
  "title": "삼성카드 5% 캐시백",
  "description": "삼성카드로 결제 시 5% 캐시백 혜택",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "discount_policy_id": 1,
  "card_partner": "삼성카드",
  "cashback_rate": 5.00,
  "title": "삼성카드 5% 캐시백",
  "description": "삼성카드로 결제 시 5% 캐시백 혜택",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

### 3. 여러 카드사 일괄 등록
```http
POST /api/discount/card-benefits/bulk
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "card_benefits": [
    {
      "card_partner": "삼성카드",
      "cashback_rate": 5.00,
      "title": "삼성카드 5% 캐시백",
      "description": "삼성카드로 결제 시 5% 캐시백 혜택"
    },
    {
      "card_partner": "현대카드",
      "cashback_rate": 3.00,
      "title": "현대카드 3% 캐시백",
      "description": "현대카드로 결제 시 3% 캐시백 혜택"
    },
    {
      "card_partner": "KB카드",
      "cashback_rate": 4.00,
      "title": "KB카드 4% 캐시백",
      "description": "KB카드로 결제 시 4% 캐시백 혜택"
    }
  ],
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

---

## 🏷️ 브랜드별 혜택 등록 API

### 4. 브랜드 프로모션 등록
```http
POST /api/discount/promos/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "discount_rate": 10.00,
  "discount_amount": 500000,
  "title": "브랜드 프로모션 10% 할인",
  "description": "현대 브랜드 고객 대상 특별 할인",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "discount_policy_id": 1,
  "discount_rate": 10.00,
  "discount_amount": 500000,
  "title": "브랜드 프로모션 10% 할인",
  "description": "현대 브랜드 고객 대상 특별 할인",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

### 5. 여러 프로모션 일괄 등록
```http
POST /api/discount/promos/bulk
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "promos": [
    {
      "discount_rate": 10.00,
      "title": "신규 고객 10% 할인",
      "description": "신규 고객 대상 특별 할인"
    },
    {
      "discount_amount": 1000000,
      "title": "정액 할인 100만원",
      "description": "정액 할인 혜택"
    },
    {
      "discount_rate": 5.00,
      "discount_amount": 300000,
      "title": "복합 할인",
      "description": "할인율과 정액 할인 복합 적용"
    }
  ],
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

---

## 🚛 재고보유 할인 등록 API

### 6. 재고 할인 등록
```http
POST /api/discount/inventory-discounts/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "inventory_level_threshold": 100,
  "discount_rate": 3.00,
  "title": "재고 100대 이상 3% 할인",
  "description": "재고가 100대 이상일 때 추가 할인",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "discount_policy_id": 1,
  "inventory_level_threshold": 100,
  "discount_rate": 3.00,
  "title": "재고 100대 이상 3% 할인",
  "description": "재고가 100대 이상일 때 추가 할인",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

### 7. 여러 재고 기준 일괄 등록
```http
POST /api/discount/inventory-discounts/bulk
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "inventory_discounts": [
    {
      "inventory_level_threshold": 50,
      "discount_rate": 2.00,
      "title": "재고 50대 이상 2% 할인",
      "description": "재고가 50대 이상일 때 할인"
    },
    {
      "inventory_level_threshold": 100,
      "discount_rate": 3.00,
      "title": "재고 100대 이상 3% 할인",
      "description": "재고가 100대 이상일 때 할인"
    },
    {
      "inventory_level_threshold": 200,
      "discount_rate": 5.00,
      "title": "재고 200대 이상 5% 할인",
      "description": "재고가 200대 이상일 때 할인"
    }
  ],
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

---

## ⏰ 선구매 할인 등록 API

### 8. 선구매 할인 등록
```http
POST /api/discount/pre-purchases/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "event_type": "PRE_PURCHASE",
  "discount_rate": 8.00,
  "discount_amount": 800000,
  "title": "사전 구매 8% 할인",
  "description": "사전 구매 시 8% 할인 혜택",
  "pre_purchase_start": "2024-01-01T00:00:00",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "discount_policy_id": 1,
  "event_type": "PRE_PURCHASE",
  "discount_rate": 8.00,
  "discount_amount": 800000,
  "title": "사전 구매 8% 할인",
  "description": "사전 구매 시 8% 할인 혜택",
  "pre_purchase_start": "2024-01-01T00:00:00",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

### 9. 여러 선구매 이벤트 일괄 등록
```http
POST /api/discount/pre-purchases/bulk
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "discount_policy_id": 1,
  "pre_purchases": [
    {
      "event_type": "PRE_PURCHASE",
      "discount_rate": 8.00,
      "title": "사전 구매 8% 할인",
      "description": "사전 구매 시 8% 할인",
      "pre_purchase_start": "2024-01-01T00:00:00"
    },
    {
      "event_type": "SPECIAL_OFFER",
      "discount_amount": 1000000,
      "title": "특가 이벤트 100만원 할인",
      "description": "특가 이벤트 할인"
    },
    {
      "event_type": "PRE_PURCHASE",
      "discount_rate": 5.00,
      "discount_amount": 500000,
      "title": "복합 선구매 할인",
      "description": "할인율과 정액 할인 복합"
    }
  ],
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true
}
```

---

## 🔄 통합 등록 API

### 10. 모든 할인 유형 통합 등록
```http
POST /api/discount/bulk-register/
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "brand_id": 1,
  "trim_id": 5,
  "version_id": 10,
  "policy_type": "CARD_BENEFIT",
  "title": "현대 아반떼 하이브리드 종합 할인 정책",
  "description": "현대 아반떼 하이브리드에 대한 모든 할인 정책",
  "valid_from": "2024-01-01T00:00:00",
  "valid_to": "2024-12-31T23:59:59",
  "is_active": true,
  
  "card_benefits": [
    {
      "card_partner": "삼성카드",
      "cashback_rate": 5.00,
      "title": "삼성카드 5% 캐시백",
      "description": "삼성카드로 결제 시 5% 캐시백"
    },
    {
      "card_partner": "현대카드",
      "cashback_rate": 3.00,
      "title": "현대카드 3% 캐시백",
      "description": "현대카드로 결제 시 3% 캐시백"
    }
  ],
  
  "promos": [
    {
      "discount_rate": 10.00,
      "title": "신규 고객 10% 할인",
      "description": "신규 고객 대상 특별 할인"
    }
  ],
  
  "inventory_discounts": [
    {
      "inventory_level_threshold": 100,
      "discount_rate": 3.00,
      "title": "재고 100대 이상 3% 할인",
      "description": "재고가 100대 이상일 때 추가 할인"
    }
  ],
  
  "pre_purchases": [
    {
      "event_type": "PRE_PURCHASE",
      "discount_rate": 8.00,
      "title": "사전 구매 8% 할인",
      "description": "사전 구매 시 8% 할인",
      "pre_purchase_start": "2024-01-01T00:00:00"
    }
  ]
}
```

**Response:**
```json
{
  "discount_policy": {
    "id": 1,
    "brand_id": 1,
    "trim_id": 5,
    "version_id": 10,
    "policy_type": "CARD_BENEFIT",
    "title": "현대 아반떼 하이브리드 종합 할인 정책",
    "description": "현대 아반떼 하이브리드에 대한 모든 할인 정책",
    "valid_from": "2024-01-01T00:00:00",
    "valid_to": "2024-12-31T23:59:59",
    "is_active": true
  },
  "card_benefits": [
    {
      "id": 1,
      "discount_policy_id": 1,
      "card_partner": "삼성카드",
      "cashback_rate": 5.00,
      "title": "삼성카드 5% 캐시백"
    },
    {
      "id": 2,
      "discount_policy_id": 1,
      "card_partner": "현대카드",
      "cashback_rate": 3.00,
      "title": "현대카드 3% 캐시백"
    }
  ],
  "promos": [
    {
      "id": 1,
      "discount_policy_id": 1,
      "discount_rate": 10.00,
      "title": "신규 고객 10% 할인"
    }
  ],
  "inventory_discounts": [
    {
      "id": 1,
      "discount_policy_id": 1,
      "inventory_level_threshold": 100,
      "discount_rate": 3.00,
      "title": "재고 100대 이상 3% 할인"
    }
  ],
  "pre_purchases": [
    {
      "id": 1,
      "discount_policy_id": 1,
      "event_type": "PRE_PURCHASE",
      "discount_rate": 8.00,
      "title": "사전 구매 8% 할인"
    }
  ],
  "summary": {
    "total_policies": 1,
    "total_card_benefits": 2,
    "total_promos": 1,
    "total_inventory_discounts": 1,
    "total_pre_purchases": 1
  }
}
```

---

## 🔍 조회 API

### 11. 할인 정책 조회
```http
GET /api/discount/policies/?brand_id=1&trim_id=5&version_id=10&policy_type=CARD_BENEFIT
Authorization: Bearer {token}
```

### 12. 특정 정책의 모든 할인 정보 조회
```http
GET /api/discount/policies/{policy_id}/details
Authorization: Bearer {token}
```

**Response:**
```json
{
  "policy": {
    "id": 1,
    "brand_id": 1,
    "trim_id": 5,
    "version_id": 10,
    "policy_type": "CARD_BENEFIT",
    "title": "현대 아반떼 하이브리드 종합 할인 정책"
  },
  "card_benefits": [...],
  "promos": [...],
  "inventory_discounts": [...],
  "pre_purchases": [...]
}
```

### 13. 버전별 할인 정책 요약
```http
GET /api/discount/versions/{version_id}/summary
Authorization: Bearer {token}
```

---

## 📊 사용 예시

### 시나리오 1: 현대 아반떼 하이브리드 할인 정책 등록

```bash
# 1. 기본 정책 생성
curl -X POST "http://localhost:8000/api/discount/policies/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "brand_id": 1,
    "trim_id": 5,
    "version_id": 10,
    "policy_type": "CARD_BENEFIT",
    "title": "현대 아반떼 하이브리드 할인 정책",
    "valid_from": "2024-01-01T00:00:00",
    "valid_to": "2024-12-31T23:59:59"
  }'

# 2. 카드사 제휴 등록
curl -X POST "http://localhost:8000/api/discount/card-benefits/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "discount_policy_id": 1,
    "card_partner": "삼성카드",
    "cashback_rate": 5.00,
    "title": "삼성카드 5% 캐시백"
  }'

# 3. 브랜드 프로모션 등록
curl -X POST "http://localhost:8000/api/discount/promos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "discount_policy_id": 1,
    "discount_rate": 10.00,
    "title": "신규 고객 10% 할인"
  }'
```

### 시나리오 2: 통합 등록 (한번에 모든 유형)

```bash
curl -X POST "http://localhost:8000/api/discount/bulk-register/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "brand_id": 1,
    "trim_id": 5,
    "version_id": 10,
    "policy_type": "CARD_BENEFIT",
    "title": "현대 아반떼 하이브리드 종합 할인 정책",
    "valid_from": "2024-01-01T00:00:00",
    "valid_to": "2024-12-31T23:59:59",
    "card_benefits": [
      {
        "card_partner": "삼성카드",
        "cashback_rate": 5.00,
        "title": "삼성카드 5% 캐시백"
      }
    ],
    "promos": [
      {
        "discount_rate": 10.00,
        "title": "신규 고객 10% 할인"
      }
    ],
    "inventory_discounts": [
      {
        "inventory_level_threshold": 100,
        "discount_rate": 3.00,
        "title": "재고 100대 이상 3% 할인"
      }
    ],
    "pre_purchases": [
      {
        "event_type": "PRE_PURCHASE",
        "discount_rate": 8.00,
        "title": "사전 구매 8% 할인",
        "pre_purchase_start": "2024-01-01T00:00:00"
      }
    ]
  }'
```

---

## 🎯 핵심 특징

### ✅ 장점
1. **유연한 등록 방식**: 개별 등록과 통합 등록 모두 지원
2. **일괄 처리**: 여러 할인 유형을 한번에 등록 가능
3. **버전 기반 관리**: 버전별로 할인 정책 관리
4. **타입 안전성**: 각 유형별 명확한 스키마 정의
5. **확장성**: 새로운 할인 유형 추가 용이

### 🔍 검증 규칙
1. **필수 필드 검증**: 각 유형별 필수 필드 확인
2. **할인율 범위**: 0-100% 범위 내 검증
3. **날짜 검증**: 시작일 < 종료일 확인
4. **정책 유형 일치**: 정책 타입과 세부 유형 일치 확인
5. **버전 존재 확인**: 버전 ID 유효성 검증

---

## 📚 요약

| API | 목적 | 특징 |
|-----|------|------|
| `/policies/` | 기본 정책 생성 | 허브 테이블 생성 |
| `/card-benefits/` | 카드사 제휴 등록 | 캐시백 비율 관리 |
| `/promos/` | 브랜드 프로모션 등록 | 할인율/정액 할인 |
| `/inventory-discounts/` | 재고 할인 등록 | 재고 기준 관리 |
| `/pre-purchases/` | 선구매 할인 등록 | 이벤트 타입 관리 |
| `/bulk-register/` | 통합 등록 | 모든 유형 한번에 |

이 설계는 **유연하고 확장 가능한 할인 정책 관리 시스템**을 제공합니다.
