"""
Dependency Injection - FastAPI 의존성 주입
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.application.auth_service import AuthService, get_auth_service
from app.infrastructure.repositories import (
    SQLAlchemyBrandRepository,
    SQLAlchemyModelRepository,
    SQLAlchemyTrimRepository,
    SQLAlchemyColorRepository,
    SQLAlchemyOptionRepository
)
from ..infrastructure.excel_parser import PandasExcelParser
from ..application.use_cases import (
    BrandService,
    ModelService,
    TrimService,
    ExcelImportService
)


# ===== Repository Dependencies =====
def get_brand_repository(db: Session = Depends(get_db)):
    return SQLAlchemyBrandRepository(db)


def get_model_repository(db: Session = Depends(get_db)):
    return SQLAlchemyModelRepository(db)


def get_trim_repository(db: Session = Depends(get_db)):
    return SQLAlchemyTrimRepository(db)


def get_color_repository(db: Session = Depends(get_db)):
    return SQLAlchemyColorRepository(db)


def get_option_repository(db: Session = Depends(get_db)):
    return SQLAlchemyOptionRepository(db)


# ===== Service Dependencies =====
def get_brand_service(
    repository=Depends(get_brand_repository)
):
    return BrandService(repository)


def get_model_service(
    repository=Depends(get_model_repository)
):
    return ModelService(repository)


def get_trim_service(
    repository=Depends(get_trim_repository)
):
    return TrimService(repository)


def get_excel_import_service(
    db: Session = Depends(get_db)
):
    from ..infrastructure.repositories import (
        SQLAlchemyStagingBrandRepository,
        SQLAlchemyStagingModelRepository,
        SQLAlchemyStagingTrimRepository
    )
    
    excel_parser = PandasExcelParser()
    staging_brand_repo = SQLAlchemyStagingBrandRepository(db)
    staging_model_repo = SQLAlchemyStagingModelRepository(db)
    staging_trim_repo = SQLAlchemyStagingTrimRepository(db)
    
    return ExcelImportService(
        excel_parser=excel_parser,
        staging_brand_repo=staging_brand_repo,
        staging_model_repo=staging_model_repo,
        staging_trim_repo=staging_trim_repo
    )


# ===== Authentication Dependencies =====
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..domain.entities import User

security = HTTPBearer()

def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """현재 사용자 반환 (토큰 검증)"""
    user = auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(
    auth_service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """현재 활성 사용자 반환"""
    user = auth_service.get_current_active_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="활성 사용자가 아닙니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

