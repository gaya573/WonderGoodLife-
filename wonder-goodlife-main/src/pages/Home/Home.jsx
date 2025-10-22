import React, { useState, useEffect } from 'react';
import './Home.css';
import CarCard from '../../components/CarCard';
import YoutubeCard from '../../components/YoutubeCard';
import WonderBlogSection from '../../components/WonderBlogSection';
import { useSlideDebounce } from '../../hooks/useSlideDebounce';

const Home = () => {
  const [timeLeft, setTimeLeft] = useState({
    days: 10,
    hours: 15,
    minutes: 57,
    seconds: 17
  });

  const specialCars = [
    { name: '더 뉴 스포티지 NQ5 하이브리드', spec: '2.5 터보 익스클루시브 9인승' },
    { name: '카니발 1.6 터보 하이브리드', spec: '시그니처 11인승' },
    { name: 'G80 전기차', spec: '롱 레인지 2WD' },
    { name: '아이오닉 6', spec: '롱 레인지 2WD 익스클루시브' },
    { name: '그랜저 하이브리드', spec: '캘리그라피' },
    { name: 'K8 하이브리드', spec: 'GL3 프레스티지' },
    { name: 'EV6', spec: '롱 레인지 2WD GT 라인' },
    { name: '투싼 하이브리드', spec: '1.6 터보 프레스티지' },
    { name: '셀토스', spec: '1.6 가솔린 터보 트렌디' },
    { name: '팰리세이드', spec: '디젤 2.2 익스클루시브 7인승' }
  ];

  const itemsPerSlide = 4;
  const cardWidth = 260;
  const cardGap = 20;
  
  // 효율적인 복제: 3배 (30개) - 가볍고 충분함
  const extendedCars = React.useMemo(() => {
    const copies = 3;
    return Array(copies).fill(null).flatMap(() => specialCars);
  }, []);
  
  // 중간에서 시작 (15번)
  const centerIndex = Math.floor(extendedCars.length / 2);
  const [currentSlide, setCurrentSlide] = React.useState(centerIndex);
  const [autoSlideKey, setAutoSlideKey] = React.useState(0); // 타이머 리셋용
  
  // 디바운스 훅 사용
  const { isTransitioning, executeDebounced, completeTransition } = useSlideDebounce();

  const handlePrevSlide = () => {
    executeDebounced(() => {
      setCurrentSlide(prev => prev - 1);
      setAutoSlideKey(prev => prev + 1); // 타이머 초기화
    });
  };

  const handleNextSlide = () => {
    executeDebounced(() => {
      setCurrentSlide(prev => prev + 1);
      setAutoSlideKey(prev => prev + 1); // 타이머 초기화
    });
  };

  // Transition 끝났을 때 처리
  const handleTransitionEnd = () => {
    const minBoundary = specialCars.length; // 10
    const maxBoundary = extendedCars.length - specialCars.length; // 20
    
    // 경계를 벗어났으면 중앙으로 점프
    if (currentSlide <= minBoundary || currentSlide >= maxBoundary) {
      completeTransition();
      setTimeout(() => {
        setCurrentSlide(centerIndex);
      }, 10);
    } else {
      completeTransition();
    }
  };

  // 2초마다 자동 슬라이드 (버튼 클릭 시 초기화)
  React.useEffect(() => {
    const autoSlide = setInterval(() => {
      executeDebounced(() => {
        setCurrentSlide(prev => prev + 1);
      });
    }, 2000);

    return () => clearInterval(autoSlide);
  }, [autoSlideKey, executeDebounced]); // autoSlideKey 변경 시 타이머 재시작

  

  const cars = [
    {
      rank: 1,
      name: '쏘렌토',
      brand: '(디젤/아이보리색)',
      year: '2022년',
      mileage: '17,739km',
      description: '뛰밀러 + 일괄 결좌 SUV, 공간 활용도와 연비 우수\n실제적 컨텐츠 높고, 인수 수요도 많은 다목 렌트카',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=200&h=150&fit=crop'
    },
    {
      rank: 2,
      name: '쏘렌토',
      brand: '(디젤/아이보리색)',
      year: '2022년',
      mileage: '17,739km',
      description: '뛰밀러 + 일괄 결좌 SUV, 공간 활용도와 연비 우수\n실제적 컨텐츠 높고, 인수 수요도 많은 다목 렌트카',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=200&h=150&fit=crop'
    },
    {
      rank: 3,
      name: '쏘렌토',
      brand: '(디젤/아이보리색)',
      year: '2022년',
      mileage: '17,739km',
      description: '뛰밀러 + 일괄 결좌 SUV, 공간 활용도와 연비 우수\n실제적 컨텐츠 높고, 인수 수요도 많은 다목 렌트카',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=200&h=150&fit=crop'
    },
    {
      rank: 4,
      name: '쏘렌토',
      brand: '(디젤/아이보리색)',
      year: '2022년',
      mileage: '17,739km',
      description: '뛰밀러 + 일괄 결좌 SUV, 공간 활용도와 연비 우수\n실제적 컨텐츠 높고, 인수 수요도 많은 다목 렌트카',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=200&h=150&fit=crop'
    },
    {
      rank: 5,
      name: '쏘렌토',
      brand: '(디젤/아이보리색)',
      year: '2022년',
      mileage: '17,739km',
      description: '뛰밀러 + 일괄 결좌 SUV, 공간 활용도와 연비 우수\n실제적 컨텐츠 높고, 인수 수요도 많은 다목 렌트카',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=200&h=150&fit=crop'
    }
  ];
  


  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: prev.minutes - 1, seconds: 59 };
        } else if (prev.hours > 0) {
          return { ...prev, hours: prev.hours - 1, minutes: 59, seconds: 59 };
        } else if (prev.days > 0) {
          return { ...prev, days: prev.days - 1, hours: 23, minutes: 59, seconds: 59 };
        }
        return prev;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div>
    
    
    <div className="home">
      <div className="page-container" style={{ marginTop: 0 }}>
        {/* 메인 콘텐츠 영역 */}
        <div className="main-content-wrapper">
        {/* 왼쪽 히어로 배너 (840x450) */}
        <div className="hero-section">
          
          {/* 메인 콘텐츠 - 가로 배치 */}
          <div className="main-hero-section">
            {/* 전국 단 1대 특가차량 배너 */}
            <section className="hero-banner">
           
            </section>

            {/* 당일 견적확인 폼 (420x450px) */}
            <div className="quote-form-section">
  <div className="quote-form-card">
    <div className="form-header">
      <span className="flame-icon"></span>
      <h3>당일 견적확인</h3>
    </div>
    
    <form className="quote-form">
      <div className="form-group">
        <label>이름 <span className="required">*</span></label>
        <input type="text" placeholder="예) 홍길동" />
      </div>
      
      <div className="form-group">
        <label>연락처 <span className="required">*</span></label>
        <input type="tel" placeholder="예) 01012345678 (-제외)" />
      </div>
      
      <div className="form-group">
        <label>차종 <span className="required">*</span></label>
        <input type="text" placeholder="예) 렌터카" />
      </div>
      
      <div className="checkbox-group">
        <label className="checkbox-label">
          <input type="checkbox" defaultChecked />
          <span className="checkmark"></span>
          [필수] 개인정보 수집-이용-제공 동의 <span className="link">[보기]</span>
        </label>
        
        <label className="checkbox-label">
          <input type="checkbox" defaultChecked />
          <span className="checkmark"></span>
          [필수] 개인정보 제3자 제공 동의 <span className="link">[보기]</span>
        </label>
      </div>
      
      <button type="button" className="consult-btn blue">비대면 상담 신청</button>
      <button type="button" className="consult-btn yellow">
        <span className="phone-icon"></span>
        전화 상담 1577-8319
      </button>
    </form>
  </div>
