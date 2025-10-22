# React 무한 캐러셀 구현 중 발생한 버그 해결 과정

## 프로젝트 개요
- **목표**: 특가 차량 섹션에 무한 스크롤 캐러셀 구현
- **요구사항**: 
  - 4개 카드만 화면에 표시
  - 부드러운 슬라이드 애니메이션
  - 끊김 없는 무한 루프
  - 2초마다 자동 슬라이드

---

## 발생한 버그 및 해결 과정

### 🐛 Bug #1: 페이지네이션 vs 슬라이드 애니메이션

**문제 상황**
```javascript
// 잘못된 구현
const handleNextSlide = () => {
  setCurrentSlide(prev => (prev < totalSlides - 1 ? prev + 1 : 0));
};
```
- 버튼 클릭 시 4개씩 페이지 단위로 넘어감
- 슬라이드 애니메이션이 아닌 페이지 전환처럼 작동

**원인 분석**
- `grid-template-columns`를 사용하여 4개 단위로 레이아웃 변경
- `transform: translateX()`가 4개 단위로만 이동

**해결 방법**
```javascript
// 올바른 구현
const handleNextSlide = () => {
  setCurrentSlide(prev => prev + 1);
};

// CSS
.special-cars-list {
  display: flex;
  gap: 1.25rem;
}

// Transform 계산
transform: `translateX(-${currentSlide * (cardWidth + cardGap)}px)`
```

**핵심 포인트**
- ✅ 1개씩 이동하도록 변경
- ✅ Flexbox로 연속된 레이아웃 구성
- ✅ 카드 하나의 너비(260px) + gap(20px) 단위로 이동

---

### 🐛 Bug #2: 카드 크기가 계속 변하는 문제

**문제 상황**
```css
/* 잘못된 CSS */
.special-car-card {
  width: 260px;
  /* height 미지정 */
}
```
- 차량 이름이나 설명 길이에 따라 카드 높이 변경
- 슬라이드할 때마다 레이아웃이 흔들림

**원인 분석**
- 높이를 고정하지 않아 콘텐츠에 따라 유동적으로 변함
- 이미지 높이도 미지정
- 텍스트 오버플로우 처리 없음

**해결 방법**
```css
/* 올바른 CSS */
.special-car-card {
  width: 260px;
  min-height: 340px;
  max-height: 340px;
}

.special-car-image {
  height: 150px;
  overflow: hidden;
}

.special-car-info h4,
.special-car-info p {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* h4는 2줄 */
  -webkit-box-orient: vertical;
  min-height: 44px;
}
```

**핵심 포인트**
- ✅ 카드 높이를 `min-height`와 `max-height`로 고정
- ✅ 이미지 높이 고정
- ✅ 말줄임표로 텍스트 오버플로우 처리
- ✅ `min-height`로 텍스트 공간 확보

---

### 🐛 Bug #3: 슬라이드 시 순간적으로 빈 공간이 보이는 버그

**문제 상황**
```javascript
// 잘못된 구현
const extendedCars = [...specialCars, ...specialCars.slice(0, 4)];
// 10개 + 4개 = 14개만 렌더링
```
- 10번째 카드에서 다음 버튼 클릭 시 순간적으로 빈 공간 노출
- 무한 루프는 작동하지만 시각적으로 끊김

**원인 분석**
- 복제 카드가 충분하지 않음
- 초기 위치가 0번에서 시작해서 뒤로 갈 여유가 없음
- Transition이 끝나기 전에 빈 공간이 화면에 보임

**해결 방법**
```javascript
// 올바른 구현
const extendedCars = [...specialCars, ...specialCars, ...specialCars];
// 10 + 10 + 10 = 30개 (3배 복제)

// 초기 위치를 중간 세트로 설정
const [currentSlide, setCurrentSlide] = useState(specialCars.length);
// 0번이 아닌 10번에서 시작

// 무한 루프 처리
React.useEffect(() => {
  if (currentSlide <= 0) {
    setTimeout(() => {
      setIsTransitioning(false);
      setCurrentSlide(specialCars.length); // 10번으로 점프
      setTimeout(() => setIsTransitioning(true), 50);
    }, 600);
  } else if (currentSlide >= specialCars.length * 2) {
    setTimeout(() => {
      setIsTransitioning(false);
      setCurrentSlide(specialCars.length); // 10번으로 점프
      setTimeout(() => setIsTransitioning(true), 50);
    }, 600);
  }
}, [currentSlide, specialCars.length]);
```

**핵심 포인트**
- ✅ 카드를 3배 복제 (앞뒤 여유 확보)
- ✅ 초기 위치를 중간 세트로 설정
- ✅ Transition 끝난 후 점프 처리
- ✅ 시각적으로 끊김 없음

**데이터 구조 시각화**
```
[세트1: 0~9] [세트2: 10~19] [세트3: 20~29]
              ↑ 초기 시작 위치 (10번)
              
← 뒤로: 9→8→...→0 → (점프) → 10
→ 앞으로: 10→11→...→19 → (점프) → 10
```

---

### 🐛 Bug #4: 컨테이너 크기 조정 문제

**문제 상황**
```css
/* 잘못된 CSS */
.special-cars-carousel {
  display: grid;
  grid-template-columns: 100px 1fr 100px;
}
```
- 화면 크기에 따라 4개 이상 보이거나, 3개만 보임
- 슬라이드 시 빈 공간 노출

**해결 방법**
```css
/* 올바른 CSS */
.special-cars-carousel {
  display: grid;
  grid-template-columns: 100px minmax(0, 1100px) 100px;
  max-width: 1400px;
  margin: 0 auto;
}

.special-cars-list-wrapper {
  overflow: hidden;
  width: 100%;
  max-width: 1100px;
}
```

