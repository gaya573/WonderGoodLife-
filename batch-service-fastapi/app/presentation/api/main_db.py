"""
메인 DB 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/main-db", tags=["main-db"])


@router.get("/status")
def get_main_db_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """메인 DB 현황 조회"""
    try:
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM
        )
        
        # 메인 DB 통계 조회
        brands_count = db.query(BrandORM).count()
        vehicle_lines_count = db.query(VehicleLineORM).count()
        models_count = db.query(ModelORM).count()
        trims_count = db.query(TrimORM).count()
        options_count = db.query(OptionORM).count()
        
        # 브랜드별 상세 정보 조회
        brands = db.query(BrandORM).all()
        brands_data = []
        
        for brand in brands:
            vehicle_lines = db.query(VehicleLineORM).filter(VehicleLineORM.brand_id == brand.id).all()
            models_count_for_brand = 0
            
            for vehicle_line in vehicle_lines:
                models_count_for_brand += db.query(ModelORM).filter(ModelORM.vehicle_line_id == vehicle_line.id).count()
            
            brands_data.append({
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "manager": brand.manager,
                "vehicle_lines_count": len(vehicle_lines),
                "models_count": models_count_for_brand
            })
        
        # 데이터가 없는 경우 빈 상태 응답
        if brands_count == 0:
            return {
                "stats": {
                    "brands": 0,
                    "vehicle_lines": 0,
                    "models": 0,
                    "trims": 0,
                    "options": 0
                },
                "brands": [],
                "last_updated": datetime.now().isoformat(),
                "database_status": "connected",
                "is_empty": True,
                "message": "메인 DB에 데이터가 없습니다."
            }
        
        return {
            "stats": {
                "brands": brands_count,
                "vehicle_lines": vehicle_lines_count,
                "models": models_count,
                "trims": trims_count,
                "options": options_count
            },
            "brands": brands_data,
            "last_updated": datetime.now().isoformat(),
            "database_status": "connected",
            "is_empty": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메인 DB 현황 조회 실패: {str(e)}")


@router.get("/brands/{brand_id}/details")
def get_brand_details(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드별 상세 데이터 조회"""
    try:
        print(f"브랜드 {brand_id} 상세 데이터 조회 시작")
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM
        )
        
        # 브랜드 조회
        brand = db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다.")
        
        print(f"브랜드 찾음: {brand.name}")
        
        # 차량 라인별 데이터 조회
        vehicle_lines = db.query(VehicleLineORM).filter(VehicleLineORM.brand_id == brand_id).all()
        print(f"차량 라인 {len(vehicle_lines)}개 찾음")
        vehicle_lines_data = []
        
        for vehicle_line in vehicle_lines:
            print(f"차량 라인 처리 중: {vehicle_line.name}")
            # 모델 조회
            models = db.query(ModelORM).filter(ModelORM.vehicle_line_id == vehicle_line.id).all()
            print(f"모델 {len(models)}개 찾음")
            models_data = []
            
            for model in models:
                print(f"모델 처리 중: {model.name}")
                # 트림 조회
                trims = db.query(TrimORM).filter(TrimORM.model_id == model.id).all()
                print(f"트림 {len(trims)}개 찾음")
                trims_data = []
                
                for trim in trims:
                    print(f"트림 처리 중: {trim.name}")
                    # 옵션 조회
                    options = db.query(OptionORM).filter(OptionORM.trim_id == trim.id).all()
                    print(f"옵션 {len(options)}개 찾음")
                    options_data = []
                    
                    for option in options:
                        options_data.append({
                            "id": option.id,
                            "name": option.name,
                            "code": option.code,
                            "description": option.description,
                            "price": option.price,
                            "discounted_price": option.discounted_price,
                            "category": option.category
                        })
                    
                    trims_data.append({
                        "id": trim.id,
                        "name": trim.name,
                        "car_type": trim.car_type,
                        "fuel_name": trim.fuel_name,
                        "cc": trim.cc,
                        "base_price": trim.base_price,
                        "description": trim.description,
                        "options": options_data
                    })
                
                models_data.append({
                    "id": model.id,
                    "name": model.name,
                    "code": model.code,
                    "description": model.description,
                    "release_year": model.release_year,
                    "price": model.price,
                    "foreign": model.foreign,
                    "trims": trims_data
                })
            
            vehicle_lines_data.append({
                "id": vehicle_line.id,
                "name": vehicle_line.name,
                "description": vehicle_line.description,
                "models": models_data
            })
        
        result = {
            "id": brand.id,
            "name": brand.name,
            "country": brand.country,
            "manager": brand.manager,
            "vehicle_lines": vehicle_lines_data
        }
        
        print(f"브랜드 {brand_id} 상세 데이터 조회 완료: {len(vehicle_lines_data)}개 차량 라인")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"브랜드 {brand_id} 상세 데이터 조회 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"브랜드 상세 데이터 조회 실패: {str(e)}")


