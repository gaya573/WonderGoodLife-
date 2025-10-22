import React, { useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import styles from './PromotionBrands.module.css';
import { brandCards as cardDataByBrand, allBrandCards } from './data';


const BRANDS = [
  '전체',
  '현대',
  '기아',
  '제네시스',
  '한국지엠(쉐보레)',
  'KGM',
  '르노코리아',
  '테슬라',
  '벤츠',
  'BMW',
  '기타 수입차'
];

export default function PromotionBrands() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [tab, setTab] = useState(searchParams.get('tab') || 'active');
  const [brand, setBrand] = useState(searchParams.get('maker') || '전체');

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '할인 프로모션', link: '/promotion' },
    { label: '브랜드별 혜택 전체' }
  ];

  const allCards = useMemo(() => allBrandCards, []);

  const displayed = useMemo(() => {
    const list = brand === '전체' ? allCards : (cardDataByBrand[brand] || []);
    return list;
  }, [brand, allCards]);

  const handleSelectBrand = (next) => {
    setBrand(next);
    const p = new URLSearchParams(searchParams);
    if (next === '전체') p.delete('maker'); else p.set('maker', next);
    setSearchParams(p, { replace: true });
  };

  const isEnded = tab === 'ended';

  return (
    <div className={styles['promo-page']}>
      <div className={`${styles['promo-container']} ${isEnded ? styles['ended'] : ''}`}>
        <Breadcrumb items={breadcrumbItems} />

        <div className={styles['promo-header']}>
          <h2 className={styles['promo-title']}>브랜드별 혜택 전체2</h2>
          <p className={styles['promo-sub']}>브랜드 선택 후, 진행중/종료된 기획전을 확인하세요</p>
         
        </div>

        <div className={styles['brand-bar']} role="listbox" aria-label="브랜드 선택">
          <div className={styles['brand-scroller']}>
            {BRANDS.map((b) => (
              <button
                key={b}
                type="button"
                className={`${styles['brand-pill']} ${brand === b ? styles['selected'] : ''}`}
                aria-selected={brand === b}
                onClick={() => handleSelectBrand(b)}
              >
                <div className={styles['brand-circle']} aria-hidden="true" />
                <span className={styles['brand-label']}>{b}</span>
              </button>
            ))}
          </div>
        </div>

        <div className={styles['promo-grid']}>
          {displayed.map((c) => (
            <article key={`${c.brand}-${c.id}`} className={styles['promo-card']} onClick={()=>navigate(`/promotion/brands/detail/${c.id}`)}>
              <div className={styles['promo-card-top']}>
                <img src={c.img} alt={c.name} loading="lazy" />
              </div>
              <div className={styles['promo-card-body']}>
                <h3>{c.name}</h3>
                <p>{c.desc}</p>
              </div>
              <button
                className={styles['promo-card-btn']}
                onClick={() => navigate(`/promotion/brands/detail/${c.id}`)}
              >
                혜택 상담 받기
              </button>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}