**계산식**
```
카드 4개: 260px × 4 = 1040px
Gap 3개: 20px × 3 = 60px
총 너비: 1100px
```

**핵심 포인트**
- ✅ 정확히 4개만 보이도록 `max-width` 설정
- ✅ `overflow: hidden`으로 나머지 숨김
- ✅ `minmax(0, 1100px)`로 반응형 대응

---

## 최종 구현 코드

### React Component
```javascript
const Home = () => {
  const specialCars = [
    { name: '더 뉴 스포티지 NQ5 하이브리드', spec: '2.5 터보 익스클루시브 9인승' },
    // ... 10개 데이터
  ];

  const itemsPerSlide = 4;
  const cardWidth = 260;
  const cardGap = 20;
  
  // 3배 복제
  const extendedCars = [...specialCars, ...specialCars, ...specialCars];
  
  // 중간에서 시작
  const [currentSlide, setCurrentSlide] = useState(specialCars.length);
  const [isTransitioning, setIsTransitioning] = useState(true);

  const handlePrevSlide = () => {
    setCurrentSlide(prev => prev - 1);
  };

  const handleNextSlide = () => {
    setCurrentSlide(prev => prev + 1);
  };

  // 무한 루프 처리
  React.useEffect(() => {
    if (currentSlide <= 0) {
      setTimeout(() => {
        setIsTransitioning(false);
        setCurrentSlide(specialCars.length);
        setTimeout(() => setIsTransitioning(true), 50);
      }, 600);
    } else if (currentSlide >= specialCars.length * 2) {
      setTimeout(() => {
        setIsTransitioning(false);
        setCurrentSlide(specialCars.length);
        setTimeout(() => setIsTransitioning(true), 50);
      }, 600);
    }
  }, [currentSlide, specialCars.length]);

  // 2초마다 자동 슬라이드
  React.useEffect(() => {
    const autoSlide = setInterval(() => {
      handleNextSlide();
    }, 2000);

    return () => clearInterval(autoSlide);
  }, [currentSlide]);

  return (
    <div className="special-cars-list-wrapper">
      <div 
        className="special-cars-list"
        style={{
          transform: `translateX(-${currentSlide * (cardWidth + cardGap)}px)`,
          transition: isTransitioning 
            ? 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)' 
            : 'none'
        }}
      >
        {extendedCars.map((car, index) => (
          <div key={index} className="special-car-card">
            {/* 카드 내용 */}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### CSS
```css
.special-cars-carousel {
  display: grid;
  grid-template-columns: 100px minmax(0, 1100px) 100px;
  align-items: center;
  gap: 1.5rem;
  margin: 2.5rem auto 3rem;
  max-width: 1400px;
}

.special-cars-list-wrapper {
  overflow: hidden;
  width: 100%;
  max-width: 1100px;
  padding: 4px;
  margin: 0 auto;
}

.special-cars-list {
  display: flex;
  gap: 1.25rem;
  will-change: transform;
}

.special-car-card {
  flex-shrink: 0;
  width: 260px;
  min-height: 340px;
  max-height: 340px;
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 12px;
}

.special-car-image {
  height: 150px;
  overflow: hidden;
}

.special-car-info h4 {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 44px;
}
```

---

## 배운 점 및 Best Practices

### 1. 무한 루프 구현 패턴
- **데이터 3배 복제**: 앞뒤로 충분한 여유 확보
- **중간에서 시작**: 양방향 스크롤 가능
- **Transition 후 점프**: 사용자가 눈치채지 못하게 위치 재조정

### 2. 카드 크기 고정
- `min-height`, `max-height` 동시 사용
- 이미지와 텍스트 모두 고정 영역 설정
- `-webkit-line-clamp`로 텍스트 오버플로우 처리

### 3. Transform vs Transition
- `transform`은 항상 적용 (위치 제어)
- `transition`은 조건부 적용 (애니메이션 on/off)
- 점프 시에는 `transition: none` 필수

### 4. 정확한 계산
- 카드 너비 + gap을 정확히 계산
- 컨테이너 크기를 정확히 맞춰 빈 공간 방지
- `overflow: hidden`으로 나머지 숨김

### 5. Auto Slide
- `setInterval`로 자동 재생
- `useEffect` cleanup으로 메모리 누수 방지
- 의존성 배열에 `currentSlide` 추가로 매번 새로운 interval 생성

---

## 성능 최적화 포인트

### 1. GPU 가속
```css
.special-cars-list {
  will-change: transform;
}
```

### 2. Cubic-Bezier Easing
```css
transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
```
- 부드러운 감속 효과
- Material Design 표준 easing

### 3. Flexbox vs Grid
- 슬라이드에는 Flexbox가 더 적합
- Grid는 페이지네이션에 적합

---

## 결론

React에서 무한 캐러셀을 구현할 때는 다음 사항들을 고려해야 합니다:

1. ✅ **데이터 구조**: 충분한 복제본 생성
2. ✅ **초기 위치**: 중간에서 시작
3. ✅ **크기 고정**: 레이아웃 흔들림 방지
4. ✅ **Transition 제어**: 점프 시 애니메이션 끄기
5. ✅ **정확한 계산**: 컨테이너와 카드 크기 정밀 계산

이러한 패턴을 잘 활용하면 끊김 없는 부드러운 무한 캐러셀을 구현할 수 있습니다! 🎉

---

## 참고 자료
- [React useEffect Hook](https://react.dev/reference/react/useEffect)
- [CSS Transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [Line Clamping](https://css-tricks.com/line-clampin/)