@router.get("/search")
def search_main_db(
    q: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """메인 DB 검색"""
    try:
        from app.infrastructure.orm_models import (
            BrandORM, VehicleLineORM, ModelORM, TrimORM, OptionORM
        )
        
        if not q or len(q.strip()) < 2:
            return {"results": []}
        
        search_query = f"%{q.strip()}%"
        results = []
        
        # 모델 검색
        models = db.query(ModelORM).join(VehicleLineORM).join(BrandORM).filter(
            ModelORM.name.ilike(search_query)
        ).all()
        
        for model in models:
            vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == model.vehicle_line_id).first()
            brand = db.query(BrandORM).filter(BrandORM.id == vehicle_line.brand_id).first()
            
            results.append({
                "type": "model",
                "id": model.id,
                "name": model.name,
                "brand": brand.name,
                "vehicle_line": vehicle_line.name,
                "details": f"{brand.name} • {vehicle_line.name}"
            })
        
        # 트림 검색
        trims = db.query(TrimORM).join(ModelORM).join(VehicleLineORM).join(BrandORM).filter(
            TrimORM.name.ilike(search_query)
        ).all()
        
        for trim in trims:
            model = db.query(ModelORM).filter(ModelORM.id == trim.model_id).first()
            vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == model.vehicle_line_id).first()
            brand = db.query(BrandORM).filter(BrandORM.id == vehicle_line.brand_id).first()
            
            results.append({
                "type": "trim",
                "id": trim.id,
                "name": trim.name,
                "brand": brand.name,
                "model": model.name,
                "vehicle_line": vehicle_line.name,
                "details": f"{brand.name} • {model.name} • {vehicle_line.name}"
            })
        
        # 옵션 검색
        options = db.query(OptionORM).join(TrimORM).join(ModelORM).join(VehicleLineORM).join(BrandORM).filter(
            OptionORM.name.ilike(search_query)
        ).all()
        
        for option in options:
            trim = db.query(TrimORM).filter(TrimORM.id == option.trim_id).first()
            model = db.query(ModelORM).filter(ModelORM.id == trim.model_id).first()
            vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == model.vehicle_line_id).first()
            brand = db.query(BrandORM).filter(BrandORM.id == vehicle_line.brand_id).first()
            
            results.append({
                "type": "option",
                "id": option.id,
                "name": option.name,
                "brand": brand.name,
                "model": model.name,
                "trim": trim.name,
                "vehicle_line": vehicle_line.name,
                "details": f"{brand.name} • {model.name} • {trim.name} • {vehicle_line.name}"
            })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")


# ===== CRUD API 엔드포인트들 =====

