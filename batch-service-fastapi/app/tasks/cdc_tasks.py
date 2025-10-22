"""
CDC (Change Data Capture) Tasks
새로운 구조에 맞게 수정된 Staging → Main 데이터 전송
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..infrastructure.database import SessionLocal
from ..infrastructure.orm_models import (
    StagingBrandORM, StagingVehicleLineORM, StagingModelORM, StagingTrimORM,
    BrandORM, VehicleLineORM, ModelORM, TrimORM
)
from ..domain.entities import ApprovalStatus
from ..application.use_cases import MigrationService

logger = get_task_logger(__name__)


@shared_task(bind=True, name="migrate_version_to_main")
def migrate_version_to_main(self, version_id: int):
    """
    승인된 버전의 모든 Staging 데이터를 Main 테이블로 전송
    새로운 구조에 맞게 수정
    
    Args:
        version_id: 승인된 버전 ID
    """
    db: Session = SessionLocal()
    
    try:
        from ..infrastructure.repositories import (
            SQLAlchemyStagingVersionRepository,
            SQLAlchemyBrandRepository,
            SQLAlchemyVehicleLineRepository,
            SQLAlchemyModelRepository,
            SQLAlchemyTrimRepository,
            SQLAlchemyStagingBrandRepository,
            SQLAlchemyStagingVehicleLineRepository,
            SQLAlchemyStagingModelRepository,
            SQLAlchemyStagingTrimRepository
        )
        
        # Repository 인스턴스 생성
        version_repo = SQLAlchemyStagingVersionRepository(db)
        brand_repo = SQLAlchemyBrandRepository(db)
        vehicle_line_repo = SQLAlchemyVehicleLineRepository(db)
        model_repo = SQLAlchemyModelRepository(db)
        trim_repo = SQLAlchemyTrimRepository(db)
        
        staging_brand_repo = SQLAlchemyStagingBrandRepository(db)
        staging_vehicle_line_repo = SQLAlchemyStagingVehicleLineRepository(db)
        staging_model_repo = SQLAlchemyStagingModelRepository(db)
        staging_trim_repo = SQLAlchemyStagingTrimRepository(db)
        
        # 버전 확인
        version = version_repo.find_by_id(version_id)
        if not version:
            raise ValueError(f"Version not found: {version_id}")
        
        if version.approval_status != ApprovalStatus.APPROVED:
            raise ValueError(f"Version is not approved: {version_id}")
        
        logger.info(f"Starting migration for version {version_id}: {version.version_name}")
        
        # MigrationService 사용
        migration_service = MigrationService(
            version_repo=version_repo,
            brand_repo=brand_repo,
            vehicle_line_repo=vehicle_line_repo,
            model_repo=model_repo,
            trim_repo=trim_repo,
            staging_brand_repo=staging_brand_repo,
            staging_vehicle_line_repo=staging_vehicle_line_repo,
            staging_model_repo=staging_model_repo,
            staging_trim_repo=staging_trim_repo
        )
        
        # 마이그레이션 실행
        success = migration_service.migrate_approved_version(version_id)
        
        if success:
            # 버전 상태를 MIGRATED로 업데이트
            version.approval_status = ApprovalStatus.MIGRATED
            version_repo.update(version_id, version)
            
            logger.info(f"Migration completed for version {version_id}")
            return {
                "version_id": version_id,
                "success": True,
                "message": f"Version {version.version_name} migrated successfully"
            }
        else:
            raise Exception("Migration failed")
        
    except Exception as e:
        logger.error(f"Migration failed for version {version_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()


@shared_task(bind=True, name="sync_approved_to_main")
def sync_approved_to_main(self, entity_type: str, staging_id: int):
    """
    승인된 Staging 데이터를 Main 테이블로 전송 (개별 엔티티)
    새로운 구조에 맞게 수정
    
    Args:
        entity_type: "brand", "vehicle_line", "model", "trim"
        staging_id: Staging 테이블의 ID
    """
    db: Session = SessionLocal()
    
    try:
        if entity_type == "brand":
            _sync_brand(db, staging_id)
        elif entity_type == "vehicle_line":
            _sync_vehicle_line(db, staging_id)
        elif entity_type == "model":
            _sync_model(db, staging_id)
        elif entity_type == "trim":
            _sync_trim(db, staging_id)
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        logger.info(f"CDC sync completed: {entity_type} ID {staging_id}")
        
    except Exception as e:
        logger.error(f"CDC sync failed: {entity_type} ID {staging_id}, Error: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()


def _sync_brand(db: Session, staging_id: int):
    """Staging Brand → Main Brand"""
    staging = db.query(StagingBrandORM).filter(StagingBrandORM.id == staging_id).first()
    if not staging:
        raise ValueError(f"Staging brand not found: {staging_id}")
    
    if staging.approval_status != ApprovalStatus.APPROVED:
        raise ValueError(f"Brand is not approved: {staging_id}")
    
    # Main 테이블에 같은 이름이 있는지 확인
    existing = db.query(BrandORM).filter(BrandORM.name == staging.name).first()
    
    if existing:
        # 이미 존재하면 업데이트
        existing.country = staging.country
        existing.logo_url = staging.logo_url
        existing.manager = staging.manager
        logger.info(f"Updated existing brand: {existing.id}")
    else:
        # 새로 생성
        main_brand = BrandORM(
            name=staging.name,
            country=staging.country,
            logo_url=staging.logo_url,
            manager=staging.manager
        )
        db.add(main_brand)
        db.flush()  # ID를 얻기 위해 flush
        logger.info(f"Created new brand: {staging.name}")
    
    db.commit()


def _sync_vehicle_line(db: Session, staging_id: int):
    """Staging VehicleLine → Main VehicleLine"""
    staging = db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.id == staging_id).first()
    if not staging:
        raise ValueError(f"Staging vehicle line not found: {staging_id}")
    
    if staging.approval_status != ApprovalStatus.APPROVED:
        raise ValueError(f"Vehicle line is not approved: {staging_id}")
    
    # Brand ID 매핑 (Staging brand_id → Main brand_id)
    staging_brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == staging.brand_id).first()
    if not staging_brand:
        raise ValueError(f"Staging brand not found: {staging.brand_id}")
    
    main_brand = db.query(BrandORM).filter(BrandORM.name == staging_brand.name).first()
    if not main_brand:
        raise ValueError(f"Main brand not found for: {staging_brand.name}")
    
    # Main 테이블에 같은 이름이 있는지 확인
    existing = db.query(VehicleLineORM).filter(
        VehicleLineORM.brand_id == main_brand.id,
        VehicleLineORM.name == staging.name
    ).first()
    
    if existing:
        # 이미 존재하면 업데이트
        existing.description = staging.description
        logger.info(f"Updated existing vehicle line: {existing.id}")
    else:
        # 새로 생성
        main_vehicle_line = VehicleLineORM(
            name=staging.name,
            description=staging.description,
            brand_id=main_brand.id
        )
        db.add(main_vehicle_line)
        db.flush()  # ID를 얻기 위해 flush
        logger.info(f"Created new vehicle line: {staging.name}")
    
    db.commit()


def _sync_model(db: Session, staging_id: int):
    """Staging Model → Main Model"""
    staging = db.query(StagingModelORM).filter(StagingModelORM.id == staging_id).first()
    if not staging:
        raise ValueError(f"Staging model not found: {staging_id}")
    
    if staging.approval_status != ApprovalStatus.APPROVED:
        raise ValueError(f"Model is not approved: {staging_id}")
    
    # VehicleLine ID 매핑
    staging_vehicle_line = db.query(StagingVehicleLineORM).filter(StagingVehicleLineORM.id == staging.vehicle_line_id).first()
    if not staging_vehicle_line:
        raise ValueError(f"Staging vehicle line not found: {staging.vehicle_line_id}")
    
    # Main VehicleLine 찾기
    staging_brand = db.query(StagingBrandORM).filter(StagingBrandORM.id == staging_vehicle_line.brand_id).first()
    if not staging_brand:
        raise ValueError(f"Staging brand not found: {staging_vehicle_line.brand_id}")
    
    main_brand = db.query(BrandORM).filter(BrandORM.name == staging_brand.name).first()
    if not main_brand:
        raise ValueError(f"Main brand not found for: {staging_brand.name}")
    
    main_vehicle_line = db.query(VehicleLineORM).filter(
        VehicleLineORM.brand_id == main_brand.id,
        VehicleLineORM.name == staging_vehicle_line.name
    ).first()
    if not main_vehicle_line:
        raise ValueError(f"Main vehicle line not found for: {staging_vehicle_line.name}")
    
    # Main 테이블에 같은 코드가 있는지 확인
    existing = db.query(ModelORM).filter(ModelORM.code == staging.code).first()
    
    if existing:
        # 이미 존재하면 업데이트
        existing.name = staging.name
        existing.vehicle_line_id = main_vehicle_line.id
        existing.release_year = staging.release_year
        existing.price = staging.price
        existing.foreign = staging.foreign
        logger.info(f"Updated existing model: {existing.id}")
    else:
        # 새로 생성
        main_model = ModelORM(
            name=staging.name,
            code=staging.code,
            vehicle_line_id=main_vehicle_line.id,
            release_year=staging.release_year,
            price=staging.price,
            foreign=staging.foreign
        )
        db.add(main_model)
        db.flush()  # ID를 얻기 위해 flush
        logger.info(f"Created new model: {staging.name}")
    
    db.commit()


def _sync_trim(db: Session, staging_id: int):
    """Staging Trim → Main Trim"""
    staging = db.query(StagingTrimORM).filter(StagingTrimORM.id == staging_id).first()
    if not staging:
        raise ValueError(f"Staging trim not found: {staging_id}")
    
    if staging.approval_status != ApprovalStatus.APPROVED:
        raise ValueError(f"Trim is not approved: {staging_id}")
    
    # Model ID 매핑
    staging_model = db.query(StagingModelORM).filter(StagingModelORM.id == staging.model_id).first()
    if not staging_model:
        raise ValueError(f"Staging model not found: {staging.model_id}")
    
    # Main Model 찾기
    main_model = db.query(ModelORM).filter(ModelORM.code == staging_model.code).first()
    if not main_model:
        raise ValueError(f"Main model not found for code: {staging_model.code}")
    
    # Main 테이블에 같은 이름이 있는지 확인
    existing = db.query(TrimORM).filter(
        TrimORM.model_id == main_model.id,
        TrimORM.name == staging.name
    ).first()
    
    if existing:
        # 이미 존재하면 업데이트
        existing.car_type = staging.car_type
        existing.fuel_name = staging.fuel_name
        existing.cc = staging.cc
        existing.base_price = staging.base_price
        existing.description = staging.description
        logger.info(f"Updated existing trim: {existing.id}")
    else:
        # 새로 생성
        main_trim = TrimORM(
            model_id=main_model.id,
            car_type=staging.car_type,
            name=staging.name,
            fuel_name=staging.fuel_name,
            cc=staging.cc,
            base_price=staging.base_price,
            description=staging.description
        )
        db.add(main_trim)
        db.flush()  # ID를 얻기 위해 flush
        logger.info(f"Created new trim: {staging.name}")
    
    db.commit()


@shared_task(name="cleanup_approved_staging_data")
def cleanup_approved_staging_data():
    """
    승인된 Staging 데이터 정리
    일정 기간 후 삭제 or 아카이빙
    """
    db: Session = SessionLocal()
    
    try:
        # 7일 이상 지난 승인 데이터 삭제
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Brand 정리
        db.query(StagingBrandORM).filter(
            StagingBrandORM.approval_status == ApprovalStatus.APPROVED,
            StagingBrandORM.approved_at < cutoff_date
        ).delete()
        
        # VehicleLine 정리
        db.query(StagingVehicleLineORM).filter(
            StagingVehicleLineORM.approval_status == ApprovalStatus.APPROVED,
            StagingVehicleLineORM.approved_at < cutoff_date
        ).delete()
        
        # Model 정리
        db.query(StagingModelORM).filter(
            StagingModelORM.approval_status == ApprovalStatus.APPROVED,
            StagingModelORM.approved_at < cutoff_date
        ).delete()
        
        # Trim 정리
        db.query(StagingTrimORM).filter(
            StagingTrimORM.approval_status == ApprovalStatus.APPROVED,
            StagingTrimORM.approved_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info("Approved staging data cleanup completed")
        
    finally:
        db.close()


@shared_task(name="sync_pending_approvals")
def sync_pending_approvals():
    """
    PENDING 상태의 Staging 데이터를 주기적으로 체크하여
    승인 조건을 만족하는 데이터를 자동 승인
    """
    db: Session = SessionLocal()
    
    try:
        # PENDING 상태의 버전들 조회
        from ..infrastructure.repositories import SQLAlchemyStagingVersionRepository
        version_repo = SQLAlchemyStagingVersionRepository(db)
        
        pending_versions = version_repo.find_all(approval_status=ApprovalStatus.PENDING.value)
        
        for version in pending_versions:
            # 자동 승인 조건 체크 (예: 특정 시간 경과, 특정 조건 만족 등)
            # 여기서는 단순히 24시간 경과된 버전을 자동 승인하는 예시
            if version.created_at and (datetime.utcnow() - version.created_at).days >= 1:
                version.approval_status = ApprovalStatus.APPROVED
                version.approved_by = "auto_approval_system"
                version_repo.update(version.id, version)
                
                logger.info(f"Auto-approved version: {version.version_name}")
        
        db.commit()
        
    finally:
        db.close()