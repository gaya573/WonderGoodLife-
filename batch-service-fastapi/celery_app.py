"""
Celery Application Entry Point
app/celery_app.py의 인스턴스를 import
"""
from app.celery_app import celery_app

__all__ = ['celery_app']

