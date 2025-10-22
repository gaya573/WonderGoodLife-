"""
이벤트 관리 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.event_service import EventService, get_event_service
from app.application.permission_service import PermissionService, get_permission_service
from app.domain.entities import EventType, EventStatus
from app.presentation.dependencies import get_current_active_user
from app.domain.entities import User
from ...schemas import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    EventRegistrationCreate, EventRegistrationResponse, EventRegistrationListResponse
)

router = APIRouter(prefix="/api/events", tags=["events"])


# ===== 이벤트 Repository 의존성 =====
# 의존성 함수들은 직접 사용하지 않고 Service를 통해 처리


# ===== 이벤트 CRUD API =====

@router.get("/", response_model=EventListResponse)
def get_events(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수"),
    event_type: Optional[EventType] = Query(None, description="이벤트 타입 필터"),
    status: Optional[EventStatus] = Query(None, description="이벤트 상태 필터"),
    event_service: EventService = Depends(get_event_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 목록 조회"""
    try:
        events = event_service.get_events(
            skip=skip,
            limit=limit,
            event_type=event_type,
            status=status
        )
        
        total_count = event_service.count_events(event_type=event_type, status=status)
        
        return EventListResponse(
            events=[EventResponse.model_validate(event) for event in events],
            total_count=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 목록 조회 실패: {str(e)}")


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service),
    current_user: User = Depends(get_current_active_user)
):
    """특정 이벤트 조회"""
    try:
        event = event_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이벤트를 찾을 수 없습니다"
            )
        
        return EventResponse.model_validate(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 조회 실패: {str(e)}")


@router.post("/", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    event_service: EventService = Depends(get_event_service),
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """새 이벤트 생성"""
    try:
        # 권한 확인
        if not permission_service.can_create_event(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이벤트 생성 권한이 없습니다"
            )
        
        event = event_service.create_event(
            title=event_data.title,
            description=event_data.description,
            event_type=event_data.event_type,
            start_date=event_data.start_date,
            end_date=event_data.end_date,
            location=event_data.location,
            max_participants=event_data.max_participants,
            created_by=current_user.id
        )
        
        return EventResponse.model_validate(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 생성 실패: {str(e)}")


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    event_service: EventService = Depends(get_event_service),
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 수정"""
    try:
        # 기존 이벤트 조회
        existing_event = event_service.get_event(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이벤트를 찾을 수 없습니다"
            )
        
        # 권한 확인
        if not permission_service.can_edit_event(current_user, existing_event):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이벤트 수정 권한이 없습니다"
            )
        
        # 이벤트 수정
        updated_event = event_service.update_event(event_id, event_data)
        
        return EventResponse.model_validate(updated_event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 수정 실패: {str(e)}")


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service),
    permission_service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 삭제"""
    try:
        # 기존 이벤트 조회
        existing_event = event_service.get_event(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이벤트를 찾을 수 없습니다"
            )
        
        # 권한 확인
        if not permission_service.can_delete_event(current_user, existing_event):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이벤트 삭제 권한이 없습니다"
            )
        
        # 이벤트 삭제
        event_service.delete_event(event_id)
        
        return {"message": "이벤트가 성공적으로 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 삭제 실패: {str(e)}")


# ===== 이벤트 등록 API =====

@router.post("/{event_id}/register", response_model=EventRegistrationResponse)
def register_for_event(
    event_id: int,
    registration_data: EventRegistrationCreate,
    event_service: EventService = Depends(get_event_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 등록"""
    try:
        registration = event_service.register_for_event(
            event_id=event_id,
            user_id=current_user.id,
            additional_info=registration_data.additional_info
        )
        
        return EventRegistrationResponse.model_validate(registration)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 등록 실패: {str(e)}")


@router.delete("/{event_id}/unregister")
def unregister_from_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 등록 취소"""
    try:
        event_service.unregister_from_event(event_id, current_user.id)
        
        return {"message": "이벤트 등록이 취소되었습니다"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 등록 취소 실패: {str(e)}")


@router.get("/{event_id}/registrations", response_model=EventRegistrationListResponse)
def get_event_registrations(
    event_id: int,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수"),
    event_service: EventService = Depends(get_event_service),
    current_user: User = Depends(get_current_active_user)
):
    """이벤트 등록자 목록 조회"""
    try:
        registrations = event_service.get_event_registrations(
            event_id=event_id,
            skip=skip,
            limit=limit
        )
        
        total_count = event_service.count_event_registrations(event_id)
        
        return EventRegistrationListResponse(
            registrations=[EventRegistrationResponse.model_validate(reg) for reg in registrations],
            total_count=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 등록자 목록 조회 실패: {str(e)}")


@router.get("/health")
def health_check():
    """이벤트 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "events",
        "message": "이벤트 서비스가 정상 작동 중입니다"
    }