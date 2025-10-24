# 할인 정책 트랜잭션 버그 분석

## 🐛 발견된 문제

### 증상
- 전체 정책: 6개
- 카드사 제휴: 1개
- 브랜드 프로모션: 1개
- 재고 할인: 1개
- 선구매 할인: 1개
- **불완전한 정책: 2개** (세부 정보 없이 기본 정책만 존재)

### 원인 분석

#### 1. 데이터 생성 프로세스
```
프론트엔드
  ↓
1. createDiscountPolicy() 호출
  ↓
  백엔드: DiscountPolicyORM 생성
  ↓
  commit() ✅ (이미 DB에 저장됨)
  ↓
2. createCardBenefit() 호출
  ↓
  백엔드: BrandCardBenefitORM 생성
  ↓
  commit() ✅
```

#### 2. 문제점
- **각 Repository의 create 메서드에서 개별 commit 발생**
- 2단계 API 호출이 원자적으로 처리되지 않음
- 두 번째 단계 실패 시 기본 정책만 남음

#### 3. 코드 위치

**discount_repositories.py**
```python
def create(self, policy: DiscountPolicy) -> DiscountPolicy:
    policy_orm = DiscountPolicyORM(...)
    self.db.add(policy_orm)
    self.db.commit()  # ⚠️ 여기서 커밋
    self.db.refresh(policy_orm)
    return self._orm_to_entity(policy_orm)
```

**AddDiscountPolicy.jsx**
```javascript
// 1단계: 기본 정책 생성
const policy = await createDiscountPolicy(policyData);  // ✅ commit 됨

// 2단계: 세부 정보 생성
await createCardBenefit(detailData);  // ❌ 실패하면 기본 정책만 남음
```

## 🔧 해결 방법

### 방법 1: 백엔드 통합 API 추가 (권장)

**장점:**
- 트랜잭션 보장
- 원자적 처리
- 데이터 일관성 보장

**구현:**
1. Service 레이어에 통합 메서드 추가
2. Repository의 commit 제거 (flush만 사용)
3. API 레이어에서 통합 엔드포인트 추가

### 방법 2: 프론트엔드 롤백 로직 추가

**장점:**
- 빠른 적용 가능
- 기존 코드 수정 최소화

**단점:**
- 네트워크 문제 시 롤백 실패 가능
- 완벽한 트랜잭션 보장 어려움

**구현:**
```javascript
try {
  const policy = await createDiscountPolicy(policyData);
  await createCardBenefit(detailData);
} catch (error) {
  // 롤백: 기본 정책 삭제
  await deleteDiscountPolicy(policy.id);
  throw error;
}
```

### 방법 3: Repository 수정 (대규모 리팩토링)

**장점:**
- 근본적인 해결
- 모든 엔티티에 적용 가능

**단점:**
- 많은 코드 수정 필요
- 테스트 범위 확대

**구현:**
- Repository의 create 메서드에서 commit 제거
- Service 레이어에서 트랜잭션 관리
- API 레이어에서 최종 commit

## 📊 현재 데이터베이스 상태

```
discount_policy 테이블: 6개
├── 완전한 정책: 4개 (각 카테고리별 1개)
└── 불완전한 정책: 2개 (세부 정보 없음)
```

**불완전한 정책 확인:**
```sql
SELECT dp.* 
FROM discount_policy dp
LEFT JOIN brand_card_benefit bcb ON dp.id = bcb.discount_policy_id
LEFT JOIN brand_promo bp ON dp.id = bp.discount_policy_id
LEFT JOIN brand_inventory_discount bid ON dp.id = bid.discount_policy_id
LEFT JOIN brand_pre_purchase bpp ON dp.id = bpp.discount_policy_id
WHERE bcb.id IS NULL 
  AND bp.id IS NULL 
  AND bid.id IS NULL 
  AND bpp.id IS NULL;
```

## 🎯 권장 조치

1. **즉시 조치**: 불완전한 정책 2개 삭제
2. **단기 조치**: 방법 2 적용 (프론트엔드 롤백 로직)
3. **장기 조치**: 방법 1 적용 (백엔드 통합 API)

## 📝 영향받는 파일

- `app/infrastructure/discount_repositories.py` - Repository commit 로직
- `app/application/discount_service.py` - Service 레이어
- `app/presentation/api/discount/policies.py` - API 엔드포인트
- `admin-page/admin-wondergoodlife/src/pages/AddDiscountPolicy.jsx` - 프론트엔드
