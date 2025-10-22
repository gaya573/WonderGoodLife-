# 🔄 데이터 흐름 (Staging → Approval → Main)

## 📊 전체 아키텍처

```
┌─────────────────────┐
│   React Admin Page  │ (프론트엔드)
└──────┬──────────────┘
       │
       ├─────────────────────────────┐
       ↓                             ↓
┌──────────────────┐      ┌─────────────────────┐
│  FastAPI         │      │  Spring Boot        │
│  (배치 서비스)    │      │  (CRUD 서비스)      │
│  :8000           │      │  :8080              │
└──────┬───────────┘      └──────────┬──────────┘
       │                             │
       └─────────────┬───────────────┘
                     ↓
          ┌──────────────────────┐
          │  MySQL Database      │
          │  ┌────────────────┐  │
          │  │ Staging Tables │  │ ← FastAPI CRUD
          │  │ (임시 데이터)   │  │
          │  └────────────────┘  │
          │         ↓ CDC         │
          │  ┌────────────────┐  │
          │  │  Main Tables   │  │ ← Spring CRUD
          │  │  (승인된 데이터)│  │
          │  └────────────────┘  │
          └──────────────────────┘
```

## 🔥 핵심 워크플로우

### 1️⃣ 엑셀 업로드 → Staging 저장

```
사용자 엑셀 업로드
   ↓
POST /api/jobs/excel/upload (FastAPI)
   ↓
Celery Worker (백그라운드)
   ↓
Staging 테이블에 저장
   - staging_brand (approval_status = PENDING)
   - staging_model (approval_status = PENDING)
   - staging_trim (approval_status = PENDING)
```

### 2️⃣ 관리자 확인 (FastAPI CRUD)

```
GET /api/staging/brands?status=PENDING
   ↓
관리자가 Staging 데이터 확인
   ↓
PUT /api/staging/brands/{id} (수정 가능)
```

### 3️⃣ 승인 → CDC → Main 테이블

```
POST /api/staging/brands/{id}/approve
   ↓
Staging 데이터 상태 = APPROVED
   ↓
Celery CDC Task 실행
   ↓
Main 테이블에 복사
   - brand
   - model
   - trim
```

### 4️⃣ Spring Boot에서 조회

```
GET /api/brands (Spring Boot :8080)
   ↓
Main 테이블 조회
   ↓
승인된 데이터만 반환
```

## 📡 API 엔드포인트

### FastAPI (:8000) - Staging 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| **작업 관리** |
| POST | `/api/jobs/excel/upload` | 엑셀 비동기 업로드 |
| GET | `/api/jobs/{id}` | 작업 상태 조회 (폴링) |
| **Staging CRUD** |
| GET | `/api/staging/brands` | Staging 브랜드 목록 |
| GET | `/api/staging/brands?status=PENDING` | 승인 대기 목록 |
| PUT | `/api/staging/brands/{id}` | Staging 브랜드 수정 |
| **승인/거부** |
| POST | `/api/staging/brands/{id}/approve` | 승인 (→ CDC) |
| POST | `/api/staging/brands/{id}/reject` | 거부 |
| POST | `/api/staging/approve-all` | 일괄 승인 |

### Spring Boot (:8080) - Main 데이터 조회

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/brands` | 승인된 브랜드 조회 |
| GET | `/api/models` | 승인된 모델 조회 |
| GET | `/api/trims` | 승인된 트림 조회 |
| PUT | `/api/brands/{id}` | 브랜드 수정 |
| DELETE | `/api/brands/{id}` | 브랜드 삭제 |

## 🔄 상세 흐름

### Step 1: 엑셀 업로드

```typescript
// React
const formData = new FormData();
formData.append('file', file);

const response = await axios.post(
  'http://localhost:8000/api/jobs/excel/upload',
  formData
);

const jobId = response.data.id;  // Job ID 받음
```

### Step 2: 작업 상태 폴링

```typescript
// 2초마다 상태 확인
const checkStatus = setInterval(async () => {
  const status = await axios.get(
    `http://localhost:8000/api/jobs/${jobId}`
  );
  
  if (status.data.status === 'COMPLETED') {
    clearInterval(checkStatus);
    // Staging 데이터 조회로 이동
    loadStagingData();
  }
}, 2000);
```

### Step 3: Staging 데이터 확인

```typescript
// Staging 데이터 조회
const stagingBrands = await axios.get(
  'http://localhost:8000/api/staging/brands?status=PENDING'
);

// 관리자가 데이터 확인
// [ ] 현대 (KR) - 수정 가능
// [ ] 기아 (KR) - 수정 가능
```

### Step 4: 데이터 수정 (선택)

```typescript
// 수정 필요 시
await axios.put(
  `http://localhost:8000/api/staging/brands/${id}`,
  { name: "현대자동차", country: "KR" }
);
```

### Step 5: 승인

```typescript
// 개별 승인
await axios.post(
  `http://localhost:8000/api/staging/brands/${id}/approve`,
  { approved_by: "admin@example.com" }
);

// 또는 일괄 승인
await axios.post(
  'http://localhost:8000/api/staging/approve-all',
  { approved_by: "admin@example.com" }
);
```

### Step 6: CDC (자동)

```python
# Celery Task가 백그라운드에서 실행
@shared_task
def sync_approved_to_main(entity_type, staging_id):
    # Staging 데이터 조회
    staging_brand = db.query(StagingBrandORM).get(staging_id)
    
    # Main 테이블에 복사
    main_brand = BrandORM(
        name=staging_brand.name,
        country=staging_brand.country,
        logo_url=staging_brand.logo_url
    )
    db.add(main_brand)
    db.commit()
```

### Step 7: Spring Boot에서 조회

```java
// Spring Boot Controller
@GetMapping("/api/brands")
public List<Brand> getBrands() {
    // Main 테이블에서 조회
    return brandRepository.findAll();
}
```

## 🎯 테이블 구조

### Staging 테이블 (FastAPI)

```sql
staging_brand
├── id
├── name
├── country
├── logo_url
├── approval_status (PENDING/APPROVED/REJECTED)
├── created_by (batch_service)
├── created_at
├── approved_by
├── approved_at
└── rejection_reason
```

### Main 테이블 (Spring Boot)

```sql
brand
├── id
├── name
├── country
└── logo_url
```

## 💡 왜 이런 구조?

### ✅ 장점

1. **데이터 검증**: 관리자가 승인 전 확인/수정 가능
2. **안전성**: 잘못된 데이터가 Main DB로 바로 들어가지 않음
3. **이력 관리**: 누가 언제 승인했는지 추적 가능
4. **롤백 가능**: 승인 전 데이터는 언제든 삭제 가능

### 🔄 흐름 요약

```
엑셀 업로드
   ↓ (Celery Worker)
Staging 테이블 (PENDING)
   ↓ (관리자 확인/수정)
승인 버튼
   ↓ (CDC Task)
Main 테이블
   ↓ (Spring Boot)
프론트엔드 조회
```

---

**단순하고 명확한 승인 워크플로우!** ✨

