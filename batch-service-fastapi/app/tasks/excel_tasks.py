"""
Excel Processing Tasks - Celery로 비동기 처리
새로운 구조에 맞게 수정
"""
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import pandas as pd
from io import BytesIO

from ..celery_app import celery_app
from ..infrastructure.database import SessionLocal
from ..infrastructure.orm_models import BatchJobORM
from ..domain.entities import JobStatus, ApprovalStatus
from ..application.use_cases import ExcelImportService
from ..infrastructure.repositories import (
    SQLAlchemyStagingVersionRepository,
    SQLAlchemyStagingBrandRepository,
    SQLAlchemyStagingVehicleLineRepository,
    SQLAlchemyStagingModelRepository,
    SQLAlchemyStagingTrimRepository,
    SQLAlchemyStagingOptionRepository
)
from ..infrastructure.excel_parser import PandasExcelParser

logger = get_task_logger(__name__)


@celery_app.task(name="process_excel_file_for_version", bind=True)
def process_excel_file_for_version(self, job_id: int, file_path: str, version_id: int, country: str):
    """
    버전별 엑셀 파일 비동기 처리 - 새로운 구조
    
    Args:
        job_id: BatchJob ID
        file_path: 업로드된 파일 경로
        version_id: 버전 ID
        country: 브랜드 국가 코드
    """
    db: Session = SessionLocal()
    
    # 중복 실행 방지
    task_id = self.request.id
    logger.info(f"Starting Excel processing task: {task_id} for job: {job_id}")
    
    try:
        # 버전 확인
        version_repo = SQLAlchemyStagingVersionRepository(db)
        version = version_repo.find_by_id(version_id)
        if not version:
            raise ValueError(f"Version not found: {version_id}")
        
        if version.approval_status != ApprovalStatus.PENDING:
            raise ValueError(f"Only PENDING versions can be processed: {version.approval_status}")
        
        # 작업 상태 업데이트: PROCESSING
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Processing Excel file for version {version_id}: {file_path} (Job ID: {job_id})")
        
        # 파일 읽기
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 새로운 구조의 Repository들 생성
        excel_parser = PandasExcelParser()
        staging_brand_repo = SQLAlchemyStagingBrandRepository(db)
        staging_vehicle_line_repo = SQLAlchemyStagingVehicleLineRepository(db)
        staging_model_repo = SQLAlchemyStagingModelRepository(db)
        staging_trim_repo = SQLAlchemyStagingTrimRepository(db)
        staging_option_repo = SQLAlchemyStagingOptionRepository(db)  # 새로운 통합 옵션 레포지토리
        staging_option_repo = SQLAlchemyStagingOptionRepository(db)
        
        # ExcelImportService 사용하여 처리 (통합된 옵션 구조)
        service = ExcelImportService(
            excel_parser=excel_parser,
            db=db,  # SQLAlchemy 세션 추가
            version_repo=version_repo,
            staging_brand_repo=staging_brand_repo,
            staging_vehicle_line_repo=staging_vehicle_line_repo,
            staging_model_repo=staging_model_repo,
            staging_trim_repo=staging_trim_repo,
            staging_option_repo=staging_option_repo  # 통합된 옵션 레포지토리
        )
        
        # 비동기 처리를 동기로 실행 (Celery Worker 내부에서)
        import asyncio
        result = asyncio.run(service.import_excel(file_content, country, version_id, "batch_service"))
        
        # 작업 완료 상태 업데이트
        job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.total_rows = result.total_rows
        job.processed_rows = result.processed_rows
        job.result_data = {
            "success": result.success,
            "message": result.message,
            "brand_count": result.brand_count,
            "vehicle_line_count": result.vehicle_line_count,
            "model_count": result.model_count,
            "trim_count": result.trim_count,
            "option_count": result.option_count,
            "errors": result.errors,
            "version_id": version_id
        }
        
        if not result.success:
            job.error_message = result.message
        
        db.commit()
        
        logger.info(f"Excel processing completed for version {version_id}: Job ID {job_id}")
        
        return {
            "job_id": job_id,
            "version_id": version_id,
            "success": result.success,
            "message": result.message,
            "total_rows": result.total_rows,
            "processed_rows": result.processed_rows,
            "brand_count": result.brand_count,
            "vehicle_line_count": result.vehicle_line_count,
            "model_count": result.model_count,
            "trim_count": result.trim_count,
            "option_count": result.option_count
        }
        
    except Exception as e:
        logger.error(f"Excel processing failed for version {version_id}: {str(e)}")
        
        # 작업 실패 상태 업데이트
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            db.commit()
        
        # 재시도 (최대 1회만)
        raise process_excel_file_for_version.retry(exc=e, countdown=200, max_retries=1)
        
    finally:
        db.close()


