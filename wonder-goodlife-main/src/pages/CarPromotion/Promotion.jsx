import React, { useState } from 'react';
import EstimateModal from '../../components/modals/EstimateModal';
import Breadcrumb from '../../components/Breadcrumb';
import EventCard from '../../components/EventCard';
import { useNavigate } from 'react-router-dom';
import styles from './Promotion.module.css';

// 카드 데이터: 디자인 시안에 맞춰 카테고리/배지/테마 포함
const cardDataByBrand = {
  현대차: [
    { id: 1, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '쏘나타', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=900&h=560&fit=crop' },
    { id: 2, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '아반떼', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1542362567-b07e54358753?w=900&h=560&fit=crop' },
    { id: 3, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '투싼', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=900&h=560&fit=crop' },
    { id: 4, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '팰리세이드', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1619767886558-efdc259cde1b?w=900&h=560&fit=crop' },
    { id: 5, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '아이오닉', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1619767886558-efdc259cde1b?w=900&h=560&fit=crop' },
    { id: 6, title: '현대차 프로모션', badge: 'PROMOTION', theme: 'hyundai', name: '캐스퍼', desc: '지금 특가, 실제 딜러사 행사 문의', img: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=900&h=560&fit=crop' }
  ],
  기아: [
    { id: 7, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: 'K5', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1617531653520-bd466e19bc3e?w=900&h=560&fit=crop' },
    { id: 8, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: '쏘렌토', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=900&h=560&fit=crop' },
    { id: 9, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: 'EV6', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1619767886558-efdc259cde1b?w=900&h=560&fit=crop' },
    { id: 10, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: 'K3', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=900&h=560&fit=crop' },
    { id: 11, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: '레이', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1542362567-b07e54358753?w=900&h=560&fit=crop' },
    { id: 12, title: 'KIA', badge: 'BEST SELLER', theme: 'kia', name: '니로', desc: '가장 사랑받는 베스트 셀러', img: 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=900&h=560&fit=crop' }
  ],
  'MERCEDES-BENZ': [
    { id: 13, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'C-Class', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1606016159991-5de14d7a9ac0?w=900&h=560&fit=crop' },
    { id: 14, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'E-Class', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=900&h=560&fit=crop' },
    { id: 15, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'GLC', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=900&h=560&fit=crop' },
    { id: 16, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'A-Class', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=900&h=560&fit=crop' },
    { id: 17, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'CLA', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=900&h=560&fit=crop' },
    { id: 18, title: 'MERCEDES - BENZ', badge: '', theme: 'mercedes', name: 'GLE', desc: '수입차 특별가 라인업', img: 'https://images.unsplash.com/photo-1617531653520-bd466e19bc3e?w=900&h=560&fit=crop' }
  ],
  트럭특수: [
    { id: 19, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '마이티', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1585386959984-a41552231658?w=900&h=560&fit=crop' },
    { id: 20, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '포터', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?w=900&h=560&fit=crop' },
    { id: 21, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '카고', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1493238792000-8113da705763?w=900&h=560&fit=crop' },
    { id: 22, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '덤프', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=900&h=560&fit=crop' },
    { id: 23, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '집게차', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1548690312-e3b507d8c110?w=900&h=560&fit=crop' },
    { id: 24, title: '트럭·특수오토바이', badge: 'EVENT', theme: 'truck', name: '특수오토바이', desc: '즉시 가능한 특수/상용차 혜택', img: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=900&h=560&fit=crop' }
  ]
};

export default function Promotion() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const [tab, setTab] = useState('active');

  // 탭별 데이터 분리(시안 기준 2x3)
  const activeItems = [
    cardDataByBrand['현대차'][0],
    cardDataByBrand['기아'][0],
    cardDataByBrand['MERCEDES-BENZ'][0],
    cardDataByBrand['현대차'][1],
    cardDataByBrand['기아'][1],
    cardDataByBrand['트럭특수'][0]
  ];

  const endedItems = [
    cardDataByBrand['현대차'][2],
    cardDataByBrand['기아'][2],
    cardDataByBrand['MERCEDES-BENZ'][1],
    cardDataByBrand['현대차'][3],
    cardDataByBrand['기아'][3],
    cardDataByBrand['트럭특수'][1]
  ];

  const displayedItems = tab === 'active' ? activeItems : endedItems;

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '할인 프로모션', link: '/promotion' },
    { label: '브랜드별 혜택' }
  ];

  return (
    <div className={styles['promo-page']}>
      <div className={`${styles['promo-container']} ${tab === 'ended' ? styles['ended'] : ''}`}>
        <Breadcrumb items={breadcrumbItems} />

        <div className={styles['promo-header']}>
          <h2 className={styles['promo-title']}>브랜드별 혜택</h2>
          <p className={styles['promo-sub']}>원더가 제안하는 브랜드별 혜택, 지금 확인해보세요</p>
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
            <EventCard
              key={c.id}
              title={c.title}
              subtitle={c.badge}
              image={c.img}
              description={c.desc}
              theme={c.theme}
              ended={tab === 'ended'}
              onClick={() => navigate(`/promotion/brands/detail/${c.id}`)}
            />
          ))}
        </div>

        <div className={styles['promo-more']}>
          <button type="button" className={styles['promo-more-btn']} onClick={()=>window.location.assign('/promotion/brands?tab=active')}>더 많은 차량별 혜택 보기 {'>'}</button>
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

      <EstimateModal open={open} onClose={() => setOpen(false)} carName="브랜드별 혜택 프로모션" />
    </div>
  );
}