</div>
          </div>
        </div>
          {/* 마감임박 섹션 */}
          <section className="closing-soon">
            <div>
            <div className="section-header">
              <div className="header-icon">⏰</div>
              <h2>마감임박</h2>
            </div>
            </div>
            <p className="section-subtitle">현재 인기 차종, 단 3대 남았습니다</p>
            
            <div className="countdown-timer">
              <div className="timer-item">
                <div className="number-box">{timeLeft.days}</div>
                <span className="unit">일</span>
              </div>
              <div className="timer-item">
                <div className="number-box">{timeLeft.hours}</div>
                <span className="unit">시</span>
              </div>
              <div className="timer-item">
                <div className="number-box">{timeLeft.minutes}</div>
                <span className="unit">분</span>
              </div>
              <div className="timer-item">
                <div className="number-box">{timeLeft.seconds}</div>
                <span className="unit">초</span>
              </div>
            </div>

            <div className="featured-cars">
              {[1, 2, 3].map((item) => (
                <div key={item} className="featured-car-card">
                  <div className="featured-car-card-top">
                    <img src="https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop" alt="차량 이미지" />
                  </div>
                  <div className="featured-car-card-bottom">
                    <div className="car-desc">
                      <h4>더 뉴 스포티지 NQ5 하이브리드</h4>
                      <p>2.0 시그니처 트림</p>
                    </div>
                    <button className="quote-btn">빠른 상담 받기</button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 주간 인기차량 TOP 5 */}
          <section className="popular-cars">
            <div className="section-header">
              <h2>주간 인기차량 TOP 5</h2>
              <p className="section-subtitle">지금 리얼타임 인기 차량으로 선정된 차량 확인하세요</p>
            </div>
            
            <div className="cars-list">
              {cars.map((car) => (
                <CarCard key={car.rank} {...car} />
              ))}
            </div>
          </section>

          {/* 유튜브 섹션 */}
          <section className="youtube-section">
            <YoutubeCard />
          </section>

          {/* 블로그 섹션 - 전용 컴포넌트 (Home.css 재사용 안 함) */}
          <WonderBlogSection />
          </div>
        </div>
      </div>

        {/* 특가 차량 섹션 - 홈 컨테이너 밖 */}
        <section className="special-offers">
        <div className="special-offers-header">
          <div className="special-offers-title-wrapper">
            <span className="special-offers-icon">🎆</span>
            <h2 className="special-offers-title">특가 차량, 지금 아니면 놓칩니다!</h2>
          </div>
          <p className="special-offers-subtitle">계약 순서에 따라 혜택은 조기 종료될 수 있습니다.</p>
        </div>
        
        <div className="special-cars-carousel">
          <button 
            className="special-carousel-btn special-prev" 
            onClick={handlePrevSlide}
            aria-label="이전 차량"
          >
            <svg width="54" height="54" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          
          <div className="special-cars-list-wrapper">
            <div 
              className="special-cars-list"
              style={{
                transform: `translateX(-${currentSlide * (cardWidth + cardGap)}px)`,
                transition: isTransitioning ? 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)' : 'none'
              }}
              onTransitionEnd={handleTransitionEnd}
            >
              {extendedCars.map((car, index) => (
                <div key={index} className="special-car-card">
                  <div className="special-car-image">
                    <img src="https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop" alt={car.name} />
                  </div>
                  <div className="special-car-info">
                    <h4>{car.name}</h4>
                    <p>{car.spec}</p>
                  </div>
                  <button className="special-car-btn">비대면 견적신청</button>
                </div>
              ))}
            </div>
          </div>
          
          <button 
            className="special-carousel-btn special-next" 
            onClick={handleNextSlide}
            aria-label="다음 차량"
          >
            <svg width="54" height="54" viewBox="0 0 24 24" fill="none">
              <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        
        <button className="more-cars-btn">
          더 많은 차량 보기
          <svg width="32" height="32" viewBox="0 0 20 20" fill="none">
            <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </section>
    </div>
  );
};

export default Home;