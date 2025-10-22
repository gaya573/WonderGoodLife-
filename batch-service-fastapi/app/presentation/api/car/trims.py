"""
Trim API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.application.use_cases import TrimService
from app.domain.entities import Trim
from ...dependencies import get_trim_service
from ...schemas import TrimRequest, TrimResponse

router = APIRouter(prefix="/api/trims", tags=["trims"])


@router.get("", response_model=List[TrimResponse])
def get_all_trims(
    model_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    service: TrimService = Depends(get_trim_service)
):
    """모든 트림 조회 (모델 ID로 필터링 가능)"""
    trims = service.get_all_trims(model_id, skip, limit)
    return [TrimResponse(**t.__dict__) for t in trims]


@router.get("/{trim_id}", response_model=TrimResponse)
def get_trim(
    trim_id: int,
    service: TrimService = Depends(get_trim_service)
):
    """특정 트림 조회"""
    trim = service.get_trim_by_id(trim_id)
    if not trim:
        raise HTTPException(status_code=404, detail="Trim not found")
    return TrimResponse(**trim.__dict__)


@router.post("", response_model=TrimResponse, status_code=status.HTTP_201_CREATED)
def create_trim(
    request: TrimRequest,
    service: TrimService = Depends(get_trim_service)
):
    """트림 생성"""
    try:
        trim = Trim(**request.model_dump())
        created_trim = service.create_trim(trim)
        return TrimResponse(**created_trim.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{trim_id}", response_model=TrimResponse)
def update_trim(
    trim_id: int,
    request: TrimRequest,
    service: TrimService = Depends(get_trim_service)
):
    """트림 수정"""
    try:
        trim = Trim(**request.model_dump())
        updated_trim = service.update_trim(trim_id, trim)
        if not updated_trim:
            raise HTTPException(status_code=404, detail="Trim not found")
        return TrimResponse(**updated_trim.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{trim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trim(
    trim_id: int,
    service: TrimService = Depends(get_trim_service)
):
    """트림 삭제"""
    success = service.delete_trim(trim_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trim not found")
    return None

