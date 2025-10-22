from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database (MySQL)
    database_url: str = "mysql+pymysql://wondergoodlife_user:wondergoodlife_pass123@localhost:3306/wondergoodlife_db"
    
    # Database Connection Pool Settings
    db_pool_size: int = 5          # 기본 연결 풀 크기
    db_max_overflow: int = 10      # 오버플로우 연결 수
    db_pool_timeout: int = 30      # 연결 대기 시간 (초)
    db_pool_recycle: int = 3600    # 연결 재활용 시간 (초)
    
    # Celery & Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    SECRET_KEY: str = "GOODLIFE_SECRET1_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
    
    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "./uploads"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
