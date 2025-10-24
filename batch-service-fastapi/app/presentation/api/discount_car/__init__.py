"""
Main DB 할인 정책 API 메인 라우터 - 모든 할인 정책 관련 API 통합
"""
from fastapi import APIRouter

from .policies import router as policies_router
from .card_benefits import router as card_benefits_router
from .promos import router as promos_router
from .inventory_discounts import router as inventory_discounts_router
from .pre_purchases import router as pre_purchases_router

router = APIRouter()

# 각 하위 라우터를 메인 라우터에 포함
router.include_router(policies_router)
router.include_router(card_benefits_router)
router.include_router(promos_router)
router.include_router(inventory_discounts_router)
router.include_router(pre_purchases_router)

