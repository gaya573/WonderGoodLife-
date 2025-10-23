import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import SearchBar from '../../components/SearchBar';
import PromotionCard from '../../components/PromotionCard';
import CarFilterPanel from '../../components/filters/CarFilterPanel';
import styles from './PrepurchaseDealsAll.module.css';
import { deals as dataAll } from '../ExpressDeals/data';

const PrepurchaseDealsAll = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '선구매 핫딜 특가', link: '/prepurchase-deals' },
    { label: '전체보기' },
  ];

  const manufacturers = [
    { name: '전체', logo: null },
    { name: '현대', logo: '🚗' },
    { name: '기아', logo: '🚙' },
    { name: '제네시스', logo: '🚘' },
    { name: '쉐보레', logo: '🚐' }
  ];
  const carTypes = ['전체', 'SUV', '세단', '전기', '하이브리드', '승합'];
  const fuelTypes = ['전체', '가솔린', '디젤', '하이브리드', '전기'];
  const priceRanges = ['60만원', '120만원', '240만원'];

  const filtered = useMemo(() => {
    let list = [...dataAll];
    if (searchQuery) list = list.filter(d => d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.brand.toLowerCase().includes(searchQuery.toLowerCase()));
    switch (sortBy) {
      case 'priceLow': list.sort((a,b)=>a.price-b.price); break;
      case 'priceHigh': list.sort((a,b)=>b.price-a.price); break;
      case 'recent': default: break;
    }
    return list;
  }, [searchQuery, sortBy]);

  const handleCardClick = (id) => navigate(`/prepurchase-deals/detail/${id ?? 0}`);

  return (
    <div className={styles['express-page']}>
      <div className={styles['express-container']}>
        <Breadcrumb items={breadcrumbItems} />
        <div className={styles['section-header']}>
                <h3 className={styles['section-title']}>🚨 [특가 마감 임박] 지금 계약 시 특별 할인</h3>
              </div>
        <div >
          
        </div>

        <div className={styles['express-layout']}>
        

          <main className={styles['express-main']}>
            <div className={styles['express-toolbar']}>
              <div className={styles['express-sort']}>
                <select value={sortBy} onChange={(e)=>setSortBy(e.target.value)} className={styles['carlist-sort-select']}>
                  <option value="recent">최신순</option>
                  <option value="priceLow">가격낮은순</option>
                  <option value="priceHigh">가격높은순</option>
                </select>
              </div>
              <div className={styles['express-search']}>
                <SearchBar value={searchQuery} onChange={(e)=>setSearchQuery(e.target.value)} placeholder="모델/제조사 검색" variant="long" />
              </div>
            </div>

            <div className={styles['carlist-grid']}>
              {filtered.map((d, idx) => (
                <PromotionCard
                  key={d.id ?? idx}
                  id={d.id ?? idx}
                  name={d.name}
                  desc={d.brand ? `${d.brand}\n월 ${d.price}만원~` : `월 ${d.price}만원~`}
                  img={d.image}
                  brand={d.brand}
                  onClick={handleCardClick}
                  buttonText="내 견적 알아보기"
                />
              ))}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default PrepurchaseDealsAll;
