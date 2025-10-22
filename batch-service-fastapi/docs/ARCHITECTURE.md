# 🏗️ 아키텍처 설계

## 📊 전체 시스템 구조

```
┌───────────────────────────────────────────────────────┐
│                  Frontend (React)                      │
│              Admin Dashboard :5173                     │
└────────┬────────────────────────────────┬─────────────┘
         │                                │
         ↓                                ↓
┌─────────────────────┐        ┌──────────────────────┐
│   FastAPI :8000     │        │  Spring Boot :8080   │
│   (배치 서비스)      │        │  (CRUD 서비스)       │
│                     │        │                      │
│  - 엑셀 업로드      │        │  - 브랜드 조회       │
│  - 크롤링 (향후)    │        │  - 모델 조회         │
│  - Staging CRUD     │        │  - 트림 조회         │
│  - 승인 처리        │        │  - Main 데이터 수정  │
└────────┬────────────┘        └──────────┬───────────┘
         │                                │
         │   ┌────────────────────────────┘
         │   │
         ↓   ↓
┌────────────────────────────────────────────────────┐
│               MySQL Database                       │
│  ┌──────────────────┐    ┌────────────────────┐  │
│  │ Staging Tables   │    │  Main Tables       │  │
│  │ (임시 데이터)     │    │  (승인된 데이터)    │  │
│  │                  │    │                    │  │
│  │ staging_brand    │━━━▶│  brand            │  │
│  │ staging_model    │ CDC │  model            │  │
│  │ staging_trim     │    │  trim             │  │
│  └──────────────────┘    └────────────────────┘  │
└────────────────────────────────────────────────────┘

        ↑
        │ Celery Tasks
┌───────┴────────┐
│  Redis Queue   │
│  :6379         │
└────────────────┘
```

## 🎯 역할 분담

### FastAPI (:8000) - 배치 서비스

**책임:**
- ✅ 엑셀 파일 업로드
- ✅ 크롤링 (향후)
- ✅ Staging 테이블 CRUD
- ✅ 승인/거부 처리
- ✅ CDC (Staging → Main 전송)

**엔드포인트:**
```
POST   /api/jobs/excel/upload
GET    /api/jobs/{id}
GET    /api/staging/brands
PUT    /api/staging/brands/{id}
POST   /api/staging/brands/{id}/approve
```

### Spring Boot (:8080) - CRUD 서비스

**책임:**
- ✅ 승인된 데이터 조회
- ✅ Main 테이블 CRUD
- ✅ 비즈니스 로직 (추천, 검색 등)

**엔드포인트:**
```
GET    /api/brands
GET    /api/models
GET    /api/trims
PUT    /api/brands/{id}
DELETE /api/brands/{id}
```

## 🔄 데이터 흐름

### 1. 엑셀 업로드 플로우

```
사용자 (React)
   │
   ├─→ POST /api/jobs/excel/upload (FastAPI)
   │      ↓
   │   Job 생성 (PENDING)
   │      ↓
   │   Celery Task 등록
   │      ↓
   │   즉시 응답 (Job ID)
   │
   ├─→ GET /api/jobs/{id} (폴링 2초마다)
   │      ↓
   │   status: PROCESSING → COMPLETED
   │
   └─→ GET /api/staging/brands?status=PENDING
          ↓
       Staging 데이터 표시
```

### 2. 승인 플로우

```
관리자 (React)
   │
   ├─→ GET /api/staging/brands?status=PENDING
   │      ↓
   │   승인 대기 리스트 표시
   │
   ├─→ PUT /api/staging/brands/1 (수정 - 선택)
   │
   └─→ POST /api/staging/brands/1/approve
          ↓
       Staging 상태 → APPROVED
          ↓
       Celery CDC Task 실행
          ↓
       Main 테이블에 복사
```

### 3. Spring Boot 조회 플로우

```
사용자 (React)
   │
   └─→ GET /api/brands (Spring Boot :8080)
          ↓
       Main 테이블에서 조회
          ↓
       승인된 데이터만 반환
```

## 🏗️ Hexagonal Architecture

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (API)            │
│  ┌────────┐ ┌────────┐ ┌──────────────┐   │
│  │Brands  │ │Staging │ │Jobs (Celery) │   │
│  └────────┘ └────────┘ └──────────────┘   │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│      Application Layer (Use Cases)          │
│  ┌────────────┐ ┌──────────────────────┐   │
│  │Services    │ │Ports (Interfaces)    │   │
│  └────────────┘ └──────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│        Domain Layer (Business Logic)        │
│  ┌────────┐ ┌────────┐ ┌──────────────┐   │
│  │Entities│ │Value   │ │Approval      │   │
│  │        │ │Objects │ │Workflow      │   │
│  └────────┘ └────────┘ └──────────────┘   │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│    Infrastructure Layer (Adapters)          │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐    │
│  │Repository│ │Excel     │ │Celery   │    │
│  │(MySQL)   │ │Parser    │ │Tasks    │    │
│  └──────────┘ └──────────┘ └─────────┘    │
└─────────────────────────────────────────────┘
```

## 💾 데이터베이스 구조

### Staging 테이블

```sql
CREATE TABLE staging_brand (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL,
    logo_url VARCHAR(500),
    
    -- 승인 워크플로우
    approval_status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
    created_by VARCHAR(100) DEFAULT 'batch_service',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(100),
    approved_at DATETIME,
    rejection_reason TEXT
);
```

### Main 테이블

```sql
CREATE TABLE brand (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL,
    logo_url VARCHAR(500)
);
```

## 🔧 기술 스택

### FastAPI (배치 서비스)
- **Framework**: FastAPI
- **Async Queue**: Celery + Redis
- **ORM**: SQLAlchemy
- **Data**: Pandas (Excel), Playwright (Crawling)

### Spring Boot (CRUD 서비스)
- **Framework**: Spring Boot
- **ORM**: Spring Data JPA
- **Database**: MySQL

### 공유 리소스
- **Database**: MySQL 8.0
- **Message Broker**: Redis

## 🚀 배포 전략

### 개발 환경
```bash
# FastAPI (Docker Compose)
cd deployment/docker
docker-compose up -d

# Spring Boot (로컬)
cd carplatform/carplatform
./gradlew bootRun
```

### 프로덕션 (EC2)
```bash
# Docker Compose로 모든 서비스 실행
cd deployment/docker
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
```

**왜 Kubernetes 없이?**
- 모놀리식 구조
- 트래픽 낮음 (관리자용)
- EC2 1대로 충분
- Docker Compose가 더 단순

## 📊 장점

### ✅ 데이터 안전성
- 잘못된 데이터가 Main DB로 바로 들어가지 않음
- 관리자가 승인 전 검증 가능

### ✅ 유연성
- Staging에서 수정 가능
- 거부 시 사유 기록

### ✅ 추적 가능성
- 누가 언제 승인했는지 기록
- 배치 작업 이력 관리

### ✅ 확장성
- 크롤링 추가 시 Celery로 쉽게 확장
- CDC 로직 커스터마이징 가능

---

**현실적이고 확장 가능한 아키텍처!** 🎯


