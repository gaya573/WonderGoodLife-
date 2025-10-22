"""
FastAPI Main Application - Hexagonal Architecture + Celery
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.database import Base, engine
from .presentation.api.car import brands
from .presentation.api.car import models, trims
from .presentation.api.betch import excel, jobs
from .presentation.api.staging import staging, versions
from .presentation.api.staging import simple_search
from .presentation.api.staging.brands import router as staging_brands_router
from .presentation.api.staging.vehicle_lines import router as staging_vehicle_lines_router
from .presentation.api.staging.models import router as staging_models_router
from .presentation.api.staging.trims import router as staging_trims_router
from .presentation.api.staging.options import router as staging_options_router
from .presentation.api.auth import auth, users, permissions
from .presentation.api.event import events
from .presentation.api.main_db import router as main_db_router
from .config import settings

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="Batch Service API (Hexagonal + Celery)",
    description="헥사고날 아키텍처 + Celery 기반 비동기 배치 서비스",
    version="2.0.0"
)

# CORS 설정 (강화)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)  # ✅ 인증 API (로그인, 회원가입)
app.include_router(users.router)  # ✅ 사용자 관리 API
app.include_router(permissions.router)  # ✅ 권한 관리 API
app.include_router(brands.router)
app.include_router(models.router)
app.include_router(trims.router)
app.include_router(excel.router)
app.include_router(jobs.router)  # ✅ 작업 상태 조회 API
app.include_router(staging.router)  # ✅ Staging 데이터 CRUD & 승인 API
app.include_router(versions.router)  # ✅ 간단한 버전 관리 API
app.include_router(events.router)  # ✅ 이벤트 관리 API
app.include_router(simple_search.router)  # ✅ 간단한 검색 API
app.include_router(main_db_router)  # ✅ 메인 DB 현황 API

# Staging CRUD API 라우터들
app.include_router(staging_brands_router)  # ✅ Staging Brands CRUD API
app.include_router(staging_vehicle_lines_router)  # ✅ Staging Vehicle Lines CRUD API
app.include_router(staging_models_router)  # ✅ Staging Models CRUD API
app.include_router(staging_trims_router)  # ✅ Staging Trims CRUD API
app.include_router(staging_options_router)  # ✅ Staging Options CRUD API


@app.get("/")
def root():
    return {
        "message": "Batch Service API - Hexagonal + Celery",
        "version": "2.0.0",
        "architecture": "Ports & Adapters + Async Tasks",
        "features": [
            "Hexagonal Architecture (Clean Architecture)",
            "Celery for Async Task Processing",
            "Redis Message Broker",
            "Excel Import with Progress Tracking",
            "Web Crawling (Coming Soon)"
        ],
        "docs": "/docs",
        "flower": "http://localhost:5555 (Celery Monitoring)"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "architecture": "hexagonal",
        "async_tasks": "celery",
        "message_broker": "redis"
    }
