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
        
        # 1. 메인 서비스 마이그레이션 실행
        success = migration_service.migrate_approved_version(version_id)
        
        if not success:
            raise Exception("Main service migration failed")
        
        logger.info(f"Main service migration completed for version {version_id}")
        
        # 2. 할인 정책 마이그레이션 실행
        discount_policy_result = _migrate_discount_policies(db, version_id)
        
        logger.info(f"Discount policy migration completed for version {version_id}")
        
        # 3. 버전 상태를 MIGRATED로 업데이트
        version.approval_status = ApprovalStatus.MIGRATED
        version_repo.update(version_id, version)
        
        logger.info(f"Migration completed for version {version_id}")
        return {
            "version_id": version_id,
            "success": True,
            "message": f"Version {version.version_name} migrated successfully",
            "main_service": {
                "success": True,
                "message": "Main service migrated successfully"
            },
            "discount_policy": discount_policy_result
        }
        
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


@shared_task(bind=True, name="migrate_discount_policies_to_main")
def migrate_discount_policies_to_main(self, version_id: int):
    """
    승인된 버전의 모든 Staging 할인 정책을 Main 테이블로 전송
    전략: 기존 데이터를 모두 삭제하고 다시 삽입
    
    Args:
        version_id: 승인된 버전 ID
    """
    db: Session = SessionLocal()
    
    try:
        result = _migrate_discount_policies(db, version_id)
        return result
    except Exception as e:
        logger.error(f"Discount policy migration failed for version {version_id}: {str(e)}")
        db.rollback()
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        db.close()


