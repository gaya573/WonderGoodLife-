"""
Celery Application - 배치 작업 및 크롤링용
"""
from celery import Celery

# Celery 앱 생성
celery_app = Celery(
    "batch_service",
    broker="redis://redis:6379/0",  # Docker Compose 서비스 이름 사용
    backend="redis://redis:6379/0",  # Docker Compose 서비스 이름 사용
    include=["app.tasks.excel_tasks", "app.tasks.crawler_tasks", "app.tasks.cdc_tasks"]
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
    task_soft_time_limit=25 * 60,  # 25분
)

# 스케줄링 예시 (Celery Beat)
celery_app.conf.beat_schedule = {
    # 예: 매일 새벽 2시 크롤링 실행
    # "crawl-every-night": {
    #     "task": "app.tasks.crawler_tasks.crawl_vehicle_data",
    #     "schedule": crontab(hour=2, minute=0),
    # },
}

