"""
Web Crawling Tasks - 크롤링 배치 작업
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
from datetime import datetime

from ..infrastructure.database import SessionLocal
from ..infrastructure.orm_models import BatchJobORM
from ..domain.entities import JobStatus

logger = get_task_logger(__name__)


@shared_task(bind=True, name="crawl_vehicle_data")
def crawl_vehicle_data(self, job_id: int, target_url: str):
    """
    차량 정보 크롤링 배치 작업
    
    Args:
        job_id: BatchJob ID
        target_url: 크롤링 대상 URL
    """
    db: Session = SessionLocal()
    
    try:
        # 작업 상태 업데이트: PROCESSING
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting crawling: {target_url} (Job ID: {job_id})")
        
        # TODO: Playwright를 사용한 크롤링 구현
        # from playwright.sync_api import sync_playwright
        # 
        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     page = browser.new_page()
        #     page.goto(target_url)
        #     
        #     # 데이터 추출
        #     vehicles = page.query_selector_all('.vehicle-item')
        #     
        #     for vehicle in vehicles:
        #         # 차량 정보 추출 및 DB 저장
        #         pass
        #     
        #     browser.close()
        
        # 임시 구현
        logger.info("Crawling implementation pending...")
        
        # 작업 완료
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_data = {
            "success": True,
            "message": "크롤링 완료 (구현 예정)",
            "url": target_url
        }
        db.commit()
        
        logger.info(f"Crawling completed: Job ID {job_id}")
        
        return {
            "job_id": job_id,
            "success": True,
            "message": "크롤링 완료"
        }
        
    except Exception as e:
        logger.error(f"Crawling failed: {str(e)}")
        
        # 작업 실패 상태 업데이트
        job = db.query(BatchJobORM).filter(BatchJobORM.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            db.commit()
        
        # 재시도
        raise self.retry(exc=e, countdown=300, max_retries=5)
        
    finally:
        db.close()


@shared_task(name="scheduled_daily_crawl")
def scheduled_daily_crawl():
    """
    스케줄된 일일 크롤링
    Celery Beat으로 자동 실행
    """
    db: Session = SessionLocal()
    
    try:
        # 새 Job 생성
        from ..domain.entities import JobType
        import uuid
        
        job = BatchJobORM(
            job_type=JobType.WEB_CRAWLING,
            status=JobStatus.PENDING,
            task_id=str(uuid.uuid4()),
            created_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # 크롤링 Task 실행
        crawl_vehicle_data.delay(job.id, "https://example.com")
        
        logger.info(f"Scheduled daily crawl started: Job ID {job.id}")
        
    finally:
        db.close()