@celery_app.task(bind=True, name="process_excel_file")
def process_excel_file(self, file_content: bytes, job_id: int, version_id: int = None, country: str = "KR"):
    """
    엑셀 파일 비동기 처리 (버전별 지원)
    
    Args:
        file_content: 파일 내용 (bytes)
        job_id: Job ID (정수)
        version_id: 버전 ID (선택사항)
        country: 브랜드 국가 코드
    """
    db: Session = SessionLocal()
    
    try:
        # 작업 상태 업데이트: PROCESSING (job_id로 조회)
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if not job:
            raise ValueError(f"Job not found with id: {job_id}")
        
        # task_id가 빈 문자열인 경우 현재 Celery Task ID로 업데이트
        if not job.task_id or job.task_id == "":
            job.task_id = self.request.id
            db.commit()
        
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Processing Excel file for job: {job.id}, version: {version_id}")
        
        # 버전 처리
        version_repo = SQLAlchemyStagingVersionRepository(db)
        if version_id:
            # 특정 버전에 업로드
            version = version_repo.find_by_id(version_id)
            if not version:
                raise ValueError(f"Version not found: {version_id}")
            
            if version.approval_status != ApprovalStatus.PENDING:
                raise ValueError(f"Only PENDING versions can be processed: {version.approval_status}")
            
            target_version_id = version_id
        else:
            # 임시 버전 생성 (레거시 지원)
            target_version_id = 0  # 임시 버전 ID
        
        # 새로운 구조의 Repository들 생성
        excel_parser = PandasExcelParser()
        staging_brand_repo = SQLAlchemyStagingBrandRepository(db)
        staging_vehicle_line_repo = SQLAlchemyStagingVehicleLineRepository(db)
        staging_model_repo = SQLAlchemyStagingModelRepository(db)
        staging_trim_repo = SQLAlchemyStagingTrimRepository(db)
        staging_option_repo = SQLAlchemyStagingOptionRepository(db)  # 새로운 통합 옵션 레포지토리
        staging_option_repo = SQLAlchemyStagingOptionRepository(db)
        
        # ExcelImportService 사용하여 처리 (통합된 옵션 구조)
        service = ExcelImportService(
            excel_parser=excel_parser,
            db=db,  # SQLAlchemy 세션 추가
            version_repo=version_repo,
            staging_brand_repo=staging_brand_repo,
            staging_vehicle_line_repo=staging_vehicle_line_repo,
            staging_model_repo=staging_model_repo,
            staging_trim_repo=staging_trim_repo,
            staging_option_repo=staging_option_repo  # 통합된 옵션 레포지토리
        )
        
        # 비동기 처리를 동기로 실행 (Celery Worker 내부에서)
        import asyncio
        result = asyncio.run(service.import_excel(file_content, country, target_version_id, "batch_service"))
        
        # 작업 완료 상태 업데이트
        job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.total_rows = result.total_rows
        job.processed_rows = result.processed_rows
        job.result_data = {
            "success": result.success,
            "message": result.message,
            "brand_count": result.brand_count,
            "vehicle_line_count": result.vehicle_line_count,
            "model_count": result.model_count,
            "trim_count": result.trim_count,
            "option_count": result.option_count,
            "errors": result.errors,
            "version_id": target_version_id
        }
        
        if not result.success:
            job.error_message = result.message
        
        db.commit()
        
        logger.info(f"Excel processing completed: Job ID {job.id}")
        
        return {
            "job_id": job.id,
            "version_id": target_version_id,
            "success": result.success,
            "message": result.message,
            "total_rows": result.total_rows,
            "processed_rows": result.processed_rows,
            "brand_count": result.brand_count,
            "vehicle_line_count": result.vehicle_line_count,
            "model_count": result.model_count,
            "trim_count": result.trim_count,
            "option_count": result.option_count
        }
        
    except Exception as e:
        logger.error(f"Excel processing failed: {str(e)}")
        
        # 작업 실패 상태 업데이트
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            db.commit()
        
        # 재시도 (최대 1회만)
        raise self.retry(exc=e, countdown=120, max_retries=1)
        
    finally:
        db.close()


@celery_app.task(bind=True, name="update_job_progress")
def update_job_progress(self, job_id: int, processed_rows: int):
    """
    작업 진행 상황 업데이트
    
    Args:
        job_id: BatchJob ID
        processed_rows: 처리된 행 수
    """
    db: Session = SessionLocal()
    
    try:
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if job:
            job.processed_rows = processed_rows
            db.commit()
            logger.info(f"Job {job_id} progress: {processed_rows} rows processed")
    finally:
        db.close()


@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files(file_path: str):
    """
    임시 파일 정리
    
    Args:
        file_path: 삭제할 파일 경로
    """
    import os
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Temporary file cleaned up: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup temporary file {file_path}: {str(e)}")