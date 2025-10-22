# 🚘 WonderGoodLife 관리자 페이지

차량 정보를 관리하는 관리자 페이지입니다. **Staging/Approval 워크플로우**를 지원합니다.

## ✨ 주요 기능

### 📊 대시보드
- 브랜드, 모델, 트림 통계 확인
- 시스템 주요 기능 안내

### 📤 엑셀 업로드 (비동기)
- 드래그 앤 드롭으로 엑셀 파일 업로드
- Celery 백그라운드 처리
- 실시간 진행률 표시 (폴링 방식)
- **Staging 테이블**에 임시 저장

### 🔍 승인 대기 (Staging) ⭐ **신규!**
- 엑셀 업로드로 수집된 **임시 데이터** 확인
- 데이터 수정 가능
- 개별 승인/거부
- 일괄 승인
- **승인 시 Main 테이블로 자동 전송 (CDC)**

### 🏢 브랜드 관리
- **Main 테이블** 조회 (승인된 데이터만)
- 브랜드 생성, 수정, 삭제

### 🚗 모델 관리
- Main 테이블 조회
- 모델 생성, 수정, 삭제

### ⚙️ 트림 관리
- Main 테이블 조회
- 트림 생성, 수정, 삭제

## 🛠️ 기술 스택

- **React 19** - UI 라이브러리
- **Vite** - 빌드 도구
- **React Router** - 라우팅
- **Axios** - HTTP 클라이언트
- **CSS3** - 스타일링

## 📦 설치 및 실행

### 1. 패키지 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

개발 서버가 `http://localhost:5173`에서 실행됩니다.

## 🔗 API 연결

### 필수 서버 실행

#### 1. FastAPI (배치 서비스) - :8000
```bash
cd ../../batch-service-fastapi/deployment/docker
docker-compose up -d
```

**역할:**
- 엑셀 업로드 처리
- Staging CRUD
- 승인/거부 처리
- CDC (Staging → Main 전송)

#### 2. Spring Boot (CRUD 서비스) - :8080
```bash
cd ../../carplatform/carplatform
./gradlew bootRun
```

**역할:**
- Main 테이블 조회
- 승인된 데이터 CRUD

## 🔄 데이터 흐름

```
엑셀 업로드 (React)
   ↓
FastAPI :8000 (Celery 처리)
   ↓
Staging 테이블 (임시)
   ↓
관리자 승인 (React)
   ↓
CDC Task (Celery)
   ↓
Main 테이블
   ↓
Spring Boot :8080 (조회)
   ↓
React 화면에 표시
```

## 📋 페이지 구조

| 경로 | 파일 | 설명 | API 서버 |
|------|------|------|----------|
| `/` | Dashboard.jsx | 대시보드 | - |
| `/excel-upload` | ExcelUploadAsync.jsx | 엑셀 비동기 업로드 | FastAPI :8000 |
| `/staging-brands` | StagingBrandList.jsx | **승인 대기 목록** ⭐ | FastAPI :8000 |
| `/brands` | BrandList.jsx | 브랜드 관리 (Main) | Spring :8080 |
| `/models` | ModelList.jsx | 모델 관리 (Main) | Spring :8080 |
| `/trims` | TrimList.jsx | 트림 관리 (Main) | Spring :8080 |

## 🎯 사용 방법

### 1. 엑셀 파일 업로드

1. **엑셀 업로드** 메뉴 클릭
2. 파일 선택 또는 드래그 앤 드롭
3. **업로드 시작** 버튼 클릭
4. 진행률 확인 (0% → 100%)
5. 완료되면 **"승인 대기 데이터 보기"** 버튼 클릭

### 2. Staging 데이터 승인

1. **승인 대기** 메뉴 클릭
2. 임시 데이터 확인
3. 수정이 필요하면 **수정** 버튼 클릭
4. 확인 완료 후:
   - 개별 승인: **✅ 승인** 버튼
   - 또는 **전체 승인** 버튼 (우측 상단)
5. 승인되면 CDC가 자동으로 Main 테이블로 전송

### 3. 승인된 데이터 확인

1. **브랜드 관리** 메뉴 클릭
2. Main 테이블에 저장된 데이터 확인
3. 필요시 수정/삭제 가능

## 📡 API 엔드포인트

### FastAPI (Staging)

```javascript
// 엑셀 비동기 업로드
POST http://localhost:8000/api/jobs/excel/upload

// 작업 상태 조회 (폴링)
GET http://localhost:8000/api/jobs/{id}

// Staging 브랜드 목록
GET http://localhost:8000/api/staging/brands?status=PENDING

// Staging 브랜드 수정
PUT http://localhost:8000/api/staging/brands/{id}

// 승인
POST http://localhost:8000/api/staging/brands/{id}/approve

// 거부
POST http://localhost:8000/api/staging/brands/{id}/reject

// 일괄 승인
POST http://localhost:8000/api/staging/approve-all
```

### Spring Boot (Main)

```javascript
// Main 브랜드 조회
GET http://localhost:8080/api/brands

// Main 모델 조회
GET http://localhost:8080/api/models
```

## 🎨 UI 특징

### 승인 대기 카드
- 🟡 **노란색 배경**: Staging 데이터 강조
- 🏷️ **"승인 대기" 배지**: 우측 상단
- 🕐 **등록 시간**: 언제 업로드되었는지 표시
- 👤 **출처**: batch_service or crawling
- 4개 버튼: 승인, 수정, 거부, 삭제

### 진행률 표시
- 📊 **Progress Bar**: 0% → 100% 애니메이션
- ⏱️ **폴링 주기**: 2초마다 상태 확인
- ✅ **완료 알림**: "처리 완료! Staging 데이터를 확인하세요"

## 🔧 개발

### Linting
```bash
npm run lint
```

### 빌드
```bash
npm run build
```

## 💡 주요 변경사항

| 변경 | Before | After |
|------|--------|-------|
| 엑셀 업로드 | 동기 처리 (Spring) | **비동기 처리 (FastAPI + Celery)** |
| 데이터 저장 | Main DB로 바로 | **Staging → 승인 → Main** |
| 진행률 표시 | 없음 | **실시간 폴링으로 표시** |
| 승인 프로세스 | 없음 | **승인 대기 페이지 추가** |
| API 서버 | Spring Boot만 | **FastAPI + Spring Boot** (역할 분담) |

## 📝 환경 변수

API URL을 변경하려면 `src/services/api.js` 수정:

```javascript
const BATCH_API_URL = 'http://your-fastapi.com/api';  // FastAPI
const CRUD_API_URL = 'http://your-spring.com/api';    // Spring Boot
```

## 🚀 배포

### 프로덕션 빌드
```bash
npm run build
```

빌드된 파일은 `dist` 폴더에 생성됩니다.

### Nginx 설정 예시
```nginx
server {
    listen 80;
    
    location / {
        root /var/www/admin;
        try_files $uri $uri/ /index.html;
    }
    
    # FastAPI Proxy
    location /api/batch/ {
        proxy_pass http://localhost:8000/api/;
    }
    
    # Spring Boot Proxy
    location /api/crud/ {
        proxy_pass http://localhost:8080/api/;
    }
}
```

## 📚 관련 문서

- [WORKFLOW.md](./WORKFLOW.md) - 상세 워크플로우 설명

---

**Made with ❤️ for WonderGoodLife**