@router.post("/brands")
def create_brand(
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 생성"""
    try:
        from app.infrastructure.orm_models import BrandORM
        
        new_brand = BrandORM(
            name=brand_data["name"],
            country=brand_data.get("country"),
            manager=brand_data.get("manager")
        )
        db.add(new_brand)
        db.commit()
        db.refresh(new_brand)
        
        return {"id": new_brand.id, "message": "브랜드가 생성되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 생성 실패: {str(e)}")


@router.put("/brands/{brand_id}")
def update_brand(
    brand_id: int,
    brand_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 수정"""
    try:
        from app.infrastructure.orm_models import BrandORM
        
        brand = db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다.")
        
        # 브랜드 정보 업데이트
        if "name" in brand_data:
            brand.name = brand_data["name"]
        if "country" in brand_data:
            brand.country = brand_data["country"]
        if "manager" in brand_data:
            brand.manager = brand_data["manager"]
        
        # 업데이트 정보 설정
        brand.updated_by_username = getattr(current_user, 'username', 'admin')
        brand.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        brand.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(brand)
        
        return {
            "success": True,
            "message": "브랜드가 성공적으로 수정되었습니다",
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "country": brand.country,
                "manager": brand.manager
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"브랜드 수정 에러: {str(e)}")
        print(f"브랜드 데이터: {brand_data}")
        print(f"브랜드 ID: {brand_id}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"브랜드 수정 실패: {str(e)}")


@router.delete("/brands/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """브랜드 삭제"""
    try:
        from app.infrastructure.orm_models import BrandORM
        
        brand = db.query(BrandORM).filter(BrandORM.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다.")
        
        db.delete(brand)
        db.commit()
        return {"message": "브랜드가 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"브랜드 삭제 실패: {str(e)}")


@router.post("/vehicle-lines")
def create_vehicle_line(
    vehicle_line_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """차량 라인 생성"""
    try:
        from app.infrastructure.orm_models import VehicleLineORM
        
        new_vehicle_line = VehicleLineORM(
            name=vehicle_line_data["name"],
            description=vehicle_line_data.get("description"),
            brand_id=vehicle_line_data["brand_id"]
        )
        db.add(new_vehicle_line)
        db.commit()
        db.refresh(new_vehicle_line)
        
        return {"id": new_vehicle_line.id, "message": "차량 라인이 생성되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"차량 라인 생성 실패: {str(e)}")


@router.put("/vehicle-lines/{vehicle_line_id}")
def update_vehicle_line(
    vehicle_line_id: int,
    vehicle_line_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """차량 라인 수정"""
    try:
        from app.infrastructure.orm_models import VehicleLineORM
        
        vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == vehicle_line_id).first()
        if not vehicle_line:
            raise HTTPException(status_code=404, detail="차량 라인을 찾을 수 없습니다.")
        
        # 차량 라인 정보 업데이트
        if "name" in vehicle_line_data:
            vehicle_line.name = vehicle_line_data["name"]
        if "description" in vehicle_line_data:
            vehicle_line.description = vehicle_line_data["description"]
        
        # 업데이트 정보 설정
        vehicle_line.updated_by_username = getattr(current_user, 'username', 'admin')
        vehicle_line.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        vehicle_line.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle_line)
        
        return {
            "success": True,
            "message": "차량 라인이 성공적으로 수정되었습니다",
            "vehicle_line": {
                "id": vehicle_line.id,
                "name": vehicle_line.name,
                "description": vehicle_line.description,
                "brand_id": vehicle_line.brand_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"차량 라인 수정 에러: {str(e)}")
        print(f"차량 라인 데이터: {vehicle_line_data}")
        print(f"차량 라인 ID: {vehicle_line_id}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"차량 라인 수정 실패: {str(e)}")


@router.delete("/vehicle-lines/{vehicle_line_id}")
def delete_vehicle_line(
    vehicle_line_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """차량 라인 삭제"""
    try:
        from app.infrastructure.orm_models import VehicleLineORM
        
        vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == vehicle_line_id).first()
        if not vehicle_line:
            raise HTTPException(status_code=404, detail="차량 라인을 찾을 수 없습니다.")
        
        db.delete(vehicle_line)
        db.commit()
        return {"message": "차량 라인이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"차량 라인 삭제 실패: {str(e)}")


@router.post("/models")
def create_model(
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """모델 생성"""
    try:
        from app.infrastructure.orm_models import ModelORM
        
        new_model = ModelORM(
            name=model_data["name"],
            code=model_data["code"],
            description=model_data.get("description"),
            vehicle_line_id=model_data["vehicle_line_id"],
            release_year=model_data.get("release_year"),
            price=model_data.get("price"),
            foreign=model_data.get("foreign", False)
        )
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        
        return {"id": new_model.id, "message": "모델이 생성되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"모델 생성 실패: {str(e)}")


@router.put("/models/{model_id}")
def update_model(
    model_id: int,
    model_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """모델 수정"""
    try:
        from app.infrastructure.orm_models import ModelORM
        
        model = db.query(ModelORM).filter(ModelORM.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        # 모델 정보 업데이트
        if "name" in model_data:
            model.name = model_data["name"]
        if "code" in model_data:
            model.code = model_data["code"]
        if "description" in model_data:
            model.description = model_data["description"]
        if "release_year" in model_data:
            release_year = model_data["release_year"]
            if release_year is None or release_year == '':
                model.release_year = None
            elif isinstance(release_year, (int, float)):
                model.release_year = int(release_year)
            elif isinstance(release_year, str) and release_year.strip():
                model.release_year = int(release_year)
            else:
                model.release_year = None
        if "price" in model_data:
            price = model_data["price"]
            if price is None or price == '':
                model.price = None
            elif isinstance(price, (int, float)):
                model.price = int(price)
            elif isinstance(price, str) and price.strip():
                model.price = int(price)
            else:
                model.price = None
        if "foreign" in model_data:
            model.foreign = model_data["foreign"]
        
        # 업데이트 정보 설정
        model.updated_by_username = getattr(current_user, 'username', 'admin')
        model.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        model.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(model)
        
        return {
            "success": True,
            "message": "모델이 성공적으로 수정되었습니다",
            "model": {
                "id": model.id,
                "name": model.name,
                "code": model.code,
                "description": model.description,
                "release_year": model.release_year,
                "price": model.price,
                "foreign": model.foreign,
                "vehicle_line_id": model.vehicle_line_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"모델 수정 에러: {str(e)}")
        print(f"모델 데이터: {model_data}")
        print(f"모델 ID: {model_id}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"모델 수정 실패: {str(e)}")


@router.delete("/models/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """모델 삭제"""
    try:
        from app.infrastructure.orm_models import ModelORM
        
        model = db.query(ModelORM).filter(ModelORM.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
        
        db.delete(model)
        db.commit()
        return {"message": "모델이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"모델 삭제 실패: {str(e)}")


@router.post("/trims")
def create_trim(
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """트림 생성"""
    try:
        from app.infrastructure.orm_models import TrimORM
        
        new_trim = TrimORM(
            name=trim_data["name"],
            car_type=trim_data["car_type"],
            fuel_name=trim_data.get("fuel_name"),
            cc=trim_data.get("cc"),
            base_price=trim_data.get("base_price"),
            description=trim_data.get("description"),
            model_id=trim_data["model_id"]
        )
        db.add(new_trim)
        db.commit()
        db.refresh(new_trim)
        
        return {"id": new_trim.id, "message": "트림이 생성되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 생성 실패: {str(e)}")


@router.put("/trims/{trim_id}")
def update_trim(
    trim_id: int,
    trim_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """트림 수정"""
    try:
        from app.infrastructure.orm_models import TrimORM
        
        trim = db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        if not trim:
            raise HTTPException(status_code=404, detail="트림을 찾을 수 없습니다.")
        
        # 트림 정보 업데이트
        if "name" in trim_data:
            trim.name = trim_data["name"]
        if "car_type" in trim_data:
            trim.car_type = trim_data["car_type"]
        if "fuel_name" in trim_data:
            trim.fuel_name = trim_data["fuel_name"]
        if "cc" in trim_data:
            trim.cc = trim_data["cc"]
        if "base_price" in trim_data:
            base_price = trim_data["base_price"]
            if base_price is None or base_price == '':
                trim.base_price = None
            elif isinstance(base_price, (int, float)):
                trim.base_price = int(base_price)
            elif isinstance(base_price, str) and base_price.strip():
                trim.base_price = int(base_price)
            else:
                trim.base_price = None
        if "description" in trim_data:
            trim.description = trim_data["description"]
        
        # 업데이트 정보 설정
        trim.updated_by_username = getattr(current_user, 'username', 'admin')
        trim.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        trim.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(trim)
        
        return {
            "success": True,
            "message": "트림이 성공적으로 수정되었습니다",
            "trim": {
                "id": trim.id,
                "name": trim.name,
                "car_type": trim.car_type,
                "fuel_name": trim.fuel_name,
                "cc": trim.cc,
                "base_price": trim.base_price,
                "description": trim.description,
                "model_id": trim.model_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"트림 수정 에러: {str(e)}")
        print(f"트림 데이터: {trim_data}")
        print(f"트림 ID: {trim_id}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"트림 수정 실패: {str(e)}")


@router.delete("/trims/{trim_id}")
def delete_trim(
    trim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """트림 삭제"""
    try:
        from app.infrastructure.orm_models import TrimORM
        
        trim = db.query(TrimORM).filter(TrimORM.id == trim_id).first()
        if not trim:
            raise HTTPException(status_code=404, detail="트림을 찾을 수 없습니다.")
        
        db.delete(trim)
        db.commit()
        return {"message": "트림이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"트림 삭제 실패: {str(e)}")


@router.post("/options")
def create_option(
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """옵션 생성"""
    try:
        from app.infrastructure.orm_models import OptionORM
        
        new_option = OptionORM(
            name=option_data["name"],
            code=option_data.get("code"),
            description=option_data.get("description"),
            price=option_data.get("price"),
            discounted_price=option_data.get("discounted_price"),
            category=option_data.get("category"),
            trim_id=option_data["trim_id"]
        )
        db.add(new_option)
        db.commit()
        db.refresh(new_option)
        
        return {"id": new_option.id, "message": "옵션이 생성되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 생성 실패: {str(e)}")


@router.put("/options/{option_id}")
def update_option(
    option_id: int,
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """옵션 수정"""
    try:
        from app.infrastructure.orm_models import OptionORM
        
        option = db.query(OptionORM).filter(OptionORM.id == option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="옵션을 찾을 수 없습니다.")
        
        # 옵션 정보 업데이트
        if "name" in option_data:
            option.name = option_data["name"]
        if "code" in option_data:
            option.code = option_data["code"]
        if "description" in option_data:
            option.description = option_data["description"]
        if "price" in option_data:
            price = option_data["price"]
            if price is None or price == '':
                option.price = None
            elif isinstance(price, (int, float)):
                option.price = int(price)
            elif isinstance(price, str) and price.strip():
                option.price = int(price)
            else:
                option.price = None
        if "discounted_price" in option_data:
            discounted_price = option_data["discounted_price"]
            if discounted_price is None or discounted_price == '':
                option.discounted_price = None
            elif isinstance(discounted_price, (int, float)):
                option.discounted_price = int(discounted_price)
            elif isinstance(discounted_price, str) and discounted_price.strip():
                option.discounted_price = int(discounted_price)
            else:
                option.discounted_price = None
        if "category" in option_data:
            option.category = option_data["category"]
        
        # 업데이트 정보 설정
        option.updated_by_username = getattr(current_user, 'username', 'admin')
        option.updated_by_email = getattr(current_user, 'email', 'admin@example.com')
        option.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(option)
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 수정되었습니다",
            "option": {
                "id": option.id,
                "name": option.name,
                "code": option.code,
                "description": option.description,
                "category": option.category,
                "price": option.price,
                "discounted_price": option.discounted_price,
                "trim_id": option.trim_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"옵션 수정 에러: {str(e)}")
        print(f"옵션 데이터: {option_data}")
        print(f"옵션 ID: {option_id}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"옵션 수정 실패: {str(e)}")


@router.delete("/options/{option_id}")
def delete_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """옵션 삭제"""
    try:
        from app.infrastructure.orm_models import OptionORM
        
        option = db.query(OptionORM).filter(OptionORM.id == option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="옵션을 찾을 수 없습니다.")
        
        db.delete(option)
        db.commit()
        return {"message": "옵션이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 삭제 실패: {str(e)}")


@router.get("/discount-policies")
def get_main_discount_policies(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """메인 DB 할인 정책 전체 조회"""
    try:
        from app.infrastructure.orm_models import (
            DiscountPolicyORM, BrandORM, VehicleLineORM, TrimORM,
            BrandCardBenefitORM, BrandPromoORM, BrandInventoryDiscountORM, BrandPrePurchaseORM
        )
        
        # 모든 할인 정책 조회
        policies = db.query(DiscountPolicyORM).all()
        
        policies_data = []
        
        for policy in policies:
            # 브랜드, Vehicle Line, 트림 정보 조회
            brand = db.query(BrandORM).filter(BrandORM.id == policy.brand_id).first()
            vehicle_line = db.query(VehicleLineORM).filter(VehicleLineORM.id == policy.vehicle_line_id).first()
            trim = db.query(TrimORM).filter(TrimORM.id == policy.trim_id).first()
            
            # 할인 유형별 상세 정보 조회
            policy_details = {}
            
            policy_type_str = policy.policy_type.value if hasattr(policy.policy_type, 'value') else str(policy.policy_type)
            
            if policy_type_str == 'CARD_BENEFIT':
                card_benefits = db.query(BrandCardBenefitORM).filter(
                    BrandCardBenefitORM.discount_policy_id == policy.id
                ).all()
                policy_details = {
                    "card_benefits": [
                        {
                            "id": cb.id,
                            "card_partner": cb.card_partner,
                            "cashback_rate": cb.cashback_rate,
                            "title": cb.title,
                            "description": cb.description,
                            "valid_from": cb.valid_from.isoformat() if cb.valid_from else None,
                            "valid_to": cb.valid_to.isoformat() if cb.valid_to else None,
                            "is_active": cb.is_active
                        }
                        for cb in card_benefits
                    ]
                }
            elif policy_type_str == 'BRAND_PROMO':
                promos = db.query(BrandPromoORM).filter(
                    BrandPromoORM.discount_policy_id == policy.id
                ).all()
                policy_details = {
                    "promos": [
                        {
                            "id": p.id,
                            "discount_rate": p.discount_rate,
                            "discount_amount": p.discount_amount,
                            "title": p.title,
                            "description": p.description,
                            "valid_from": p.valid_from.isoformat() if p.valid_from else None,
                            "valid_to": p.valid_to.isoformat() if p.valid_to else None,
                            "is_active": p.is_active
                        }
                        for p in promos
                    ]
                }
            elif policy_type_str == 'INVENTORY':
                inventory_discounts = db.query(BrandInventoryDiscountORM).filter(
                    BrandInventoryDiscountORM.discount_policy_id == policy.id
                ).all()
                policy_details = {
                    "inventory_discounts": [
                        {
                            "id": inv.id,
                            "inventory_level_threshold": inv.inventory_level_threshold,
                            "discount_rate": inv.discount_rate,
                            "title": inv.title,
                            "description": inv.description,
                            "valid_from": inv.valid_from.isoformat() if inv.valid_from else None,
                            "valid_to": inv.valid_to.isoformat() if inv.valid_to else None,
                            "is_active": inv.is_active
                        }
                        for inv in inventory_discounts
                    ]
                }
            elif policy_type_str == 'PRE_PURCHASE':
                pre_purchases = db.query(BrandPrePurchaseORM).filter(
                    BrandPrePurchaseORM.discount_policy_id == policy.id
                ).all()
                policy_details = {
                    "pre_purchases": [
                        {
                            "id": pp.id,
                            "event_type": pp.event_type.value if hasattr(pp.event_type, 'value') else str(pp.event_type),
                            "discount_rate": pp.discount_rate,
                            "discount_amount": pp.discount_amount,
                            "title": pp.title,
                            "description": pp.description,
                            "pre_purchase_start": pp.pre_purchase_start.isoformat() if pp.pre_purchase_start else None,
                            "valid_from": pp.valid_from.isoformat() if pp.valid_from else None,
                            "valid_to": pp.valid_to.isoformat() if pp.valid_to else None,
                            "is_active": pp.is_active
                        }
                        for pp in pre_purchases
                    ]
                }
            
            policies_data.append({
                "id": policy.id,
                "brand_id": policy.brand_id,
                "brand_name": brand.name if brand else None,
                "vehicle_line_id": policy.vehicle_line_id,
                "vehicle_line_name": vehicle_line.name if vehicle_line else None,
                "trim_id": policy.trim_id,
                "trim_name": trim.name if trim else None,
                "policy_type": policy_type_str,
                "title": policy.title,
                "description": policy.description,
                "valid_from": policy.valid_from.isoformat() if policy.valid_from else None,
                "valid_to": policy.valid_to.isoformat() if policy.valid_to else None,
                "is_active": policy.is_active,
                "created_at": policy.created_at.isoformat() if policy.created_at else None,
                "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
                **policy_details
            })
        
        # 통계 정보
        stats = {
            "total": len(policies_data),
            "card_benefit": len([p for p in policies_data if p["policy_type"] == "CARD_BENEFIT"]),
            "brand_promo": len([p for p in policies_data if p["policy_type"] == "BRAND_PROMO"]),
            "inventory": len([p for p in policies_data if p["policy_type"] == "INVENTORY"]),
            "pre_purchase": len([p for p in policies_data if p["policy_type"] == "PRE_PURCHASE"]),
            "active": len([p for p in policies_data if p["is_active"]])
        }
        
        return {
            "stats": stats,
            "policies": policies_data,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메인 DB 할인 정책 조회 실패: {str(e)}")