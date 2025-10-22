"""
Model API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.use_cases import ModelService
from app.domain.entities import Model
from ...dependencies import get_model_service
from ...schemas import ModelRequest, ModelResponse

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=List[ModelResponse])
def get_all_models(
    skip: int = 0,
    limit: int = 100,
    service: ModelService = Depends(get_model_service)
):
    """모든 모델 조회"""
    models = service.get_all_models(skip, limit)
    return [ModelResponse(**m.__dict__) for m in models]


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int,
    service: ModelService = Depends(get_model_service)
):
    """?�정 모델 조회"""
    model = service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelResponse(**model.__dict__)


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    request: ModelRequest,
    service: ModelService = Depends(get_model_service)
):
    """모델 ?�성"""
    try:
        model = Model(**request.model_dump())
        created_model = service.create_model(model)
        return ModelResponse(**created_model.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: int,
    request: ModelRequest,
    service: ModelService = Depends(get_model_service)
):
    """모델 ?�정"""
    try:
        model = Model(**request.model_dump())
        updated_model = service.update_model(model_id, model)
        if not updated_model:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelResponse(**updated_model.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int,
    service: ModelService = Depends(get_model_service)
):
    """모델 ??��"""
    success = service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return None

