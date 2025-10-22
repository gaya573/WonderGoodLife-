# 🔄 Admin Page 워크플로우

## 📊 전체 흐름

```
1. 엑셀 업로드 (📤)
   ↓ FastAPI :8000
2. Staging 테이블 저장 (⏳)
   ↓ 폴링 (2초마다)
3. 완료 알림 → 승인 대기 페이지로 이동
   ↓
4. Staging 데이터 확인 (🔍)
   ↓ 수정 가능
5. 승인 버튼 클릭 (✅)
   ↓ CDC Task
6. Main 테이블로 전송
   ↓
7. Spring Boot에서 조회 (🏢)
```

## 🎯 페이지별 기능

### 1️⃣ 대시보드 (`/`)
- 브랜드, 모델, 트림 통계 표시
- 최근 업데이트 정보

### 2️⃣ 엑셀 업로드 (`/excel-upload`)
**파일**: `ExcelUploadAsync.jsx`

**기능:**
- 드래그 앤 드롭 or 파일 선택
- FastAPI `/api/jobs/excel/upload` 호출
- Job ID 받음 → 폴링 시작
- 진행률 실시간 표시 (0% → 100%)
- 완료 시 "승인 대기 데이터 보기" 버튼 표시

**API:**
```javascript
const response = await uploadExcelAsync(file);
// { id: 1, status: 'PENDING', task_id: '...' }

// 2초마다 폴링
const status = await getJobStatus(jobId);
// { status: 'PROCESSING', progress_percentage: 45 }
```

### 3️⃣ 승인 대기 (`/staging-brands`) ⭐
**파일**: `StagingBrandList.jsx`

**기능:**
- Staging 브랜드 목록 조회 (PENDING만)
- 개별 수정 (이름, 국가 변경 가능)
- 개별 승인 → CDC → Main 테이블
- 개별 거부 → 사유 입력
- 일괄 승인 → 모든 PENDING 데이터 승인

**API:**
```javascript
// Staging 목록 조회
const brands = await stagingBrandAPI.getAll({ status: 'PENDING' });

// 수정
await stagingBrandAPI.update(id, { name: '현대자동차' });

// 승인
await stagingBrandAPI.approve(id, 'admin');
// → CDC Task 실행 → Main 테이블로 전송

// 거부
await stagingBrandAPI.reject(id, 'admin', '중복 데이터');

// 일괄 승인
await approveAll('admin');
```

### 4️⃣ 브랜드 관리 (`/brands`)
**파일**: `BrandList.jsx`

**기능:**
- **Main 테이블** 조회 (승인된 데이터만)
- Spring Boot API 사용 (`:8080`)
- CRUD (생성, 수정, 삭제)

**API:**
```javascript
// Main 브랜드 조회 (Spring Boot)
const brands = await brandAPI.getAll();
```

### 5️⃣ 모델 관리 (`/models`)
- Main 모델 CRUD
- Spring Boot API

### 6️⃣ 트림 관리 (`/trims`)
- Main 트림 CRUD
- Spring Boot API

## 🔗 API 서버 연결

### FastAPI (배치 서비스) - :8000
```javascript
const BATCH_API_URL = 'http://localhost:8000/api';

// 엑셀 업로드
POST /jobs/excel/upload

// 작업 상태
GET /jobs/{id}

// Staging CRUD
GET /staging/brands?status=PENDING
PUT /staging/brands/{id}
POST /staging/brands/{id}/approve
POST /staging/brands/{id}/reject
POST /staging/approve-all
```

### Spring Boot (CRUD 서비스) - :8080
```javascript
const CRUD_API_URL = 'http://localhost:8080/api';

// Main 데이터 조회
GET /brands
GET /models
GET /trims

// Main 데이터 수정
PUT /brands/{id}
DELETE /brands/{id}
```

## 🎬 사용 시나리오

### 시나리오 1: 엑셀 업로드 → 전체 승인

```
1. '엑셀 업로드' 메뉴 클릭
2. 파일 선택 → 업로드 시작
3. 진행률 확인 (0% → 100%)
4. 완료 → "승인 대기 데이터 보기" 클릭
5. Staging 브랜드 목록 확인
6. "전체 승인" 버튼 클릭
7. CDC 실행 → Main 테이블로 전송
8. '브랜드 관리'에서 확인
```

### 시나리오 2: 개별 확인 후 승인

```
1. '승인 대기' 메뉴에서 Staging 데이터 확인
2. 잘못된 데이터 있으면 "수정" 클릭
3. 수정 완료 → "승인" 버튼
4. 잘못된 데이터는 "거부" 버튼
5. Main 테이블에는 승인된 데이터만 저장
```

## 🎨 UI/UX

### 엑셀 업로드 페이지
- ⏳ **PENDING**: "작업 대기 중..."
- ⚙️ **PROCESSING**: 진행률 바 표시 "45% 완료"
- ✅ **COMPLETED**: "처리 완료! Staging 데이터를 확인하세요"
- ❌ **FAILED**: 에러 메시지 표시

### Staging 목록 페이지
- 🟡 **노란색 카드**: Staging 데이터 강조
- 🏷️ **승인 대기 배지**: 우측 상단
- 🕐 **등록 시간**: "2024-01-15 10:30:00"
- 👤 **출처**: "batch_service"
- 4개 버튼: "승인", "수정", "거부", "삭제"

## 📝 참고사항

### CORS 설정 필요

FastAPI에서 React Origin 허용:

```python
# app/config.py
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173"  # Vite 개발 서버
]
```

### 두 개의 API 서버 실행 필요

```bash
# 1. FastAPI (배치)
cd batch-service-fastapi/deployment/docker
docker-compose up -d

# 2. Spring Boot (CRUD)
cd carplatform/carplatform
./gradlew bootRun

# 3. React (프론트)
cd admin-page/admin-wondergoodlife
npm run dev
```

---

**엑셀 업로드 → Staging → 승인 → Main 완벽한 워크플로우!** ✨

