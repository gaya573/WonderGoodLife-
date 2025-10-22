import React, { useState } from 'react';
import EstimateModal from '../../components/modals/EstimateModal';
import Breadcrumb from '../../components/Breadcrumb';
import { useNavigate } from 'react-router-dom';
import styles from './CardPromotion.module.css';
import { cardBrandCards } from './data';

export default function CardPromotion() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const [tab, setTab] = useState('active');

  // 탭별 데이터 분리(카드 브랜드 기준)
  const activeItems = [
    cardBrandCards['신한'][0],
    cardBrandCards['KB국민'][0],
    cardBrandCards['현대'][0],
    cardBrandCards['롯데'][0],
    cardBrandCards['하나'][0],
    cardBrandCards['삼성'][0]
  ];

  const endedItems = [
    cardBrandCards['BC'][0],
    cardBrandCards['NH농협'][0],
    cardBrandCards['우리'][0],
    cardBrandCards['카카오뱅크'][0],
    cardBrandCards['신한'][0],
    cardBrandCards['KB국민'][0]
  ];

  const displayedItems = tab === 'active' ? activeItems : endedItems;

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '카드 프로모션', link: '/card-promotion' },
    { label: '카드 브랜드별 혜택' }
  ];

  return (
    <div className={styles['promo-page']}>
      <div className={`${styles['promo-container']} ${tab === 'ended' ? styles['ended'] : ''}`}>
        <Breadcrumb items={breadcrumbItems} />

        <div className={styles['promo-header']}>
          <h2 className={styles['promo-title']}>카드 브랜드별 혜택</h2>
          <p className={styles['promo-sub']}>원더가 제안하는 카드 브랜드별 혜택, 지금 확인해보세요</p>
          <div className={styles['promo-tabs']}>
            <button
              type="button"
              className={`${styles['promo-tab']} ${tab === 'active' ? styles['active'] : ''}`}
              onClick={() => setTab('active')}
            >
              진행중 기획전
            </button>
            <button
              type="button"
              className={`${styles['promo-tab']} ${tab === 'ended' ? styles['active'] : ''}`}
              onClick={() => setTab('ended')}
            >
              종료된 기획전
            </button>
          </div>
        </div>

        <div className={styles['promo-grid']}>
          {displayedItems.map((c) => (
            <article key={c.id} className={`${styles['promo-card']} ${styles[`theme-${c.theme}`]}`}>
              <div className={styles['promo-card-top']}>
           
                <img src={c.img} alt={c.name} />
              </div>
              <div className={styles['promo-card-body']}>
                <h3>{c.name}</h3>
                <p>{c.desc}</p>
              </div>
              <button className={styles['promo-card-btn']} onClick={() => navigate(`/card-promotion/brands/detail/${c.id}`)}>카드 혜택 상담 받기</button>
            </article>
          ))}
        </div>

        <div className={styles['promo-more']}>
          <button type="button" className={styles['promo-more-btn']} onClick={()=>window.location.assign('/card-promotion/brands?tab=active')}>더 많은 카드별 혜택 보기 {'>'}</button>
        </div>

        <section className={styles['promo-bottom-cta']}>
          <div className={styles['cta-visual']} aria-hidden="true" />
          <div className={styles['cta-wrap']}>
            <div className={styles['cta__heading']}>“1:1 맞춤견적, 지금 바로 상담받기”</div>
            <form onSubmit={(e) => { e.preventDefault(); setOpen(true); }} className={styles['cta__form']}>
              <div className={styles['cta__fields']}>
                <div className={styles['cta__row']}>
                  <label htmlFor="cta-name" className={styles['cta__label']}>이름</label>
                  <input id="cta-name" className={styles['cta__input']} type="text" placeholder="이름" aria-label="이름" />
                </div>
                <div className={styles['cta__row']}>
                  <label htmlFor="cta-phone" className={styles['cta__label']}>연락처</label>
                  <input id="cta-phone" className={styles['cta__input']} type="tel" placeholder="연락처" aria-label="연락처" />
                </div>
              </div>
              <div className={styles['cta__actions']}>
                <button className={styles['cta__submit']} type="submit">상담신청</button>
              </div>
            </form>
          </div>
        </section>

      </div>

      <EstimateModal open={open} onClose={() => setOpen(false)} carName="카드 브랜드별 혜택 프로모션" />
    </div>
  );
}


