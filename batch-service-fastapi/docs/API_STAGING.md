# 📋 Staging API 가이드

## 🎯 Staging 데이터란?

배치 작업(엑셀 업로드, 크롤링)으로 수집된 **임시 데이터**입니다.  
관리자가 확인/수정 후 승인하면 Main 테이블로 전송됩니다.

## 📡 Staging CRUD API

### 1. Staging 브랜드 목록 조회

```bash
GET /api/staging/brands
GET /api/staging/brands?status=PENDING  # 승인 대기만
GET /api/staging/brands?status=APPROVED  # 승인됨만
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "현대",
    "country": "KR",
    "logo_url": null,
    "approval_status": "PENDING",
    "created_by": "batch_service",
    "created_at": "2024-01-15T10:30:00",
    "approved_by": null,
    "approved_at": null
  }
]
```

### 2. Staging 브랜드 상세 조회

```bash
GET /api/staging/brands/1
```

### 3. Staging 브랜드 수정

```bash
PUT /api/staging/brands/1
Content-Type: application/json

{
  "name": "현대자동차",
  "country": "KR",
  "logo_url": "https://example.com/logo.png"
}
```

**주의**: `APPROVED` 상태에서는 수정 불가

### 4. Staging 브랜드 승인 ⭐

```bash
POST /api/staging/brands/1/approve
Content-Type: application/json

{
  "approved_by": "admin@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "브랜드 '현대'가 승인되었습니다. CDC를 통해 메인 테이블로 전송됩니다.",
  "entity_type": "brand",
  "entity_id": 1
}
```

**동작:**
1. Staging 데이터 상태 → `APPROVED`
2. Celery CDC Task 실행 (백그라운드)
3. Main `brand` 테이블에 복사

### 5. Staging 브랜드 거부

```bash
POST /api/staging/brands/1/reject
Content-Type: application/json

{
  "approved_by": "admin@example.com",
  "rejection_reason": "브랜드명이 정확하지 않습니다"
}
```

### 6. Staging 브랜드 삭제

```bash
DELETE /api/staging/brands/1
```

**주의**: `APPROVED` 상태에서는 삭제 불가

### 7. 일괄 승인 🚀

```bash
POST /api/staging/approve-all
Content-Type: application/json

{
  "approved_by": "admin@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "총 25개 데이터가 승인되었습니다 (Brand: 5, Model: 10, Trim: 10)",
  "entity_type": "all",
  "entity_id": 0
}
```

모든 PENDING 상태의 Brand, Model, Trim을 한 번에 승인

## 🔄 React 컴포넌트 예제

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function StagingBrandList() {
  const [stagingBrands, setStagingBrands] = useState([]);

  useEffect(() => {
    loadStagingBrands();
  }, []);

  const loadStagingBrands = async () => {
    const response = await axios.get(
      'http://localhost:8000/api/staging/brands?status=PENDING'
    );
    setStagingBrands(response.data);
  };

  const handleApprove = async (id: number) => {
    await axios.post(
      `http://localhost:8000/api/staging/brands/${id}/approve`,
      { approved_by: 'admin' }
    );
    
    alert('승인되었습니다!');
    loadStagingBrands();  // 새로고침
  };

  const handleReject = async (id: number) => {
    const reason = prompt('거부 사유를 입력하세요:');
    
    await axios.post(
      `http://localhost:8000/api/staging/brands/${id}/reject`,
      {
        approved_by: 'admin',
        rejection_reason: reason
      }
    );
    
    alert('거부되었습니다!');
    loadStagingBrands();
  };

  const handleEdit = async (id: number, newName: string) => {
    await axios.put(
      `http://localhost:8000/api/staging/brands/${id}`,
      { name: newName }
    );
    
    loadStagingBrands();
  };

  const handleApproveAll = async () => {
    if (!confirm('모든 데이터를 승인하시겠습니까?')) return;
    
    await axios.post(
      'http://localhost:8000/api/staging/approve-all',
      { approved_by: 'admin' }
    );
    
    alert('일괄 승인되었습니다!');
    loadStagingBrands();
  };

  return (
    <div>
      <h2>승인 대기 브랜드</h2>
      <button onClick={handleApproveAll}>전체 승인</button>
      
      <table>
        <thead>
          <tr>
            <th>이름</th>
            <th>국가</th>
            <th>상태</th>
            <th>작업</th>
          </tr>
        </thead>
        <tbody>
          {stagingBrands.map(brand => (
            <tr key={brand.id}>
              <td>{brand.name}</td>
              <td>{brand.country}</td>
              <td>{brand.approval_status}</td>
              <td>
                <button onClick={() => handleApprove(brand.id)}>
                  승인
                </button>
                <button onClick={() => handleReject(brand.id)}>
                  거부
                </button>
                <button onClick={() => handleEdit(brand.id, '새 이름')}>
                  수정
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default StagingBrandList;
```

## 🎯 상태 전환

```
PENDING (승인 대기)
   ↓ approve
APPROVED (승인됨) → CDC → Main 테이블
   
PENDING (승인 대기)
   ↓ reject
REJECTED (거부됨)
```

## 📊 데이터베이스 상태

### Before (Staging)

```sql
SELECT * FROM staging_brand;
```

| id | name | country | approval_status |
|----|------|---------|-----------------|
| 1 | 현대 | KR | PENDING |
| 2 | 기아 | KR | PENDING |

### After Approval (Main)

```sql
SELECT * FROM brand;
```

| id | name | country |
|----|------|---------|
| 1 | 현대 | KR |
| 2 | 기아 | KR |

## 🚀 실전 시나리오

### 시나리오 1: 엑셀 업로드 후 전체 승인

```bash
# 1. 엑셀 업로드
POST /api/jobs/excel/upload (파일 첨부)

# 2. 작업 완료 대기
GET /api/jobs/1 (폴링)

# 3. Staging 데이터 확인
GET /api/staging/brands?status=PENDING

# 4. 일괄 승인
POST /api/staging/approve-all

# 5. Spring Boot에서 조회
GET http://localhost:8080/api/brands (Main 데이터)
```

### 시나리오 2: 개별 확인 후 승인

```bash
# 1. Staging 데이터 조회
GET /api/staging/brands?status=PENDING

# 2. 개별 데이터 수정
PUT /api/staging/brands/1
{ "name": "현대자동차" }

# 3. 개별 승인
POST /api/staging/brands/1/approve

# 4. 다른 데이터는 거부
POST /api/staging/brands/2/reject
{ "rejection_reason": "중복 데이터" }
```

---

**Staging CRUD로 완벽한 승인 워크플로우!** ✅

