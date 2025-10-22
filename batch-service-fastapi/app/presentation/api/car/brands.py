"""
Brand API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.use_cases import BrandService
from app.domain.entities import Brand
from ...dependencies import get_brand_service
from ...schemas import BrandRequest, BrandResponse

router = APIRouter(prefix="/api/brands", tags=["brands"])


@router.get("/", response_model=List[BrandResponse])
def get_brands(
    skip: int = 0,
    limit: int = 100,
    service: BrandService = Depends(get_brand_service)
):
    """브랜드 목록 조회"""
    brands = service.get_brands(skip=skip, limit=limit)
    return [BrandResponse(**brand.__dict__) for brand in brands]


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service)
):
    """특정 브랜드 조회"""
    brand = service.get_brand_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return BrandResponse(**brand.__dict__)


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_data: BrandRequest,
    service: BrandService = Depends(get_brand_service)
):
    """새 브랜드 생성"""
    try:
        brand = service.create_brand(
            name=brand_data.name,
            description=brand_data.description
        )
        return BrandResponse(**brand.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand_data: BrandRequest,
    service: BrandService = Depends(get_brand_service)
):
    """브랜드 정보 수정"""
    try:
        brand = service.update_brand(
            brand_id=brand_id,
            name=brand_data.name,
            description=brand_data.description
        )
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return BrandResponse(**brand.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service)
):
    """브랜드 삭제"""
    success = service.delete_brand(brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand not found")