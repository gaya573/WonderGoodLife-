# 권한표와 API 엔드포인트 매칭 정리 (수정됨)

## 권한 체계 (역할별)

### 🔑 역할별 권한 정책
- **ADMIN (관리자)**: 모든 권한 (19개)
- **MANAGER (부장)**: 모든 권한 (19개) 
- **CEO (대표)**: 모든 권한 (19개)
- **USER (일반 사용자)**: 사용자 관리 권한 제외 (16개)

### 🚫 일반 사용자 제한사항
- **user_management_read**: 사용자 목록 조회 불가
- **user_management_write**: 사용자 생성/수정 불가  
- **user_management_delete**: 사용자 삭제 불가

---

## 현재 권한 목록 (19개)

### 1. 메인 자동차 시스템 (main_carsystem) - 모든 역할 접근 가능
- **main_carsystem_read** (ID: 1) - 메인 자동차 시스템 조회
- **main_carsystem_write** (ID: 2) - 메인 자동차 시스템 생성/수정  
- **main_carsystem_delete** (ID: 3) - 메인 자동차 시스템 삭제

### 2. 데모 자동차 시스템 (demo_carsystem) - 모든 역할 접근 가능
- **demo_carsystem_read** (ID: 4) - 데모 자동차 시스템 조회
- **demo_carsystem_write** (ID: 5) - 데모 자동차 시스템 생성/수정
- **demo_carsystem_delete** (ID: 6) - 데모 자동차 시스템 삭제

### 3. Staging 데이터 (staging_data) - 모든 역할 접근 가능
- **staging_data_read** (ID: 7) - Staging 데이터 조회
- **staging_data_write** (ID: 8) - Staging 데이터 생성/수정
- **staging_data_delete** (ID: 9) - Staging 데이터 삭제

### 4. 사용자 관리 (user_management) - ADMIN/MANAGER/CEO만 접근 가능
- **user_management_read** (ID: 10) - 사용자 관리 조회
- **user_management_write** (ID: 11) - 사용자 관리 생성/수정
- **user_management_delete** (ID: 12) - 사용자 관리 삭제

### 5. 사용자 권한 관리 (user_role) - 모든 역할 접근 가능
- **user_role_read** (ID: 13) - 사용자 권한 관리 조회
- **user_role_write** (ID: 14) - 사용자 권한 관리 생성/수정
- **user_role_delete** (ID: 15) - 사용자 권한 관리 삭제

### 6. 시스템 관리 (system_admin) - 모든 역할 접근 가능
- **system_admin_admin** (ID: 16) - 시스템 관리

### 7. 이벤트 데이터 (event_data) - 모든 역할 접근 가능
- **event_data_read** (ID: 17) - 이벤트 데이터 조회
- **event_data_write** (ID: 18) - 이벤트 데이터 생성/수정
- **event_data_delete** (ID: 19) - 이벤트 데이터 삭제

---

## API 엔드포인트와 권한 매칭

### 🔐 인증 관련 API (`/api/auth`)
- `POST /api/auth/login` - 로그인 (권한 불필요)
- `POST /api/auth/register` - 회원가입 (권한 불필요)

### 👥 사용자 관리 API (`/api/users`) - **ADMIN/MANAGER/CEO만 접근 가능**
- `GET /api/users/` - **user_management_read** 필요 (USER 제외)
- `POST /api/users/` - **user_management_write** 필요 (USER 제외)
- `GET /api/users/{user_id}` - **user_management_read** 필요 (USER 제외)
- `PUT /api/users/{user_id}` - **user_management_write** 필요 (USER 제외)
- `DELETE /api/users/{user_id}` - **user_management_delete** 필요 (USER 제외)
- `GET /api/users/me/profile` - 본인 정보 (권한 불필요)

### 🔑 권한 관리 API (`/api/permissions`) - **모든 역할 접근 가능**
- `GET /api/permissions/roles` - **user_role_read** 필요
- `POST /api/permissions/roles` - **user_role_write** 필요
- `PUT /api/permissions/roles/{role_id}` - **user_role_write** 필요
- `DELETE /api/permissions/roles/{role_id}` - **user_role_delete** 필요
- `GET /api/permissions/permissions` - **user_role_read** 필요
- `POST /api/permissions/permissions` - **user_role_write** 필요
- `DELETE /api/permissions/permissions/{permission_id}` - **user_role_delete** 필요
- `GET /api/permissions/matrix` - **user_role_read** 필요
- `POST /api/permissions/matrix/assign` - **user_role_write** 필요
- `DELETE /api/permissions/matrix/revoke` - **user_role_delete** 필요

### 📋 버전 관리 API (`/api/versions`) - **모든 역할 접근 가능**
- `GET /api/versions/` - **staging_data_read** 필요
- `POST /api/versions/` - **staging_data_write** 필요
- `GET /api/versions/{version_id}` - **staging_data_read** 필요
- `PUT /api/versions/{version_id}` - **staging_data_write** 필요
- `DELETE /api/versions/{version_id}` - **staging_data_delete** 필요
- `GET /api/versions/{version_id}/brands-with-full-data` - **staging_data_read** 필요
- `GET /api/versions/{version_id}/vehicle-lines-with-full-data` - **staging_data_read** 필요
- `GET /api/versions/{version_id}/simple-search` - **staging_data_read** 필요