def _migrate_discount_policies(db: Session, version_id: int):
    """
    할인 정책 마이그레이션 헬퍼 함수
    
    Args:
        db: 데이터베이스 세션
        version_id: 버전 ID
    
    Returns:
        dict: 마이그레이션 결과
    """
    from ..infrastructure.orm_models import (
        StagingDiscountPolicyORM, StagingBrandCardBenefitORM, StagingBrandPromoORM,
        StagingBrandInventoryDiscountORM, StagingBrandPrePurchaseORM,
        DiscountPolicyORM, BrandCardBenefitORM, BrandPromoORM,
        BrandInventoryDiscountORM, BrandPrePurchaseORM,
        StagingBrandORM, StagingVehicleLineORM, StagingTrimORM,
        BrandORM, VehicleLineORM, TrimORM
    )
    
    logger.info(f"Starting discount policy migration for version {version_id}")
    
    # 1. 기존 Main 할인 정책 모두 삭제
    logger.info("Deleting all existing discount policies...")
    db.query(BrandPrePurchaseORM).delete()
    db.query(BrandInventoryDiscountORM).delete()
    db.query(BrandPromoORM).delete()
    db.query(BrandCardBenefitORM).delete()
    db.query(DiscountPolicyORM).delete()
    db.commit()
    
    # 2. Staging 할인 정책 조회
    staging_policies = db.query(StagingDiscountPolicyORM).filter_by(version_id=version_id).all()
    
    if not staging_policies:
        logger.info(f"No discount policies found for version {version_id}")
        return {
            "success": True,
            "message": "No discount policies to migrate",
            "stats": {
                "policies": 0,
                "card_benefits": 0,
                "promos": 0,
                "inventory_discounts": 0,
                "pre_purchases": 0
            }
        }
    
    policy_count = 0
    card_benefit_count = 0
    promo_count = 0
    inventory_discount_count = 0
    pre_purchase_count = 0
    
    for staging_policy in staging_policies:
        # 3. Staging에서 Main으로 ID 매핑
        # Brand ID 매핑
        staging_brand = db.query(StagingBrandORM).filter_by(id=staging_policy.brand_id).first()
        if not staging_brand:
            logger.warning(f"Skipping policy {staging_policy.id}: Staging brand not found")
            continue
            
        main_brand = db.query(BrandORM).filter_by(name=staging_brand.name).first()
        
        # Vehicle Line ID 매핑
        staging_vehicle_line = db.query(StagingVehicleLineORM).filter_by(id=staging_policy.vehicle_line_id).first()
        if not staging_vehicle_line:
            logger.warning(f"Skipping policy {staging_policy.id}: Staging vehicle line not found")
            continue
            
        main_vehicle_line = db.query(VehicleLineORM).filter_by(
            brand_id=main_brand.id,
            name=staging_vehicle_line.name
        ).first()
        
        # Trim ID 매핑
        staging_trim = db.query(StagingTrimORM).filter_by(id=staging_policy.trim_id).first()
        if not staging_trim:
            logger.warning(f"Skipping policy {staging_policy.id}: Staging trim not found")
            continue
            
        main_trim = db.query(TrimORM).filter_by(
            model_id=main_vehicle_line.id,  # vehicle_line을 통해 모델 찾기
            name=staging_trim.name
        ).first()
        
        if not main_brand or not main_vehicle_line or not main_trim:
            logger.warning(f"Skipping policy {staging_policy.id}: Could not find main references")
            continue
        
        # 4. Main 할인 정책 생성
        main_policy = DiscountPolicyORM(
            brand_id=main_brand.id,
            vehicle_line_id=main_vehicle_line.id,
            trim_id=main_trim.id,
            policy_type=staging_policy.policy_type,
            title=staging_policy.title,
            description=staging_policy.description,
            valid_from=staging_policy.valid_from,
            valid_to=staging_policy.valid_to,
            is_active=staging_policy.is_active
        )
        db.add(main_policy)
        db.flush()
        policy_count += 1
        
        # 5. 정책 유형별 세부 정보 마이그레이션
        if staging_policy.policy_type == "CARD_BENEFIT":
            card_benefits = db.query(StagingBrandCardBenefitORM).filter_by(
                discount_policy_id=staging_policy.id
            ).all()
            
            for card_benefit in card_benefits:
                main_card_benefit = BrandCardBenefitORM(
                    discount_policy_id=main_policy.id,
                    card_partner=card_benefit.card_partner,
                    cashback_rate=card_benefit.cashback_rate,
                    title=card_benefit.title,
                    description=card_benefit.description,
                    valid_from=card_benefit.valid_from,
                    valid_to=card_benefit.valid_to,
                    is_active=card_benefit.is_active
                )
                db.add(main_card_benefit)
                card_benefit_count += 1
        
        elif staging_policy.policy_type == "BRAND_PROMO":
            promos = db.query(StagingBrandPromoORM).filter_by(
                discount_policy_id=staging_policy.id
            ).all()
            
            for promo in promos:
                main_promo = BrandPromoORM(
                    discount_policy_id=main_policy.id,
                    discount_rate=promo.discount_rate,
                    discount_amount=promo.discount_amount,
                    title=promo.title,
                    description=promo.description,
                    valid_from=promo.valid_from,
                    valid_to=promo.valid_to,
                    is_active=promo.is_active
                )
                db.add(main_promo)
                promo_count += 1
        
        elif staging_policy.policy_type == "INVENTORY":
            inventory_discounts = db.query(StagingBrandInventoryDiscountORM).filter_by(
                discount_policy_id=staging_policy.id
            ).all()
            
            for inventory_discount in inventory_discounts:
                main_inventory_discount = BrandInventoryDiscountORM(
                    discount_policy_id=main_policy.id,
                    inventory_level_threshold=inventory_discount.inventory_level_threshold,
                    discount_rate=inventory_discount.discount_rate,
                    title=inventory_discount.title,
                    description=inventory_discount.description,
                    valid_from=inventory_discount.valid_from,
                    valid_to=inventory_discount.valid_to,
                    is_active=inventory_discount.is_active
                )
                db.add(main_inventory_discount)
                inventory_discount_count += 1
        
        elif staging_policy.policy_type == "PRE_PURCHASE":
            pre_purchases = db.query(StagingBrandPrePurchaseORM).filter_by(
                discount_policy_id=staging_policy.id
            ).all()
            
            for pre_purchase in pre_purchases:
                main_pre_purchase = BrandPrePurchaseORM(
                    discount_policy_id=main_policy.id,
                    event_type=pre_purchase.event_type,
                    discount_rate=pre_purchase.discount_rate,
                    discount_amount=pre_purchase.discount_amount,
                    title=pre_purchase.title,
                    description=pre_purchase.description,
                    pre_purchase_start=pre_purchase.pre_purchase_start,
                    valid_from=pre_purchase.valid_from,
                    valid_to=pre_purchase.valid_to,
                    is_active=pre_purchase.is_active
                )
                db.add(main_pre_purchase)
                pre_purchase_count += 1
    
    # 6. 커밋
    db.commit()
    
    logger.info(f"Discount policy migration completed for version {version_id}")
    logger.info(f"Migrated: {policy_count} policies, {card_benefit_count} card benefits, "
               f"{promo_count} promos, {inventory_discount_count} inventory discounts, "
               f"{pre_purchase_count} pre-purchases")
    
    return {
        "success": True,
        "message": f"Discount policies migrated successfully",
        "stats": {
            "policies": policy_count,
            "card_benefits": card_benefit_count,
            "promos": promo_count,
            "inventory_discounts": inventory_discount_count,
            "pre_purchases": pre_purchase_count
        }
    }