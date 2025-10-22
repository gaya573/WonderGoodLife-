"""
이벤트 관련 Repository 구현체
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.entities import Event, EventRegistration, EventType, EventStatus
from .orm_models import EventORM, EventRegistrationORM


class SQLAlchemyEventRepository:
    """SQLAlchemy 기반 이벤트 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, event_id: int) -> Optional[Event]:
        db_event = self.db.query(EventORM).filter(EventORM.id == event_id).first()
        return self._to_entity(db_event) if db_event else None
    
    def find_all(self, skip: int = 0, limit: int = 100, status: Optional[EventStatus] = None, 
                 event_type: Optional[EventType] = None) -> List[Event]:
        query = self.db.query(EventORM)
        
        if status:
            query = query.filter(EventORM.status == status)
        if event_type:
            query = query.filter(EventORM.event_type == event_type)
        
        db_events = query.offset(skip).limit(limit).all()
        return [self._to_entity(event) for event in db_events]
    
    def find_active_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """활성 이벤트 조회"""
        db_events = self.db.query(EventORM).filter(
            EventORM.status == EventStatus.ACTIVE
        ).offset(skip).limit(limit).all()
        return [self._to_entity(event) for event in db_events]
    
    def find_ongoing_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """진행 중인 이벤트 조회"""
        from datetime import datetime
        now = datetime.utcnow()
        
        db_events = self.db.query(EventORM).filter(
            EventORM.status == EventStatus.ACTIVE,
            EventORM.start_date <= now,
            EventORM.end_date >= now
        ).offset(skip).limit(limit).all()
        return [self._to_entity(event) for event in db_events]
    
    def save(self, event: Event) -> Event:
        """이벤트 저장"""
        if event.id:
            # 업데이트
            db_event = self.db.query(EventORM).filter(EventORM.id == event.id).first()
            if db_event:
                self._update_orm(db_event, event)
                self.db.commit()
                return self._to_entity(db_event)
        else:
            # 생성
            db_event = self._to_orm(event)
            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)
            return self._to_entity(db_event)
        
        return event
    
    def delete(self, event_id: int) -> bool:
        """이벤트 삭제"""
        db_event = self.db.query(EventORM).filter(EventORM.id == event_id).first()
        if db_event:
            self.db.delete(db_event)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, orm: EventORM) -> Event:
        """ORM을 도메인 엔티티로 변환"""
        return Event(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            event_type=orm.event_type,
            status=orm.status,
            start_date=orm.start_date,
            end_date=orm.end_date,
            location=orm.location,
            address=orm.address,
            max_participants=orm.max_participants,
            current_participants=orm.current_participants,
            registration_fee=orm.registration_fee,
            related_brand_id=orm.related_brand_id,
            related_model_id=orm.related_model_id,
            created_by=orm.created_by,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
    
    def _to_orm(self, entity: Event) -> EventORM:
        """도메인 엔티티를 ORM으로 변환"""
        return EventORM(
            title=entity.title,
            description=entity.description,
            event_type=entity.event_type,
            status=entity.status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            location=entity.location,
            address=entity.address,
            max_participants=entity.max_participants,
            current_participants=entity.current_participants,
            registration_fee=entity.registration_fee,
            related_brand_id=entity.related_brand_id,
            related_model_id=entity.related_model_id,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _update_orm(self, orm: EventORM, entity: Event):
        """ORM 업데이트"""
        orm.title = entity.title
        orm.description = entity.description
        orm.event_type = entity.event_type
        orm.status = entity.status
        orm.start_date = entity.start_date
        orm.end_date = entity.end_date
        orm.location = entity.location
        orm.address = entity.address
        orm.max_participants = entity.max_participants
        orm.current_participants = entity.current_participants
        orm.registration_fee = entity.registration_fee
        orm.related_brand_id = entity.related_brand_id
        orm.related_model_id = entity.related_model_id
        orm.updated_at = entity.updated_at


class SQLAlchemyEventRegistrationRepository:
    """SQLAlchemy 기반 이벤트 등록 저장소"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, registration_id: int) -> Optional[EventRegistration]:
        db_registration = self.db.query(EventRegistrationORM).filter(
            EventRegistrationORM.id == registration_id
        ).first()
        return self._to_entity(db_registration) if db_registration else None
    
    def find_by_event_and_user(self, event_id: int, user_id: int) -> Optional[EventRegistration]:
        db_registration = self.db.query(EventRegistrationORM).filter(
            EventRegistrationORM.event_id == event_id,
            EventRegistrationORM.user_id == user_id
        ).first()
        return self._to_entity(db_registration) if db_registration else None
    
    def find_by_event(self, event_id: int, skip: int = 0, limit: int = 100) -> List[EventRegistration]:
        """특정 이벤트의 등록자 목록"""
        db_registrations = self.db.query(EventRegistrationORM).filter(
            EventRegistrationORM.event_id == event_id
        ).offset(skip).limit(limit).all()
        return [self._to_entity(reg) for reg in db_registrations]
    
    def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[EventRegistration]:
        """특정 사용자의 등록 목록"""
        db_registrations = self.db.query(EventRegistrationORM).filter(
            EventRegistrationORM.user_id == user_id
        ).offset(skip).limit(limit).all()
        return [self._to_entity(reg) for reg in db_registrations]
    
    def save(self, registration: EventRegistration) -> EventRegistration:
        """등록 저장"""
        if registration.id:
            # 업데이트
            db_registration = self.db.query(EventRegistrationORM).filter(
                EventRegistrationORM.id == registration.id
            ).first()
            if db_registration:
                self._update_orm(db_registration, registration)
                self.db.commit()
                return self._to_entity(db_registration)
        else:
            # 생성
            db_registration = self._to_orm(registration)
            self.db.add(db_registration)
            self.db.commit()
            self.db.refresh(db_registration)
            return self._to_entity(db_registration)
        
        return registration
    
    def delete(self, registration_id: int) -> bool:
        """등록 삭제"""
        db_registration = self.db.query(EventRegistrationORM).filter(
            EventRegistrationORM.id == registration_id
        ).first()
        if db_registration:
            self.db.delete(db_registration)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, orm: EventRegistrationORM) -> EventRegistration:
        """ORM을 도메인 엔티티로 변환"""
        return EventRegistration(
            id=orm.id,
            event_id=orm.event_id,
            user_id=orm.user_id,
            registration_date=orm.registration_date,
            phone_number=orm.phone_number,
            email=orm.email,
            notes=orm.notes,
            status=orm.status
        )
    
    def _to_orm(self, entity: EventRegistration) -> EventRegistrationORM:
        """도메인 엔티티를 ORM으로 변환"""
        return EventRegistrationORM(
            event_id=entity.event_id,
            user_id=entity.user_id,
            registration_date=entity.registration_date,
            phone_number=entity.phone_number,
            email=entity.email,
            notes=entity.notes,
            status=entity.status
        )
    
    def _update_orm(self, orm: EventRegistrationORM, entity: EventRegistration):
        """ORM 업데이트"""
        orm.phone_number = entity.phone_number
        orm.email = entity.email
        orm.notes = entity.notes
        orm.status = entity.status
