import React, { useState, useEffect, useRef } from 'react';
import HomeStyle from './Home.module.css';
import CarCard from '../../components/CarCard';
import YoutubeCard from '../../components/YoutubeCard';
import SpecialOffersSection from '../../components/SpecialOffersSection';
import ExpressDealsSection from '../../components/ExpressDealsSection';
import PromotionCard from '../../components/PromotionCard';
import { useSlideDebounce } from '../../hooks/useSlideDebounce';

const Home = () => {
  const [timeLeft, setTimeLeft] = useState({
    days: 10,
    hours: 15,
    minutes: 57,
    seconds: 17
  });

  const partnerCardsRef = useRef(null);
  const [currentScrollIndex, setCurrentScrollIndex] = useState(0);

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

  // 제휴카드사 자동 스크롤
  useEffect(() => {
    const scrollTimer = setInterval(() => {
      if (partnerCardsRef.current) {
        const cardWidth = 120; // 카드 너비 + 간격
        const maxScroll = partnerCardsRef.current.scrollWidth - partnerCardsRef.current.clientWidth;
        
        setCurrentScrollIndex(prev => {
          const nextIndex = prev + 1;
          const scrollPosition = Math.min(nextIndex * cardWidth, maxScroll);
          
          partnerCardsRef.current.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
          });
          
          // 끝에 도달하면 처음으로 돌아가기
          if (scrollPosition >= maxScroll) {
            setTimeout(() => {
              partnerCardsRef.current.scrollTo({
                left: 0,
                behavior: 'smooth'
              });
            }, 1000);
            return 0;
          }
          
          return nextIndex;
        });
      }
    }, 1000); // 1초마다 이동

    return () => clearInterval(scrollTimer);
  }, []);

  return (
    <div>
    
    
    <div className={HomeStyle['home']}>
      <div className={HomeStyle['page-container']} style={{ marginTop: 0 }}>
        {/* 메인 콘텐츠 영역 */}
        <div className={HomeStyle['main-content-wrapper']}>
        {/* 왼쪽 히어로 배너 (840x450) */}
        <div className={HomeStyle['hero-section']}>
          
          {/* 메인 콘텐츠 - 가로 배치 */}
          <div className={HomeStyle['main-hero-section']}>
            {/* 전국 단 1대 특가차량 배너 */}
            <section className={HomeStyle['hero-banner']}>
           
            </section>

            {/* 당일 견적확인 폼 (420x450px) */}
            <div className={HomeStyle['quote-form-section']}>
  <div className={HomeStyle['quote-form-card']}>
    <div className={HomeStyle['form-header']}>
      <span className={HomeStyle['flame-icon']}></span>
      <h3>당일 견적확인</h3>
    </div>
    
    <form className={HomeStyle['quote-form']}>
      <div className={HomeStyle['form-group']}>
        <label>이름 <span className={HomeStyle['required']}>*</span></label>
        <input type="text" placeholder="예) 홍길동" />
      </div>
      
      <div className={HomeStyle['form-group']}>
        <label>연락처 <span className={HomeStyle['required']}>*</span></label>
        <input type="tel" placeholder="예) 01012345678 (-제외)" />
      </div>
      
      <div className={HomeStyle['form-group']}>
        <label>차종 <span className={HomeStyle['required']}>*</span></label>
        <input type="text" placeholder="예) 렌터카" />
      </div>
      
      <div className={HomeStyle['checkbox-group']}>
        <label className={HomeStyle['checkbox-label']}>
          <input type="checkbox" defaultChecked />
          <span className={HomeStyle['checkmark']}></span>
          [필수] 개인정보 수집-이용-제공 동의 <span className={HomeStyle['link']}>[보기]</span>
        </label>
        
        <label className={HomeStyle['checkbox-label']}>
          <input type="checkbox" defaultChecked />
          <span className={HomeStyle['checkmark']}></span>
          [필수] 개인정보 제3자 제공 동의 <span className={HomeStyle['link']}>[보기]</span>
        </label>
      </div>
      
      <button type="button" className={`${HomeStyle['consult-btn']} ${HomeStyle['blue']}`}>비대면 상담 신청</button>
      <button type="button" className={`${HomeStyle['consult-btn']} ${HomeStyle['yellow']}`}>
        <span className={HomeStyle['phone-icon']}></span>
        전화 상담 1577-8319
      </button>
    </form>
  </div>
</div>
          </div>
        </div>
          {/* 마감임박 섹션 */}
          <section className={HomeStyle['closing-soon']}>
        
            <div className={HomeStyle['section-header']}>
              <div className={HomeStyle['header-icon']}>⏰</div>
              <h2>마감임박</h2>
            </div>  
            <p className={HomeStyle['section-subtitle']}>현재 인기 차종, 단 3대 남았습니다</p>
            
            <div className={HomeStyle['countdown-timer']}>
              <div className={HomeStyle['timer-item']}>
                <div className={HomeStyle['number-box']}>{timeLeft.days}</div>
                <span className={HomeStyle['unit']}>일</span>
              </div>
              <div className={HomeStyle['timer-item']}>
                <div className={HomeStyle['number-box']}>{timeLeft.hours}</div>
                <span className={HomeStyle['unit']}>시</span>
              </div>
              <div className={HomeStyle['timer-item']}>
                <div className={HomeStyle['number-box']}>{timeLeft.minutes}</div>
                <span className={HomeStyle['unit']}>분</span>
              </div>
              <div className={HomeStyle['timer-item']}>
                <div className={HomeStyle['number-box']}>{timeLeft.seconds}</div>
                <span className={HomeStyle['unit']}>초</span>
              </div>
            </div>

            <div className={HomeStyle['featured-cars']}>
              {[
                { id: 1, name: '더 뉴 스포티지 NQ5 하이브리드', desc: '2.0 시그니처 트림', img: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop', brand: 'KIA' },
                { id: 2, name: '카니발 1.6 터보 하이브리드', desc: '시그니처 11인승', img: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop', brand: 'KIA' },
                { id: 3, name: 'G80 전기차', desc: '롱 레인지 2WD', img: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop', brand: 'GENESIS' }
              ].map((car) => (
                <PromotionCard
                  key={car.id}
                  id={car.id}
                  name={car.name}
                  desc={car.desc}
                  img={car.img}
                  brand={car.brand}
                  onClick={(id) => console.log('마감임박 차량 클릭:', id)}
                  buttonText="빠른 상담 받기"
                  variant="big"
                />
              ))}
            </div>
          </section>

          {/* 주간 인기차량 TOP 5 */}
          <section className={HomeStyle['popular-cars']}>
            <div className={HomeStyle['section-header']}>
              <h2>주간 인기차량 TOP 5</h2>
              <p className={HomeStyle['section-subtitle']}>지금 리얼타임 인기 차량으로 선정된 차량 확인하세요</p>
            </div>
            
            <div className={HomeStyle['cars-list']}>
              {cars.map((car) => (
                <CarCard key={car.rank} {...car} />
              ))}
            </div>
          </section>
          </div>
          </div>
          </div>
          {/* 유튜브 섹션 */}
          <section className={HomeStyle['youtube-section']}>
            <YoutubeCard />
          </section>

          {/* 특가차량 섹션 */}
          <SpecialOffersSection />

          {/* 즉시출고차량 섹션 */}
          <ExpressDealsSection />

          {/* 제휴카드사 섹션 */}
          <section className={HomeStyle['partner-cards-section']}>
            <div className={HomeStyle['partner-cards-header']}>
              <h2 className={HomeStyle['partner-cards-title']}>제휴카드사</h2>
              <p className={HomeStyle['partner-cards-subtitle']}>
                국내 30여 개 제휴사 데이터를 비교 분석하여, 고객님께 딱 맞는 최저가 견적만을 제공합니다.
              </p>
            </div>
            
            <div ref={partnerCardsRef} className={HomeStyle['partner-cards-grid']}>
              {/* 카드사 목록 - 30개 */}
              {[
                { name: '현대카드', color: '000000', textColor: 'FFFFFF' },
                { name: '신한카드', color: '0066CC', textColor: 'FFFFFF' },
                { name: '삼성카드', color: '0066CC', textColor: 'FFFFFF' },
                { name: '우리카드', color: '0066CC', textColor: 'FFFFFF' },
                { name: 'KB손해보험', color: 'FFD700', textColor: '000000' },
                { name: '아마존카', color: '00AA00', textColor: 'FFFFFF' },
                { name: '롯데렌터카', color: 'FF0000', textColor: 'FFFFFF' },
                { name: '하모니렌트카', color: '0066CC', textColor: 'FFFFFF' },
                { name: '하나카드', color: '009639', textColor: 'FFFFFF' },
                { name: 'BC카드', color: 'E60012', textColor: 'FFFFFF' },
                { name: 'NH카드', color: '004B9C', textColor: 'FFFFFF' },
                { name: '롯데카드', color: 'ED1C24', textColor: 'FFFFFF' },
                { name: 'KB국민카드', color: 'FFD700', textColor: '000000' },
                { name: '현대해상', color: '000000', textColor: 'FFFFFF' },
                { name: '삼성화재', color: '0066CC', textColor: 'FFFFFF' },
                { name: 'DB손해보험', color: 'FF6B35', textColor: 'FFFFFF' },
                { name: '한화손해보험', color: 'FF6600', textColor: 'FFFFFF' },
                { name: 'MG손해보험', color: '00A651', textColor: 'FFFFFF' },
                { name: 'AXA손해보험', color: '000000', textColor: 'FFFFFF' },
                { name: '메리츠화재', color: '0066CC', textColor: 'FFFFFF' },
                { name: 'KB손해보험', color: 'FFD700', textColor: '000000' },
                { name: '현대캐피탈', color: '000000', textColor: 'FFFFFF' },
                { name: '신한캐피탈', color: '0066CC', textColor: 'FFFFFF' },
                { name: '삼성캐피탈', color: '0066CC', textColor: 'FFFFFF' },
                { name: '우리캐피탈', color: '0066CC', textColor: 'FFFFFF' },
                { name: 'KB캐피탈', color: 'FFD700', textColor: '000000' },
                { name: '하나캐피탈', color: '009639', textColor: 'FFFFFF' },
                { name: '롯데캐피탈', color: 'ED1C24', textColor: 'FFFFFF' },
                { name: 'NH캐피탈', color: '004B9C', textColor: 'FFFFFF' },
                { name: 'BC캐피탈', color: 'E60012', textColor: 'FFFFFF' }
              ].map((card, index) => (
                <div key={index} className={HomeStyle['partner-card']}>
                  <div className={HomeStyle['partner-logo']}>
                    <img 
                      src={`https://via.placeholder.com/140x140/${card.color}/${card.textColor}?text=${encodeURIComponent(card.name)}`} 
                      alt={card.name} 
                    />
                  </div>
                  <span className={HomeStyle['partner-name']}>{card.name}</span>
                </div>
              ))}
            </div>
          </section>

    
    </div>
  );
};

export default Home;