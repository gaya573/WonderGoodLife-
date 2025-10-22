"""
Batch Job API Router - 작업 상태 조회
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import BatchJobORM
from app.domain.entities import JobStatus, JobType
from app.tasks.excel_tasks import process_excel_file
from app.tasks.crawler_tasks import crawl_vehicle_data
from ...schemas import JobResponse, JobCreateRequest, JobListResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/excel/upload", response_model=JobResponse)
async def upload_excel_async(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    엑셀 파일 비동기 처리
    
    1. 파일을 서버에 저장
    2. Celery Task로 작업 등록
    3. Job ID 반환 (클라이언트에서 상태 조회용)
    """
    # 파일 검증
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일이 없습니다")
    
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    try:
        # 파일 내용을 메모리에서 직접 처리 (uploads 폴더 저장 제거)
        contents = await file.read()
        
        # Job 레코드 생성
        job = BatchJobORM(
            job_type=JobType.EXCEL_IMPORT.value,
            status=JobStatus.PENDING.value,
            task_id="",  # 임시로 빈 문자열, 나중에 Celery Task ID로 설정
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        
        # Celery Task 실행 (파일 내용을 직접 전달)
        task = process_excel_file.delay(contents, job.id)
        
        # Celery Task ID 업데이트
        job.task_id = task.id
        db.commit()
        
        return JobResponse(
            id=job.id,
            job_type=job.job_type,
            status=job.status,
            task_id=job.task_id,
            progress=0,
            result=None,
            error_message=None,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")


@router.post("/crawler/start", response_model=JobResponse)
async def start_crawler_job(
    request: JobCreateRequest,
    db: Session = Depends(get_db)
):
    """
    크롤러 작업 시작
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Job 레코드 생성
        job = BatchJobORM(
            id=job_id,
            job_type=JobType.CRAWLER.value,
            status=JobStatus.PENDING.value,
            parameters=request.parameters,
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        
        # Celery Task 실행
        task = crawl_vehicle_data.delay(request.parameters, job_id)
        
        # Task ID 업데이트
        job.celery_task_id = task.id
        db.commit()
        
        return JobResponse(
            id=job.id,
            job_type=job.job_type,
            status=job.status,
            task_id=job.task_id,
            progress=0,
            result=None,
            error_message=None,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"크롤러 작업 시작 실패: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    작업 상태 조회
    """
    try:
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        
        return JobResponse(
            id=job.id,
            job_type=job.job_type,
            status=job.status,
            task_id=job.task_id,
            progress=job.progress or 0,
            result=job.result,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 상태 조회 실패: {str(e)}")


@router.get("/", response_model=JobListResponse)
def list_jobs(
    skip: int = 0,
    limit: int = 20,
    job_type: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    작업 목록 조회
    """
    try:
        query = db.query(BatchJobORM)
        
        if job_type:
            query = query.filter(BatchJobORM.job_type == job_type)
        
        if status:
            query = query.filter(BatchJobORM.status == status)
        
        total_count = query.count()
        jobs = query.order_by(BatchJobORM.created_at.desc()).offset(skip).limit(limit).all()
        
        job_responses = [
            JobResponse(
                id=job.id,
                job_type=job.job_type,
                status=job.status,
                task_id=job.task_id,
                file_path=job.file_path,
                original_filename=job.original_filename,
                progress=job.progress or 0,
                result=job.result,
                error_message=job.error_message,
                created_at=job.created_at,
                updated_at=job.updated_at
            )
            for job in jobs
        ]
        
        return JobListResponse(
            jobs=job_responses,
            total_count=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 목록 조회 실패: {str(e)}")


@router.delete("/{job_id}")
def delete_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    작업 삭제
    """
    try:
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        
        # 파일 저장 로직 제거로 인해 파일 삭제 불필요
        
        db.delete(job)
        db.commit()
        
        return {"message": "작업이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"작업 삭제 실패: {str(e)}")


@router.get("/health/status")
def health_check():
    """
    시스템 상태 확인
    """
    return {
        "status": "healthy",
        "message": "작업 관리 시스템이 정상 작동 중입니다",
        "timestamp": datetime.utcnow().isoformat()
    }