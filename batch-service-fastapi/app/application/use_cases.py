"""
Use Cases - 비즈니스 유스케이스 (애플리케이션 서비스)
새로운 테이블 구조에 맞게 재작성
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from ..domain.entities import (
    Brand, Model, Trim, CarType, VehicleLine,
    StagingBrand, StagingModel, StagingTrim, StagingVehicleLine,
    StagingOption, StagingVersion,
    ApprovalStatus
)
from .ports import (
    BrandRepository, ModelRepository, TrimRepository,
    ColorRepository, OptionRepository, ExcelParser
)


@dataclass
class ImportResult:
    """엑셀 임포트 결과"""
    success: bool
    message: str
    total_rows: int
    processed_rows: int
    brand_count: int
    vehicle_line_count: int
    model_count: int
    trim_count: int
    option_count: int
    errors: List[str]


# ===== Brand Use Cases =====
class BrandService:
    """브랜드 관리 유스케이스"""
    
    def __init__(self, repository: BrandRepository):
        self.repository = repository
    
    def get_all_brands(self, skip: int = 0, limit: int = 100) -> List[Brand]:
        return self.repository.find_all(skip, limit)
    
    def get_brand_by_id(self, brand_id: int) -> Optional[Brand]:
        return self.repository.find_by_id(brand_id)
    
    def create_brand(self, brand: Brand) -> Brand:
        brand.validate()
        return self.repository.save(brand)
    
    def update_brand(self, brand_id: int, brand: Brand) -> Optional[Brand]:
        brand.validate()
        return self.repository.update(brand_id, brand)
    
    def delete_brand(self, brand_id: int) -> bool:
        return self.repository.delete(brand_id)


# ===== Vehicle Line Use Cases =====
class VehicleLineService:
    """차량 라인 관리 유스케이스"""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_all_by_brand(self, brand_id: int) -> List[VehicleLine]:
        return self.repository.find_all_by_brand(brand_id)
    
    def get_vehicle_line_by_id(self, vehicle_line_id: int) -> Optional[VehicleLine]:
        return self.repository.find_by_id(vehicle_line_id)
    
    def create_vehicle_line(self, vehicle_line: VehicleLine) -> VehicleLine:
        return self.repository.save(vehicle_line)


# ===== Model Use Cases =====
class ModelService:
    """모델 관리 유스케이스"""
    
    def __init__(self, repository: ModelRepository):
        self.repository = repository
    
    def get_all_models(self, skip: int = 0, limit: int = 100) -> List[Model]:
        return self.repository.find_all(skip, limit)
    
    def get_all_by_vehicle_line(self, vehicle_line_id: int) -> List[Model]:
        return self.repository.find_all_by_vehicle_line(vehicle_line_id)
    
    def get_model_by_id(self, model_id: int) -> Optional[Model]:
        return self.repository.find_by_id(model_id)
    
    def create_model(self, model: Model) -> Model:
        model.validate()
        return self.repository.save(model)
    
    def update_model(self, model_id: int, model: Model) -> Optional[Model]:
        model.validate()
        return self.repository.update(model_id, model)
    
    def delete_model(self, model_id: int) -> bool:
        return self.repository.delete(model_id)


# ===== Trim Use Cases =====
class TrimService:
    """트림 관리 유스케이스"""
    
    def __init__(self, repository: TrimRepository):
        self.repository = repository
    
    def get_all_trims(self, model_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Trim]:
        return self.repository.find_all(model_id, skip, limit)
    
    def get_all_by_model(self, model_id: int) -> List[Trim]:
        return self.repository.find_all_by_model(model_id)
    
    def get_trim_by_id(self, trim_id: int) -> Optional[Trim]:
        return self.repository.find_by_id(trim_id)
    
    def create_trim(self, trim: Trim) -> Trim:
        trim.validate()
        return self.repository.save(trim)
    
    def update_trim(self, trim_id: int, trim: Trim) -> Optional[Trim]:
        trim.validate()
        return self.repository.update(trim_id, trim)
    
    def delete_trim(self, trim_id: int) -> bool:
        return self.repository.delete(trim_id)


# ===== Version Management Use Cases =====
class VersionService:
    """버전 관리 유스케이스"""
    
    def __init__(self, version_repo, staging_brand_repo, staging_vehicle_line_repo, 
                 staging_model_repo, staging_trim_repo, staging_option_repo):
        self.version_repo = version_repo
        self.staging_brand_repo = staging_brand_repo
        self.staging_vehicle_line_repo = staging_vehicle_line_repo
        self.staging_model_repo = staging_model_repo
        self.staging_trim_repo = staging_trim_repo
        self.staging_option_repo = staging_option_repo
    
    def create_version(self, version_name: str, description: str, created_by: str) -> StagingVersion:
        """새 버전 생성"""
        version = StagingVersion(
            version_name=version_name,
            description=description,
            created_by=created_by,
            approval_status=ApprovalStatus.PENDING
        )
        version.validate()
        return self.version_repo.save(version)
    
    def get_version_by_id(self, version_id: int) -> Optional[StagingVersion]:
        """버전 조회"""
        return self.version_repo.find_by_id(version_id)
    
    def get_all_versions(self, skip: int = 0, limit: int = 100, approval_status: Optional[str] = None) -> List[StagingVersion]:
        """버전 목록 조회"""
        return self.version_repo.find_all(skip, limit, approval_status)
    
    def approve_version(self, version_id: int, approved_by: str) -> bool:
        """버전 승인"""
        version = self.version_repo.find_by_id(version_id)
        if not version:
            return False
        
        version.approval_status = ApprovalStatus.APPROVED
        version.approved_by = approved_by
        version.approved_at = datetime.utcnow()
        
        updated_version = self.version_repo.update(version_id, version)
        return updated_version is not None
    
    def reject_version(self, version_id: int, rejected_by: str, rejection_reason: str) -> bool:
        """버전 거부"""
        version = self.version_repo.find_by_id(version_id)
        if not version:
            return False
        
        version.approval_status = ApprovalStatus.REJECTED
        version.rejected_by = rejected_by
        version.rejected_at = datetime.utcnow()
        version.rejection_reason = rejection_reason
        
        updated_version = self.version_repo.update(version_id, version)
        return updated_version is not None


# ===== Excel Import Use Case (새로운 구조) =====
class ExcelImportService:
    """엑셀 임포트 유스케이스 - 새로운 구조에 맞게 재작성"""
    
    def __init__(
        self,
        excel_parser: ExcelParser,
        db,  # SQLAlchemy Session
        version_repo,  # StagingVersionRepository
        staging_brand_repo,  # StagingBrandRepository
        staging_vehicle_line_repo,  # StagingVehicleLineRepository
        staging_model_repo,  # StagingModelRepository
        staging_trim_repo,   # StagingTrimRepository
        staging_option_repo,  # StagingOptionRepository (통합된 옵션)
    ):
        self.excel_parser = excel_parser
        self.db = db
        self.version_repo = version_repo
        self.staging_brand_repo = staging_brand_repo
        self.staging_vehicle_line_repo = staging_vehicle_line_repo
        self.staging_model_repo = staging_model_repo
        self.staging_trim_repo = staging_trim_repo
        self.staging_option_repo = staging_option_repo  # 통합된 옵션 레포지토리
    
    async def import_excel(self, file_content: bytes, country: str, version_id: int, created_by: str) -> ImportResult:
        """
        엑셀 파일 임포트 - 한 줄씩 순차 처리로 완벽한 데이터 추출
        
        처리 방식:
        1. 엑셀을 파싱하여 브랜드별 데이터 획득
        2. 각 브랜드의 모든 행을 순차적으로 처리
        3. 각 행의 RowType에 따라 TRIM 또는 OPTION 처리
        4. 필요한 엔티티들을 즉시 생성하여 참조 관계 유지
        """
        # 통계 초기화
        stats = {
            'brand_count': 0,
            'vehicle_line_count': 0, 
            'model_count': 0,
            'trim_count': 0,
            'option_count': 0,
            'processed_rows': 0,
            'total_rows': 0
        }
        errors = []
        
        try:
            # 1. 버전 존재 확인
            version = self.version_repo.find_by_id(version_id)
            if not version:
                return self._create_error_result(f"버전 ID {version_id}를 찾을 수 없습니다")
            
            # 2. 엑셀 파싱
            brand_data = await self.excel_parser.parse(file_content)
            if not brand_data:
                return self._create_error_result("엑셀 파일에 데이터가 없습니다")
            
            stats['total_rows'] = sum(len(records) for records in brand_data.values())
            
            # 3. 각 브랜드별 순차 처리
            for brand_name, records in brand_data.items():
                try:
                    # 브랜드 생성 및 캐시 초기화
                    staging_brand = self._create_staging_brand(brand_name, country, version_id, created_by)
                    stats['brand_count'] += 1
                    
                    # 엔티티 캐시 (중복 생성 방지)
                    entity_cache = {
                        'vehicle_lines': {},  # {vehicle_line_name: StagingVehicleLine}
                        'models': {},         # {model_name: StagingModel}
                        'trims': {}           # {trim_name: StagingTrim}
                    }
                    
                    # 이전 행의 차량명과 모델명을 기억
                    last_vehicle_name = None
                    last_model_name = None
                    
                    # 4. 모든 행을 배치로 처리 (성능 최적화)
                    batch_size = 100  # 100개씩 배치 처리
                    total_records = len(records)
                    
                    for batch_start in range(0, total_records, batch_size):
                        batch_end = min(batch_start + batch_size, total_records)
                        batch_records = records[batch_start:batch_end]
                        
                        print(f"[INFO] 배치 처리 중: {batch_start + 1}-{batch_end}/{total_records} 행")
                        
                        for row_index, record in enumerate(batch_records):
                            actual_row_index = batch_start + row_index
                            try:
                                # 진행 상황 로깅 (매 50행마다)
                                if actual_row_index % 50 == 0:
                                    print(f"[INFO] 진행률: {actual_row_index + 1}/{total_records} ({((actual_row_index + 1)/total_records)*100:.1f}%)")
                                
                                result = self._process_single_row(
                                    record, staging_brand, entity_cache, created_by, actual_row_index,
                                    last_vehicle_name, last_model_name
                                )
                                
                                # 처리된 행에서 차량명과 모델명 업데이트
                                if record.get('차량명'):
                                    last_vehicle_name = record.get('차량명')
                                if record.get('Model'):
                                    last_model_name = record.get('Model')
                                
                                # 처리 결과에 따라 통계 업데이트
                                if result.get('vehicle_line_created', False):
                                    stats['vehicle_line_count'] += 1
                                if result.get('model_created', False):
                                    stats['model_count'] += 1
                                if result['type'] == 'trim' and result['created']:
                                    stats['trim_count'] += 1
                                elif result['type'] == 'option' and result['created']:
                                    stats['option_count'] += 1
                                
                                stats['processed_rows'] += 1
                                
                            except Exception as e:
                                error_msg = f"행 {actual_row_index + 1} 처리 실패 [{brand_name}]: {str(e)}"
                                print(f"[ERROR] {error_msg}")
                                errors.append(error_msg)
                        
                        # 배치 완료 후 커밋 (성능 최적화)
                        try:
                            self.db.commit()
                            print(f"[INFO] 배치 {batch_start + 1}-{batch_end} 커밋 완료")
                        except Exception as e:
                            print(f"[ERROR] 배치 커밋 실패: {str(e)}")
                            self.db.rollback()
                
                except Exception as e:
                    errors.append(f"브랜드 처리 실패 [{brand_name}]: {str(e)}")
            
            # 5. 버전 통계 업데이트
            self._update_version_stats(version_id, stats['brand_count'], stats['model_count'], stats['trim_count'])
            
            # 6. 결과 반환
            return ImportResult(
                success=len(errors) == 0,
                message=self._create_success_message(stats) if len(errors) == 0 else "일부 오류 발생",
                total_rows=stats['total_rows'],
                processed_rows=stats['processed_rows'],
                brand_count=stats['brand_count'],
                vehicle_line_count=stats['vehicle_line_count'],
                model_count=stats['model_count'],
                trim_count=stats['trim_count'],
                option_count=stats['option_count'],
                errors=errors
            )
        
        except Exception as e:
            return self._create_error_result(f"파일 처리 실패: {str(e)}")
    
    def _process_single_row(self, record: dict, staging_brand: StagingBrand, 
                           entity_cache: dict, created_by: str, row_index: int = 0,
                           last_vehicle_name: str = None, last_model_name: str = None) -> dict:
        """
        단일 행 처리 - RowType에 따라 TRIM 또는 OPTION 처리
        
        Args:
            record: 엑셀 행 데이터
            staging_brand: 현재 브랜드 엔티티
            entity_cache: 엔티티 캐시 (중복 생성 방지)
            created_by: 생성자 정보
            
        Returns:
            dict: 처리 결과 정보
        """
        row_type = record.get('RowType', '').strip()
        
        # 차량명 처리: 비어있으면 이전 행의 차량명 사용
        vehicle_name = record.get('차량명') or ''
        vehicle_name = vehicle_name.strip() if vehicle_name else ''
        if not vehicle_name and last_vehicle_name:
            vehicle_name = last_vehicle_name
            print(f"[DEBUG] 차량명이 비어있어서 이전 차량명 사용: {vehicle_name}")
        
        # 모델명 처리: 비어있으면 이전 행의 모델명 사용
        model_name = record.get('Model') or ''
        model_name = model_name.strip() if model_name else ''
        if not model_name and last_model_name:
            model_name = last_model_name
            print(f"[DEBUG] 모델명이 비어있어서 이전 모델명 사용: {model_name}")
        
        # 디버그 로깅 최소화 (성능 최적화)
        if row_index % 100 == 0:  # 매 100행마다만 로깅
            print(f"[DEBUG] _process_single_row 시작 - RowType: {row_type}, 차량명: {vehicle_name}, 모델: {model_name}")
        
        # 필수 데이터 검증
        if not vehicle_name:
            raise ValueError("차량명은 필수입니다")
        if not model_name:
            raise ValueError("모델명은 필수입니다")
        
        # 1. VehicleLine 처리
        vehicle_line_name = self._extract_vehicle_line_name(vehicle_name)
        print(f"[DEBUG] VehicleLine 이름 추출: {vehicle_line_name}")
        if not vehicle_line_name:
            raise ValueError(f"차량명에서 VehicleLine 추출 실패: {vehicle_name}")
        
        vehicle_line_result = self._get_or_create_vehicle_line(
            vehicle_line_name, staging_brand.id, entity_cache, created_by
        )
        print(f"[DEBUG] VehicleLine 처리 완료: {vehicle_line_result['created']}")
        
        # 2. Model 처리
        model_result = self._get_or_create_model(
            model_name, vehicle_line_result['entity'].id, entity_cache, created_by
        )
        print(f"[DEBUG] Model 처리 완료: {model_result['created']}")
        
        # 3. RowType에 따른 처리
        if row_type == 'TRIM':
            print(f"[DEBUG] TRIM 행 처리 시작")
            trim_result = self._process_trim_row_simple(record, model_result['entity'], entity_cache, created_by)
            result = {
                'type': 'trim',
                'created': trim_result['created'],
                'entity': trim_result['entity'],
                'vehicle_line_created': vehicle_line_result['created'],
                'model_created': model_result['created']
            }
            print(f"[DEBUG] TRIM 행 처리 완료: {result}")
            return result
        elif row_type == 'OPTION':
            print(f"[DEBUG] OPTION 행 처리 시작")
            option_result = self._process_option_row_simple(record, model_result['entity'], entity_cache, created_by)
            result = {
                'type': 'option',
                'created': option_result['created'],
                'entity': option_result['entity'],
                'vehicle_line_created': vehicle_line_result['created'],
                'model_created': model_result['created']
            }
            print(f"[DEBUG] OPTION 행 처리 완료: {result}")
            return result
        else:
            raise ValueError(f"알 수 없는 RowType: {row_type}")
    
    def _get_or_create_vehicle_line(self, vehicle_line_name: str, brand_id: int, 
                                   entity_cache: dict, created_by: str) -> dict:
        """VehicleLine 가져오기 또는 생성"""
        if vehicle_line_name in entity_cache['vehicle_lines']:
            return {'entity': entity_cache['vehicle_lines'][vehicle_line_name], 'created': False}
        
        staging_vehicle_line = self._create_staging_vehicle_line(brand_id, vehicle_line_name, created_by)
        entity_cache['vehicle_lines'][vehicle_line_name] = staging_vehicle_line
        return {'entity': staging_vehicle_line, 'created': True}
    
    def _get_or_create_model(self, model_name: str, vehicle_line_id: int, 
                            entity_cache: dict, created_by: str) -> dict:
        """Model 가져오기 또는 생성"""
        if model_name in entity_cache['models']:
            return {'entity': entity_cache['models'][model_name], 'created': False}
        
        staging_model = self._create_staging_model(vehicle_line_id, model_name, created_by)
        entity_cache['models'][model_name] = staging_model
        return {'entity': staging_model, 'created': True}
    
    def _process_trim_row_simple(self, record: dict, staging_model: StagingModel, 
                                entity_cache: dict, created_by: str) -> dict:
        """TRIM 행 간단 처리"""
        trim_name = record.get('Trim', '').strip()
        base_price_raw = record.get('BasePrice')
        base_price = self._parse_price(base_price_raw)
        
        print(f"[DEBUG] TRIM 처리 - 트림명: {trim_name}")
        print(f"[DEBUG] TRIM 처리 - BasePrice 원본: {base_price_raw} (타입: {type(base_price_raw)})")
        print(f"[DEBUG] TRIM 처리 - BasePrice 파싱 결과: {base_price}")
        print(f"[DEBUG] TRIM 처리 - 모델ID: {staging_model.id}")
        print(f"[DEBUG] TRIM 처리 - 전체 record: {record}")
        
        if not trim_name:
            raise ValueError("트림명이 없습니다")
        
        # 중복 트림 확인 - 모델별로 고유한 키 사용
        trim_key = f"{staging_model.id}_{trim_name}"
        if trim_key in entity_cache['trims']:
            print(f"[DEBUG] 기존 트림 사용: {trim_key}")
            return {'type': 'trim', 'created': False, 'entity': entity_cache['trims'][trim_key]}
        
        # 트림 생성
        print(f"[DEBUG] 새 트림 생성 중...")
        staging_trim = StagingTrim(
            name=trim_name,
            car_type=CarType.COMPACT,
            base_price=base_price,
            description=f"{trim_name} 트림",
            model_id=staging_model.id,
            created_by=created_by,
            created_by_email=created_by
        )
        
        print(f"[DEBUG] 트림 저장 중...")
        staging_trim = self.staging_trim_repo.save(staging_trim)
        entity_cache['trims'][trim_key] = staging_trim
        print(f"[DEBUG] 트림 저장 완료 - ID: {staging_trim.id}")
        
        return {'type': 'trim', 'created': True, 'entity': staging_trim}
    
    def _process_option_row_simple(self, record: dict, staging_model: StagingModel, 
                                  entity_cache: dict, created_by: str) -> dict:
        """OPTION 행 간단 처리"""
        trim_name = record.get('Trim') or ''
        trim_name = trim_name.strip() if trim_name else ''
        option_group = record.get('OptionGroup') or ''
        option_group = option_group.strip() if option_group else ''
        option_name = record.get('OptionName') or ''
        option_name = option_name.strip() if option_name else ''
        price_raw = record.get('Price')
        price = self._parse_price(price_raw)
        
        print(f"[DEBUG] OPTION 처리 - 트림명: {trim_name}")
        print(f"[DEBUG] OPTION 처리 - 그룹: {option_group}")
        print(f"[DEBUG] OPTION 처리 - 옵션명: {option_name}")
        print(f"[DEBUG] OPTION 처리 - Price 원본: {price_raw} (타입: {type(price_raw)})")
        print(f"[DEBUG] OPTION 처리 - Price 파싱 결과: {price}")
        print(f"[DEBUG] OPTION 처리 - 전체 record: {record}")
        
        if not option_name:
            raise ValueError("옵션명은 필수입니다")
        
        # OPTION 행에서 Trim이 비어있으면 OptionGroup을 트림으로 사용
        if not trim_name:
            if option_group:
                # OptionGroup에서 '/'로 구분된 트림들을 처리
                if '/' in option_group:
                    # 여러 트림에 옵션을 추가해야 함
                    trim_names = [t.strip() for t in option_group.split('/')]
                    print(f"[DEBUG] OPTION 행에서 여러 트림 감지: {trim_names}")
                    return self._process_option_for_multiple_trims(trim_names, option_name, price, staging_model, entity_cache, created_by)
                else:
                    # 단일 트림
                    trim_name = option_group
                    print(f"[DEBUG] OPTION 행에서 트림명이 비어있어서 OptionGroup을 트림으로 사용: {trim_name}")
            else:
                trim_name = "공통"
                print(f"[DEBUG] OPTION 행에서 트림명과 OptionGroup이 모두 비어있어서 공통 사용: {trim_name}")
        
        # 해당 트림 찾기 또는 생성
        trim_key = f"{staging_model.id}_{trim_name}"
        print(f"[DEBUG] 트림 키 검색: {trim_key}")
        print(f"[DEBUG] 사용 가능한 트림들: {list(entity_cache['trims'].keys())}")
        
        if trim_key not in entity_cache['trims']:
            # 트림이 없으면 새로 생성
            print(f"[DEBUG] 트림이 없어서 새로 생성: {trim_name}")
            staging_trim = StagingTrim(
                name=trim_name,
                car_type=CarType.COMPACT,
                base_price=None,  # OPTION 전용 트림이므로 기본 가격 없음
                description=f"{trim_name} 옵션 전용 트림",
                model_id=staging_model.id,
                created_by=created_by,
                created_by_email=created_by
            )
            staging_trim = self.staging_trim_repo.save(staging_trim)
            entity_cache['trims'][trim_key] = staging_trim
            print(f"[DEBUG] 새 트림 생성 완료 - ID: {staging_trim.id}, 이름: {staging_trim.name}")
        else:
            staging_trim = entity_cache['trims'][trim_key]
            print(f"[DEBUG] 기존 트림 사용 - ID: {staging_trim.id}, 이름: {staging_trim.name}")
        
        # OptionTitle 생성
        print(f"[DEBUG] OptionTitle 생성 중...")
        # 통합된 옵션 생성
        print(f"[DEBUG] 통합된 옵션 생성 중...")
        option = self._find_or_create_option(
            staging_trim.id, option_name, option_group, price, created_by
        )
        print(f"[DEBUG] 통합된 옵션 생성 완료 - ID: {option.id}")
        
        return {'type': 'option', 'created': True, 'entity': option}
    
    def _process_option_for_multiple_trims(self, trim_names: list, option_name: str, price: int, 
                                         staging_model: StagingModel, entity_cache: dict, created_by: str) -> dict:
        """여러 트림에 동일한 옵션 추가"""
        print(f"[DEBUG] 여러 트림에 옵션 추가 시작: {trim_names}")
        
        created_count = 0
        for trim_name in trim_names:
            print(f"[DEBUG] 트림 '{trim_name}'에 옵션 '{option_name}' 추가 중...")
            
            # 해당 트림 찾기 또는 생성
            trim_key = f"{staging_model.id}_{trim_name}"
            
            if trim_key not in entity_cache['trims']:
                print(f"[DEBUG] 트림 '{trim_name}'이 존재하지 않아서 생성 중...")
                # 트림 생성
                staging_trim = StagingTrim(
                    name=trim_name,
                    car_type=CarType.COMPACT,
                    base_price=None,  # 옵션 전용 트림은 기본 가격 없음
                    description=f"{trim_name} 트림",
                    model_id=staging_model.id,
                    created_by=created_by,
                    created_by_email=created_by
                )
                staging_trim = self.staging_trim_repo.save(staging_trim)
                entity_cache['trims'][trim_key] = staging_trim
                print(f"[DEBUG] 트림 '{trim_name}' 생성 완료 - ID: {staging_trim.id}")
            else:
                staging_trim = entity_cache['trims'][trim_key]
                print(f"[DEBUG] 기존 트림 '{trim_name}' 사용 - ID: {staging_trim.id}")
            
            # 옵션 생성
            staging_option = StagingOption(
                name=option_name,
                code=self._generate_option_code(option_name),
                description=f"{option_name} 옵션",
                category="선택옵션",
                price=price,
                discounted_price=None,
                trim_id=staging_trim.id,
                created_by=created_by,
                created_by_email=created_by
            )
            
            staging_option = self.staging_option_repo.save(staging_option)
            created_count += 1
            print(f"[DEBUG] 트림 '{trim_name}'에 옵션 '{option_name}' 추가 완료 - ID: {staging_option.id}")
        
        print(f"[DEBUG] 여러 트림에 옵션 추가 완료 - 총 {created_count}개 옵션 생성")
        return {'type': 'option', 'created': True, 'entity': staging_option, 'count': created_count}
    
    def _create_error_result(self, error_message: str) -> ImportResult:
        """에러 결과 생성"""
        return ImportResult(
            success=False,
            message=f"처리 실패: {error_message}",
            total_rows=0,
            processed_rows=0,
            brand_count=0,
            vehicle_line_count=0,
            model_count=0,
            trim_count=0,
            option_count=0,
            errors=[error_message]
        )
    
    def _create_success_message(self, stats: dict) -> str:
        """성공 메시지 생성"""
        return (f"데이터 import 완료 - "
                f"브랜드: {stats['brand_count']}개, "
                f"차량라인: {stats['vehicle_line_count']}개, "
                f"모델: {stats['model_count']}개, "
                f"트림: {stats['trim_count']}개, "
                f"옵션: {stats['option_count']}개")
    
    def _create_staging_brand(self, brand_name: str, country: str, version_id: int, created_by: str) -> StagingBrand:
        """Staging Brand 생성"""
        staging_brand = StagingBrand(
            name=brand_name,
            country=country,
            version_id=version_id,
            created_by=created_by,
            created_by_email=created_by,
            created_at=datetime.utcnow()
        )
        return self.staging_brand_repo.save(staging_brand)
    
    def _create_staging_vehicle_line(self, brand_id: int, vehicle_line_name: str, created_by: str) -> StagingVehicleLine:
        """Staging VehicleLine 생성"""
        staging_vehicle_line = StagingVehicleLine(
            name=vehicle_line_name,
            brand_id=brand_id,
            created_by=created_by,
            created_by_email=created_by,
            created_at=datetime.utcnow()
        )
        return self.staging_vehicle_line_repo.save(staging_vehicle_line)
    
    def _create_staging_model(self, vehicle_line_id: int, model_name: str, created_by: str) -> StagingModel:
        """Staging Model 생성"""
        staging_model = StagingModel(
            name=model_name,
            code=self._generate_model_code(model_name),
            vehicle_line_id=vehicle_line_id,
            created_by=created_by,
            created_by_email=created_by,
            created_at=datetime.utcnow()
        )
        return self.staging_model_repo.save(staging_model)
    
    def _process_trim_row(self, staging_model: StagingModel, record: dict, created_by: str) -> StagingTrim:
        """TRIM 행 처리"""
        trim_name = record.get('Trim', '')
        base_price_raw = record.get('BasePrice')
        base_price = self._parse_price(base_price_raw)
        
        print(f"[DEBUG] TRIM 처리 - 이름: '{trim_name}'")
        print(f"[DEBUG] TRIM 처리 - BasePrice 원본: {base_price_raw} (타입: {type(base_price_raw)})")
        print(f"[DEBUG] TRIM 처리 - BasePrice 파싱 결과: {base_price}")
        print(f"[DEBUG] TRIM 처리 - 전체 record: {record}")
        
        staging_trim = StagingTrim(
            name=trim_name,
            car_type=CarType.COMPACT,  # 기본값
            base_price=base_price,
            description=f"{trim_name} 트림",
            model_id=staging_model.id,
            created_by=created_by,
            created_by_email=created_by,
            created_at=datetime.utcnow()
        )
        
        return self.staging_trim_repo.save(staging_trim)
    
    def _process_option_row(self, staging_model: StagingModel, record: dict, trim_map: dict, created_by: str) -> int:
        """OPTION 행 처리 - 새로운 통합 옵션 방식"""
        option_name = record.get('OptionName', '')
        option_group = record.get('OptionGroup', '')  # 옵션 그룹
        trim_name = record.get('Trim', '')  # 옵션이 적용될 트림
        price_raw = record.get('Price')
        price = self._parse_price(price_raw)
        
        print(f"[DEBUG] OPTION 처리 - 이름: '{option_name}'")
        print(f"[DEBUG] OPTION 처리 - Price 원본: {price_raw} (타입: {type(price_raw)})")
        print(f"[DEBUG] OPTION 처리 - Price 파싱 결과: {price}")
        print(f"[DEBUG] OPTION 처리 - 전체 record: {record}")
        
        if not option_name:
            return 0
        
        # 옵션이 적용될 트림 찾기
        target_trim = None
        if trim_name and trim_name in trim_map:
            target_trim = trim_map[trim_name]
        else:
            # 트림이 지정되지 않은 경우 첫 번째 트림에 추가
            if trim_map:
                target_trim = list(trim_map.values())[0]
        
        if not target_trim:
            return 0
        
        # 새로운 통합 옵션 생성
        from ..domain.entities import StagingOption
        staging_option = StagingOption(
            name=option_name,
            trim_id=target_trim.id,
            category=option_group if option_group else "기본",
            price=price,
            description=f"{option_name} 옵션",
            created_by=created_by,
            created_by_email=created_by,
            created_at=datetime.utcnow()
        )
        
        # 새로운 옵션 저장 (새로운 통합 방식)
        try:
            self.staging_option_repo.save(staging_option)
            return 1
        except Exception as e:
            print(f"[WARNING] 새로운 옵션 저장 실패, 기존 방식으로 대체: {e}")
            # 기존 방식으로 대체 처리
        
        # 통합된 옵션으로 저장
        option = self._find_or_create_option(target_trim.id, option_name, option_group, price, created_by)
        return 1
    
    def _find_or_create_option(self, trim_id: int, option_name: str, option_group: str, price: int, created_by: str) -> StagingOption:
        """통합된 옵션 찾기 또는 생성"""
        existing = self.staging_option_repo.find_by_trim_and_name(trim_id, option_name)
        if existing:
            return existing
        
        # 옵션 그룹을 카테고리로 사용
        category = option_group if option_group else "기본"
        
        option = StagingOption(
            name=option_name,
            category=category,
            price=price,
            trim_id=trim_id,
            created_by=created_by,
            created_by_username=created_by,
            created_by_email=created_by
        )
        
        return self.staging_option_repo.save(option)
    
    def _update_version_stats(self, version_id: int, brand_count: int, model_count: int, trim_count: int):
        """버전 통계 업데이트 (동적 계산으로 변경)"""
        # 통계는 동적으로 계산하므로 데이터베이스에 저장하지 않음
        print(f"[DEBUG] 버전 {version_id} 통계 - 브랜드: {brand_count}, 모델: {model_count}, 트림: {trim_count}")
    
    @staticmethod
    def _extract_vehicle_line_name(vehicle_name: str) -> str:
        """차량명에서 VehicleLine 이름 추출"""
        if not vehicle_name:
            return ""
        
        # 년도와 공백 제거 후 브랜드명 제거
        name = str(vehicle_name).strip()
        
        # 년도 패턴 제거 (예: "2026 ", "2025 ")
        import re
        name = re.sub(r'^\d{4}\s*', '', name)
        
        # 브랜드명 제거 (현대, 기아 등)
        brand_names = ['현대', '기아', '제네시스', '쉐보레', '르노삼성']
        for brand in brand_names:
            if name.startswith(brand):
                name = name[len(brand):].strip()
                break
        
        return name
    
    @staticmethod
    def _generate_model_code(model_name: str) -> str:
        """모델명에서 코드 생성"""
        if not model_name:
            return ""
        
        # 특수문자 제거하고 대문자로 변환
        import re
        code = re.sub(r'[^\w\s]', '', model_name)
        code = code.replace(' ', '_').upper()
        
        return code
    
    @staticmethod
    def _parse_price(value) -> Optional[int]:
        """가격 파싱 (쉼표 제거 및 다양한 형식 지원)"""
        print(f"[DEBUG] _parse_price 호출 - 원본 값: {value} (타입: {type(value)})")
        
        if value is None:
            print(f"[DEBUG] _parse_price - 값이 None")
            return None
            
        if value == '' or value == ' ':
            print(f"[DEBUG] _parse_price - 값이 빈 문자열")
            return None
            
        try:
            # 문자열로 변환
            price_str = str(value).strip()
            print(f"[DEBUG] _parse_price - 문자열 변환 후: '{price_str}'")
            
            # 빈 문자열 체크
            if not price_str or price_str == 'nan' or price_str.lower() == 'none':
                print(f"[DEBUG] _parse_price - 빈 문자열 또는 nan")
                return None
            
            # 쉼표 제거
            price_str = price_str.replace(',', '').replace(' ', '')
            print(f"[DEBUG] _parse_price - 쉼표 제거 후: '{price_str}'")
            
            # 숫자로 변환
            if '.' in price_str:
                # 소수점이 있으면 float로 변환 후 int로 변환
                result = int(float(price_str))
            else:
                # 정수로 직접 변환
                result = int(price_str)
                
            print(f"[DEBUG] _parse_price - 최종 결과: {result}")
            return result
            
        except ValueError as e:
            print(f"[DEBUG] _parse_price - 숫자 변환 실패: {e}")
            return None
        except Exception as e:
            print(f"[DEBUG] _parse_price - 예상치 못한 오류: {e}")
            return None


# ===== Migration Use Case =====
class MigrationService:
    """Staging → Production 마이그레이션 유스케이스"""
    
    def __init__(
        self,
        version_repo, brand_repo, vehicle_line_repo, model_repo, trim_repo,
        staging_brand_repo, staging_vehicle_line_repo, staging_model_repo, staging_trim_repo
    ):
        self.version_repo = version_repo
        self.brand_repo = brand_repo
        self.vehicle_line_repo = vehicle_line_repo
        self.model_repo = model_repo
        self.trim_repo = trim_repo
        self.staging_brand_repo = staging_brand_repo
        self.staging_vehicle_line_repo = staging_vehicle_line_repo
        self.staging_model_repo = staging_model_repo
        self.staging_trim_repo = staging_trim_repo
    
    def migrate_approved_version(self, version_id: int) -> bool:
        """승인된 버전을 Production으로 마이그레이션"""
        version = self.version_repo.find_by_id(version_id)
        if not version or not version.is_approved():
            return False
        
        try:
            # Staging 데이터를 Production으로 마이그레이션
            staging_brands = self.staging_brand_repo.find_all_by_version(version_id)
            
            for staging_brand in staging_brands:
                # Brand 마이그레이션
                brand = Brand(
                    name=staging_brand.name,
                    country=staging_brand.country,
                    logo_url=staging_brand.logo_url,
                    manager=staging_brand.manager
                )
                production_brand = self.brand_repo.save(brand)
                
                # VehicleLine 마이그레이션
                staging_vehicle_lines = self.staging_vehicle_line_repo.find_all_by_brand(staging_brand.id)
                for staging_vehicle_line in staging_vehicle_lines:
                    vehicle_line = VehicleLine(
                        name=staging_vehicle_line.name,
                        description=staging_vehicle_line.description,
                        brand_id=production_brand.id
                    )
                    production_vehicle_line = self.vehicle_line_repo.save(vehicle_line)
                    
                    # Model 마이그레이션
                    staging_models = self.staging_model_repo.find_all_by_vehicle_line(staging_vehicle_line.id)
                    for staging_model in staging_models:
                        model = Model(
                            name=staging_model.name,
                            code=staging_model.code,
                            vehicle_line_id=production_vehicle_line.id,
                            release_year=staging_model.release_year,
                            price=staging_model.price,
                            foreign=staging_model.foreign
                        )
                        production_model = self.model_repo.save(model)
                        
                        # Trim 마이그레이션
                        staging_trims = self.staging_trim_repo.find_all_by_model(staging_model.id)
                        for staging_trim in staging_trims:
                            trim = Trim(
                                name=staging_trim.name,
                                car_type=staging_trim.car_type,
                                fuel_name=staging_trim.fuel_name,
                                cc=staging_trim.cc,
                                base_price=staging_trim.base_price,
                                description=staging_trim.description,
                                model_id=production_model.id
                            )
                            self.trim_repo.save(trim)
            
            return True
            
        except Exception as e:
            # 마이그레이션 실패 로그
            print(f"마이그레이션 실패: {str(e)}")
            return False