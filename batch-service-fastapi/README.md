# 🚀 Batch Service - FastAPI

**Hexagonal Architecture** + **Staging/Approval 워크플로우** 기반 배치 서비스

## 🎯 핵심 기능

### 1. 📤 엑셀 업로드 (비동기)
- Celery Worker가 백그라운드 처리
- Staging 테이블에 임시 저장
- 실시간 진행률 추적

### 2. 🔍 Staging 데이터 관리
- 관리자가 임시 데이터 확인/수정
- 승인/거부 처리
- 일괄 승인 지원

### 3. 🔄 CDC (Change Data Capture)
- 승인된 데이터를 Main 테이블로 자동 전송
- Celery Task로 비동기 처리

### 4. 🕷️ 크롤링 (향후)
- Playwright로 웹 크롤링
- 스케줄링 지원 (Celery Beat)

## 📊 시스템 구조

```
React → FastAPI (Staging CRUD) → Celery → MySQL (Staging)
                    ↓ 승인
                  CDC Task
                    ↓
               MySQL (Main) ← Spring Boot (조회)
```

## 📁 프로젝트 구조

```
batch-service-fastapi/
├── app/                    # 애플리케이션 (Hexagonal)
│   ├── domain/            # 도메인 로직
│   ├── application/       # 유스케이스
│   ├── infrastructure/    # DB, Parser
│   ├── presentation/      # API
│   └── tasks/             # Celery 작업
├── deployment/             # 배포 설정
│   ├── docker/            # Docker Compose
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   └── README.md          # 배포 가이드
├── docs/                   # 문서
│   ├── FLOW.md            # 데이터 흐름
│   ├── API_STAGING.md     # Staging API 가이드
│   └── ARCHITECTURE.md    # 아키텍처 설명
├── uploads/                # 업로드 파일
├── celery_app.py          # Celery 엔트리포인트
└── requirements.txt       # Python 패키지
```

## 🚀 실행 방법

### Docker Compose (추천)

```bash
cd deployment/docker
docker-compose up -d

# 접속
# - API: http://localhost:8000/docs
# - Flower: http://localhost:5555
```

### 로컬 개발

```bash
# 가상환경
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 패키지 설치
pip install -r requirements.txt

# DB & Redis만 Docker로
cd deployment/docker
docker-compose up -d mysql redis

# FastAPI 실행
uvicorn app.main:app --reload

# Celery Worker (별도 터미널)
celery -A celery_app worker --loglevel=info
```

## 📡 주요 API

### Staging 관리 (FastAPI)

```bash
# Staging 목록
GET /api/staging/brands?status=PENDING

# Staging 수정
PUT /api/staging/brands/1

# 승인 (CDC 실행)
POST /api/staging/brands/1/approve

# 거부
POST /api/staging/brands/1/reject

# 일괄 승인
POST /api/staging/approve-all
```

### Main 데이터 조회 (Spring Boot)

```bash
GET http://localhost:8080/api/brands
GET http://localhost:8080/api/models
GET http://localhost:8080/api/trims
```

## 🔄 데이터 흐름

```
1. 엑셀 업로드 → Staging 테이블
2. 관리자 확인 → FastAPI CRUD
3. 승인 → CDC Task
4. Main 테이블 → Spring Boot 조회
```

## 📚 문서

- [docs/FLOW.md](./docs/FLOW.md) - 상세 데이터 흐름
- [docs/API_STAGING.md](./docs/API_STAGING.md) - Staging API 가이드  
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - 아키텍처 설명
- [deployment/README.md](./deployment/README.md) - 배포 가이드

cd batch-service-fastapi 
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

cd deployment\docker
docker-compose up -d


## 🛠️ 기술 스택

| 항목 | 기술 | 용도 |
|------|------|------|
| API | FastAPI | Staging CRUD, 배치 작업 |
| Queue | Celery + Redis | 비동기 처리 |
| DB | MySQL | Staging + Main 테이블 |
| ORM | SQLAlchemy | Python ORM |
| Parser | Pandas | 엑셀 처리 |
| Crawler | Playwright | 웹 크롤링 (향후) |

## 🎯 왜 이런 구조?

### ✅ Staging 테이블 분리
- 배치 데이터를 바로 Main에 넣으면 위험
- 관리자 검증 후 승인 필요

### ✅ FastAPI vs Spring Boot 역할 분담
- **FastAPI**: 배치 작업 (비동기 처리)
- **Spring Boot**: CRUD (안정적인 조회)

### ✅ Kubernetes 없이 Docker Compose만
- 모놀리식 구조
- 관리자용 (트래픽 낮음)
- EC2 1대로 충분

## 📝 라이선스

MIT

---

**Made with ❤️ using FastAPI + Celery**
