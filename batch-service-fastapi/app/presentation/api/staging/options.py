"""
Staging Options CRUD API
옵션 관련 CRUD 작업을 처리하는 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure.orm_models import StagingOptionORM
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/api/staging/options", tags=["staging-options"])


@router.get("/")
def get_staging_options(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trim_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 옵션 목록 조회"""
    try:
        query = db.query(StagingOptionORM)
        
        if trim_id:
            query = query.filter(StagingOptionORM.trim_id == trim_id)
        
        total_count = query.count()
        options = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": option.id,
                    "name": option.name,
                    "code": option.code,
                    "description": option.description,
                    "category": option.category,
                    "price": option.price,
                    "discounted_price": option.discounted_price,
                    "trim_id": option.trim_id,
                    "created_by": option.created_by,
                    "created_by_username": option.created_by_username,
                    "created_by_email": option.created_by_email,
                    "created_at": option.created_at.isoformat() if option.created_at else None,
                    "updated_at": option.updated_at.isoformat() if option.updated_at else None
                }
                for option in options
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"옵션 목록 조회 실패: {str(e)}")


@router.get("/{option_id}")
def get_staging_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 옵션 상세 조회"""
    try:
        option = db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="옵션을 찾을 수 없습니다"
            )
        
        return {
            "id": option.id,
            "name": option.name,
            "code": option.code,
            "description": option.description,
            "category": option.category,
            "price": option.price,
            "discounted_price": option.discounted_price,
            "trim_id": option.trim_id,
            "created_by": option.created_by,
            "created_by_username": option.created_by_username,
            "created_by_email": option.created_by_email,
            "created_at": option.created_at.isoformat() if option.created_at else None,
            "updated_at": option.updated_at.isoformat() if option.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"옵션 조회 실패: {str(e)}")


@router.post("/")
def create_staging_option(
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 스테이징 옵션 생성"""
    try:
        # 빈 문자열을 None으로 변환
        price = option_data.get('price')
        price_value = int(price) if price and price.strip() else None
        
        discounted_price = option_data.get('discounted_price')
        discounted_price_value = int(discounted_price) if discounted_price and discounted_price.strip() else None
        
        new_option = StagingOptionORM(
            name=option_data.get('name'),
            code=option_data.get('code'),
            description=option_data.get('description'),
            category=option_data.get('category'),
            price=price_value,
            discounted_price=discounted_price_value,
            trim_id=option_data.get('trim_id'),
            created_by=getattr(current_user, 'username', 'admin'),
            created_by_username=getattr(current_user, 'username', 'admin'),
            created_by_email=getattr(current_user, 'email', 'admin@example.com')
        )
        
        db.add(new_option)
        db.commit()
        db.refresh(new_option)
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 생성되었습니다",
            "option": {
                "id": new_option.id,
                "name": new_option.name,
                "code": new_option.code,
                "description": new_option.description,
                "category": new_option.category,
                "price": new_option.price,
                "discounted_price": new_option.discounted_price,
                "trim_id": new_option.trim_id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"옵션 생성 에러: {str(e)}")
        print(f"옵션 데이터: {option_data}")
        print(f"현재 사용자: {current_user}")
        print(f"에러 타입: {type(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"옵션 생성 실패: {str(e)}")


@router.put("/{option_id}")
def update_staging_option(
    option_id: int,
    option_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 옵션 수정"""
    try:
        option = db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="옵션을 찾을 수 없습니다"
            )
        
        # 옵션 정보 업데이트
        if 'name' in option_data:
            option.name = option_data['name']
        if 'code' in option_data:
            option.code = option_data['code']
        if 'description' in option_data:
            option.description = option_data['description']
        if 'category' in option_data:
            option.category = option_data['category']
        if 'price' in option_data:
            # 빈 문자열을 None으로 변환
            price = option_data['price']
            if price is None or price == '':
                option.price = None
            elif isinstance(price, (int, float)):
                option.price = int(price)
            elif isinstance(price, str) and price.strip():
                option.price = int(price)
            else:
                option.price = None
                
        if 'discounted_price' in option_data:
            # 빈 문자열을 None으로 변환
            discounted_price = option_data['discounted_price']
            if discounted_price is None or discounted_price == '':
                option.discounted_price = None
            elif isinstance(discounted_price, (int, float)):
                option.discounted_price = int(discounted_price)
            elif isinstance(discounted_price, str) and discounted_price.strip():
                option.discounted_price = int(discounted_price)
            else:
                option.discounted_price = None
        
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


@router.delete("/{option_id}")
def delete_staging_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """스테이징 옵션 삭제"""
    try:
        option = db.query(StagingOptionORM).filter(StagingOptionORM.id == option_id).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="옵션을 찾을 수 없습니다"
            )
        
        db.delete(option)
        db.commit()
        
        return {
            "success": True,
            "message": "옵션이 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"옵션 삭제 실패: {str(e)}")
