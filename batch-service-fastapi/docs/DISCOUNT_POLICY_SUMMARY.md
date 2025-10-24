# 할인 정책 (Discount Policy) 시스템 요약

## 📋 개요

Staging 레이어에 추가된 할인 정책 시스템은 브랜드, 차량 라인, 트림, 버전 단위로 다양한 할인 정책을 관리하는 시스템입니다.

## 🎯 할인 정책 유형

### 1. 카드사 제휴 할인 (CARD_BENEFIT)
- **설명**: 특정 카드사와 제휴하여 제공하는 캐시백 할인
- **주요 필드**:
  - `card_partner`: 카드사명 (예: 삼성카드, 신한카드)
  - `cashback_rate`: 캐시백 비율 (%)
- **예시**: "삼성카드 결제 시 5% 캐시백"

### 2. 브랜드 프로모션 할인 (BRAND_PROMO)
- **설명**: 브랜드 고유의 프로모션 할인
- **주요 필드**:
  - `discount_rate`: 할인율 (%)
  - `discount_amount`: 할인 금액 (원)
- **예시**: "현대차 특가 프로모션 10% 할인" 또는 "100만원 할인"

### 3. 재고 보유 할인 (INVENTORY)
- **설명**: 재고가 일정 수준 이상일 때 제공하는 할인
- **주요 필드**:
  - `inventory_level_threshold`: 재고 기준 수량
  - `discount_rate`: 할인율 (%)
- **예시**: "재고 10대 이상 시 15% 할인"

### 4. 선구매/특가 할인 (PRE_PURCHASE)
- **설명**: 선구매 또는 특가 이벤트 할인
- **주요 필드**:
  - `event_type`: 이벤트 타입 (PRE_PURCHASE, SPECIAL_OFFER)
  - `discount_rate`: 할인율 (%)
  - `discount_amount`: 할인 금액 (원)
  - `pre_purchase_start`: 선구매 시작일
- **예시**: "선구매 고객 20% 할인" 또는 "특가 이벤트 200만원 할인"

## 📊 데이터베이스 구조

### 테이블 관계도

```
staging_version (버전)
    ↓
staging_brand (브랜드)
    ↓
staging_vehicle_line (차량 라인)
    ↓
staging_model (모델)
    ↓
staging_trim (트림)
    ↓
staging_discount_policy (할인 정책 허브) ← [브랜드, 차량라인, 트림, 버전 참조]
    ├── staging_brand_card_benefit (카드사 제휴)
    ├── staging_brand_promo (브랜드 프로모션)
    ├── staging_brand_inventory_discount (재고 할인)
    └── staging_brand_pre_purchase (선구매/특가)
```

### 핵심 테이블

#### 1. staging_discount_policy (허브 테이블)
- **역할**: 할인 정책의 중심 허브
- **외래 키**: brand_id, vehicle_line_id, trim_id, version_id
- **정책 유형**: policy_type (ENUM)

#### 2. 세부 정책 테이블들
각 정책 유형별로 세부 정보를 저장하는 테이블이 분리되어 있습니다.

## 🔑 주요 특징

### 1. 계층적 구조
- 브랜드 → 차량 라인 → 모델 → 트림 → 할인 정책
- 각 계층별로 할인 정책 적용 가능

### 2. 버전 관리
- 할인 정책도 버전 단위로 관리
- 승인/거부 프로세스 지원

### 3. 유효 기간 관리
- `valid_from`: 유효 시작일
- `valid_to`: 유효 종료일
- 자동 만료 처리 가능

### 4. 활성/비활성 상태
- `is_active`: 활성 상태 관리
- 필요 시 정책을 비활성화하여 사용 가능

## 📝 API 엔드포인트

### 기본 CRUD
- `POST /api/discount/policies/` - 할인 정책 생성
- `GET /api/discount/policies/{policy_id}` - 단일 조회
- `GET /api/discount/policies/` - 목록 조회 (페이지네이션)
- `PUT /api/discount/policies/{policy_id}` - 수정
- `DELETE /api/discount/policies/{policy_id}` - 삭제

### 세부 정책별 API
- `POST /api/discount/card-benefits/` - 카드사 제휴 생성
- `POST /api/discount/promos/` - 브랜드 프로모션 생성
- `POST /api/discount/inventory-discounts/` - 재고 할인 생성
- `POST /api/discount/pre-purchases/` - 선구매/특가 생성

### 통합 API
- `POST /api/discount/policies/with-details` - 정책과 세부 정보 함께 생성
- `GET /api/discount/policies/{policy_id}/details` - 정책 상세 조회 (모든 유형 포함)
- `DELETE /api/discount/policies/{policy_id}/with-details` - 정책과 세부 정보 함께 삭제

## 🚀 사용 방법

### 1. 테이블 생성
```bash
# MySQL 접속
mysql -u wondergoodlife_user -p wondergoodlife_db

# SQL 스크립트 실행
source create_discount_policy_tables.sql
```

### 2. 할인 정책 생성 예시
```python
# 카드사 제휴 할인 정책 생성
policy_data = {
    "brand_id": 1,
    "vehicle_line_id": 1,
    "trim_id": 1,
    "version_id": 1,
    "policy_type": "CARD_BENEFIT",
    "title": "삼성카드 5% 캐시백",
    "description": "삼성카드로 결제 시 5% 캐시백",
    "valid_from": "2024-01-01T00:00:00",
    "valid_to": "2024-12-31T23:59:59",
    "is_active": True,
    "card_partner": "삼성카드",
    "cashback_rate": "5"
}
```

## 🔍 주요 기능

### 1. 검증 기능
- 각 정책 유형별 필수 필드 검증
- 유효 기간 검증 (시작일 < 종료일)
- 할인율/금액 범위 검증

### 2. 필터링 기능
- 브랜드별 조회
- 트림별 조회
- 버전별 조회
- 정책 유형별 조회
- 활성 상태별 조회

### 3. 페이지네이션
- 기본 20개씩 조회
- 최대 100개까지 조회 가능
- 정렬 기능 지원

## 📌 참고사항

### 1. CASCADE 삭제
- 할인 정책 삭제 시 관련 세부 정책도 자동 삭제
- 버전 삭제 시 관련 할인 정책도 자동 삭제

### 2. 트랜잭션 지원
- 정책과 세부 정보를 트랜잭션으로 함께 생성/삭제
- 일관성 보장

### 3. 확장성
- 새로운 정책 유형 추가 시 ENUM만 수정하면 됨
- 각 정책 유형별 세부 테이블 추가 가능

## 📊 통계 기능

### 버전별 할인 정책 요약
- `GET /api/discount/versions/{version_id}/summary`
- 각 정책 유형별 개수 집계
- 활성/비활성 상태별 집계

## 🎯 CDC (Change Data Capture) 지원

할인 정책도 승인된 버전의 CDC를 통해 Main 레이어로 마이그레이션될 수 있습니다.
- Staging 레이어에서 승인 → Main 레이어로 전송
- 데이터 일관성 보장

