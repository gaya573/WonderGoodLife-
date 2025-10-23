import React from 'react';
import PromotionCard from './PromotionCard';
import styles from './SpecialOffersSection.module.css';

const SpecialOffersSection = () => {
  const specialOffers = [
    {
      id: 1,
      name: '더 뉴 스포티지 NQ5 하이브리드',
      brand: 'KIA',
      year: '2024년',
      mileage: '신차',
      description: '2.5 터보 익스클루시브 9인승\n특가 할인 중',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop'
    },
    {
      id: 2,
      name: '카니발 1.6 터보 하이브리드',
      brand: 'KIA',
      year: '2024년',
      mileage: '신차',
      description: '시그니처 11인승\n특가 할인 중',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop'
    },
    {
      id: 3,
      name: 'G80 전기차',
      brand: 'GENESIS',
      year: '2024년',
      mileage: '신차',
      description: '롱 레인지 2WD\n특가 할인 중',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop'
    },
    {
      id: 4,
      name: '아이오닉 6',
      brand: 'HYUNDAI',
      year: '2024년',
      mileage: '신차',
      description: '롱 레인지 2WD 익스클루시브\n특가 할인 중',
      image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop'
    }
  ];

  return (
    <section className={styles['special-offers-section']}>
      <div className={styles['special-offers-header']}>
        <div className={styles['special-offers-title-wrapper']}>
          <span className={styles['special-offers-icon']}>🎆</span>
          <h2 className={styles['special-offers-title']}>특가 차량, 지금 아니면 놓칩니다!</h2>
        </div>
        <a href="/promotion" className={styles['special-offers-link']}>더 많은 차량 보기 →</a>
      </div>

      <div className={styles['special-offers-grid']}>
        {specialOffers.map((car) => (
          <PromotionCard
            key={car.id}
            id={car.id}
            name={car.name}
            desc={car.description}
            img={car.image}
            brand={car.brand}
            onClick={(id) => console.log('특가 차량 클릭:', id)}
            buttonText="빠른 상담받기"
          />
        ))}
      </div>

      <div className={styles['special-offers-disclaimer']}>
        * 계약 순서에 따라 혜택은 조기 종료될 수 있습니다.
      </div>
    </section>
  );
};

export default SpecialOffersSection;