### 🏢 브랜드 관리 API (`/api/staging/brands`) - **모든 역할 접근 가능**
- `GET /api/staging/brands/` - **staging_data_read** 필요
- `POST /api/staging/brands/` - **staging_data_write** 필요
- `GET /api/staging/brands/{brand_id}` - **staging_data_read** 필요
- `PUT /api/staging/brands/{brand_id}` - **staging_data_write** 필요
- `DELETE /api/staging/brands/{brand_id}` - **staging_data_delete** 필요

### 🚗 차량라인 관리 API (`/api/staging/vehicle-lines`) - **모든 역할 접근 가능**
- `GET /api/staging/vehicle-lines/` - **staging_data_read** 필요
- `POST /api/staging/vehicle-lines/` - **staging_data_write** 필요
- `GET /api/staging/vehicle-lines/{vehicle_line_id}` - **staging_data_read** 필요
- `PUT /api/staging/vehicle-lines/{vehicle_line_id}` - **staging_data_write** 필요
- `DELETE /api/staging/vehicle-lines/{vehicle_line_id}` - **staging_data_delete** 필요

### 🚙 모델 관리 API (`/api/staging/models`) - **모든 역할 접근 가능**
- `GET /api/staging/models/` - **staging_data_read** 필요
- `POST /api/staging/models/` - **staging_data_write** 필요
- `GET /api/staging/models/{model_id}` - **staging_data_read** 필요
- `PUT /api/staging/models/{model_id}` - **staging_data_write** 필요
- `DELETE /api/staging/models/{model_id}` - **staging_data_delete** 필요

### 🔧 트림 관리 API (`/api/staging/trims`) - **모든 역할 접근 가능**
- `GET /api/staging/trims/` - **staging_data_read** 필요
- `POST /api/staging/trims/` - **staging_data_write** 필요
- `GET /api/staging/trims/{trim_id}` - **staging_data_read** 필요
- `PUT /api/staging/trims/{trim_id}` - **staging_data_write** 필요
- `DELETE /api/staging/trims/{trim_id}` - **staging_data_delete** 필요

### ⚙️ 옵션 관리 API (`/api/staging/options`) - **모든 역할 접근 가능**
- `GET /api/staging/options/` - **staging_data_read** 필요
- `POST /api/staging/options/` - **staging_data_write** 필요
- `GET /api/staging/options/{option_id}` - **staging_data_read** 필요
- `PUT /api/staging/options/{option_id}` - **staging_data_write** 필요
- `DELETE /api/staging/options/{option_id}` - **staging_data_delete** 필요

### 📊 메인 자동차 시스템 API (`/api/car`) - **모든 역할 접근 가능**
- `GET /api/car/brands/` - **main_carsystem_read** 필요
- `POST /api/car/brands/` - **main_carsystem_write** 필요
- `GET /api/car/models/` - **main_carsystem_read** 필요
- `POST /api/car/models/` - **main_carsystem_write** 필요
- `GET /api/car/trims/` - **main_carsystem_read** 필요
- `POST /api/car/trims/` - **main_carsystem_write** 필요

### 📈 배치 작업 API (`/api/batch`) - **모든 역할 접근 가능**
- `GET /api/batch/jobs/` - **system_admin_admin** 필요
- `POST /api/batch/jobs/` - **system_admin_admin** 필요
- `GET /api/batch/jobs/{job_id}` - **system_admin_admin** 필요
- `POST /api/batch/excel/upload` - **system_admin_admin** 필요

### 🎉 이벤트 관리 API (`/api/events`) - **모든 역할 접근 가능**
- `GET /api/events/` - **event_data_read** 필요
- `POST /api/events/` - **event_data_write** 필요
- `GET /api/events/{event_id}` - **event_data_read** 필요
- `PUT /api/events/{event_id}` - **event_data_write** 필요
- `DELETE /api/events/{event_id}` - **event_data_delete** 필요
- `POST /api/events/{event_id}/register` - **event_data_write** 필요

---

## 권한 체크 구현 방안

### 1. 권한 체크 로직 (수정됨)
```python
def check_user_permission(db: Session, user: User, resource: str, action: str) -> bool:
    # ADMIN, MANAGER, CEO는 모든 권한을 가짐
    if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.CEO]:
        return True
    
    # 일반 사용자(USER)는 사용자 관리 권한을 가질 수 없음
    if user.role == UserRole.USER and resource == "user_management":
        return False
    
    # 나머지 권한 체크 로직...
```

### 2. 역할별 권한 정책
- **ADMIN/MANAGER/CEO**: 모든 API 접근 가능
- **USER**: 사용자 관리 API 제외, 나머지 모든 API 접근 가능

### 3. 프론트엔드 UI 제어
- 일반 사용자에게는 사용자 관리 메뉴 숨김
- 권한 관리 페이지에서 일반 사용자에게 사용자 관리 권한 할당 불가

이제 올바른 권한 체계가 구현되었습니다!
