"""
Database 설정
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

# SQLAlchemy 엔진 생성 (연결 풀 설정 최적화)
engine = create_engine(
    settings.database_url,
    echo=True,
    # 연결 풀 설정 (설정 파일에서 가져옴)
    pool_size=settings.db_pool_size,          # 기본 연결 풀 크기
    max_overflow=settings.db_max_overflow,    # 오버플로우 연결 수
    pool_timeout=settings.db_pool_timeout,    # 연결 대기 시간
    pool_recycle=settings.db_pool_recycle,    # 연결 재활용 시간
    pool_pre_ping=True,                       # 연결 유효성 검사 활성화
    # 연결 설정
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "connect_timeout": 60,
        "read_timeout": 60,
        "write_timeout": 60
    }
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()


# DB 세션 의존성
def get_db():
    """
    데이터베이스 세션을 안전하게 관리하는 의존성 함수
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # 오류 발생 시 롤백
        db.rollback()
        raise e
    finally:
        # 세션 정리
        db.close()


# 컨텍스트 매니저를 사용한 DB 세션 관리
class DatabaseSession:
    """
    컨텍스트 매니저를 사용한 안전한 데이터베이스 세션 관리
    """
    def __init__(self):
        self.db = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 예외 발생 시 롤백
            self.db.rollback()
        self.db.close()
        return False


# 편의 함수
def get_db_session():
    """
    컨텍스트 매니저를 반환하는 편의 함수
    """
    return DatabaseSession()

