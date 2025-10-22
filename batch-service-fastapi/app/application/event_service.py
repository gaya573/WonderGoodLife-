"""
이벤트 관리 서비스
"""
from typing import List, Optional
from datetime import datetime
from ..domain.entities import Event, EventRegistration, EventType, EventStatus
from ..infrastructure.event_repositories import (
    SQLAlchemyEventRepository,
    SQLAlchemyEventRegistrationRepository
)


class EventService:
    """이벤트 관리 서비스"""
    
    def __init__(
        self,
        event_repo: SQLAlchemyEventRepository,
        event_registration_repo: SQLAlchemyEventRegistrationRepository
    ):
        self.event_repo = event_repo
        self.event_registration_repo = event_registration_repo
    
    def create_event(self, event: Event, created_by: str) -> Event:
        """이벤트 생성"""
        event.created_by = created_by
        event.created_at = datetime.utcnow()
        event.validate()
        
        return self.event_repo.save(event)
    
    def update_event(self, event: Event) -> Optional[Event]:
        """이벤트 수정"""
        existing_event = self.event_repo.find_by_id(event.id)
        if not existing_event:
            return None
        
        event.updated_at = datetime.utcnow()
        event.validate()
        
        return self.event_repo.save(event)
    
    def delete_event(self, event_id: int) -> bool:
        """이벤트 삭제"""
        return self.event_repo.delete(event_id)
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """이벤트 조회"""
        return self.event_repo.find_by_id(event_id)
    
    def get_all_events(self, skip: int = 0, limit: int = 100, 
                      status: Optional[EventStatus] = None,
                      event_type: Optional[EventType] = None) -> List[Event]:
        """전체 이벤트 목록 조회"""
        return self.event_repo.find_all(skip=skip, limit=limit, 
                                       status=status, event_type=event_type)
    
    def get_active_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """활성 이벤트 목록 조회"""
        return self.event_repo.find_active_events(skip=skip, limit=limit)
    
    def get_ongoing_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """진행 중인 이벤트 목록 조회"""
        return self.event_repo.find_ongoing_events(skip=skip, limit=limit)
    
    def register_for_event(self, event_id: int, user_id: int, 
                          phone_number: Optional[str] = None,
                          email: Optional[str] = None,
                          notes: Optional[str] = None) -> Optional[EventRegistration]:
        """이벤트 등록"""
        # 이벤트 존재 확인
        event = self.event_repo.find_by_id(event_id)
        if not event:
            return None
        
        # 등록 가능 여부 확인
        if not event.can_register():
            return None
        
        # 중복 등록 확인
        existing_registration = self.event_registration_repo.find_by_event_and_user(event_id, user_id)
        if existing_registration:
            return None
        
        # 등록 생성
        registration = EventRegistration(
            event_id=event_id,
            user_id=user_id,
            phone_number=phone_number,
            email=email,
            notes=notes,
            status="confirmed"
        )
        registration.validate()
        
        # 등록 저장
        saved_registration = self.event_registration_repo.save(registration)
        
        # 이벤트 참가자 수 업데이트
        if saved_registration:
            event.current_participants += 1
            self.event_repo.save(event)
        
        return saved_registration
    
    def cancel_registration(self, event_id: int, user_id: int) -> bool:
        """이벤트 등록 취소"""
        registration = self.event_registration_repo.find_by_event_and_user(event_id, user_id)
        if not registration:
            return False
        
        # 등록 상태를 취소로 변경
        registration.status = "cancelled"
        self.event_registration_repo.save(registration)
        
        # 이벤트 참가자 수 업데이트
        event = self.event_repo.find_by_id(event_id)
        if event and event.current_participants > 0:
            event.current_participants -= 1
            self.event_repo.save(event)
        
        return True
    
    def get_event_registrations(self, event_id: int, skip: int = 0, limit: int = 100) -> List[EventRegistration]:
        """이벤트 등록자 목록 조회"""
        return self.event_registration_repo.find_by_event(event_id, skip=skip, limit=limit)
    
    def get_user_registrations(self, user_id: int, skip: int = 0, limit: int = 100) -> List[EventRegistration]:
        """사용자 등록 목록 조회"""
        return self.event_registration_repo.find_by_user(user_id, skip=skip, limit=limit)
    
    def activate_event(self, event_id: int) -> bool:
        """이벤트 활성화"""
        event = self.event_repo.find_by_id(event_id)
        if not event:
            return False
        
        event.status = EventStatus.ACTIVE
        event.updated_at = datetime.utcnow()
        self.event_repo.save(event)
        return True
    
    def deactivate_event(self, event_id: int) -> bool:
        """이벤트 비활성화"""
        event = self.event_repo.find_by_id(event_id)
        if not event:
            return False
        
        event.status = EventStatus.INACTIVE
        event.updated_at = datetime.utcnow()
        self.event_repo.save(event)
        return True
    
    def complete_event(self, event_id: int) -> bool:
        """이벤트 완료"""
        event = self.event_repo.find_by_id(event_id)
        if not event:
            return False
        
        event.status = EventStatus.COMPLETED
        event.updated_at = datetime.utcnow()
        self.event_repo.save(event)
        return True


def get_event_service(event_repo,
                     event_registration_repo):
    """이벤트 서비스 의존성 주입"""
    return EventService(event_repo, event_registration_repo)
