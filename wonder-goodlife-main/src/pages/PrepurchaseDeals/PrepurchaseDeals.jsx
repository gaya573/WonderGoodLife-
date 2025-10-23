import React, { useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import SearchBar from '../../components/SearchBar';
import CarFilterPanel from '../../components/filters/CarFilterPanel';
import PromotionCard from '../../components/PromotionCard';
import styles from './PrepurchaseDeals.module.css';
import { dealsTop as dataTop, deals as dataAll } from '../ExpressDeals/data';

const PrepurchaseDeals = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [minPrice, setMinPrice] = useState(Number(searchParams.get('min') || 60));
  const [maxPrice, setMaxPrice] = useState(Number(searchParams.get('max') || 240));
  const [sortBy, setSortBy] = useState('recent');
  const [searchQuery, setSearchQuery] = useState('');
  const [manufacturer, setManufacturer] = useState(searchParams.get('maker') || '전체');
  const [carType, setCarType] = useState(searchParams.get('type') || '전체');
  const [fuel, setFuel] = useState(searchParams.get('fuel') || '전체');

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '선구매 핫딜 특가' }
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

  const dealsTop = dataTop;
  const deals = dataAll;

  const filtered = useMemo(() => {
    let list = [...deals];
    if (searchQuery) list = list.filter(d => d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.brand.toLowerCase().includes(searchQuery.toLowerCase()));
    switch (sortBy) {
      case 'priceLow': list.sort((a,b)=>a.price-b.price); break;
      case 'priceHigh': list.sort((a,b)=>b.price-a.price); break;
      case 'recent': default: break;
    }
    return list;
  }, [deals, searchQuery, sortBy]);

  const syncParams = (next) => {
    const params = new URLSearchParams(searchParams);
    Object.entries(next).forEach(([k,v]) => { if (v === '전체' || v === undefined || v === null) params.delete(k); else params.set(k, String(v)); });
    setSearchParams(params, { replace: true });
  };

  const handleMinPriceChange = (e) => {
    const value = Number(e.target.value);
    if (value <= maxPrice - 10) { setMinPrice(value); syncParams({ min: value, max: maxPrice }); }
  };
  const handleMaxPriceChange = (e) => {
    const value = Number(e.target.value);
    if (value >= minPrice + 10) { setMaxPrice(value); syncParams({ min: minPrice, max: value }); }
  };

  const handleSelectManufacturer = (name) => { setManufacturer(name); syncParams({ maker: name }); };
  const handleSelectCarType = (value) => { setCarType(value); syncParams({ type: value }); };
  const handleSelectFuel = (value) => { setFuel(value); syncParams({ fuel: value }); };

  const handleCardClick = () => navigate('/prepurchase-deals/detail/0');

  return (
    <div className={styles['express-page']}>
      <div className={styles['express-container']}>
        <Breadcrumb items={breadcrumbItems} />

        <div className={styles['express-banner']}>
          <div className={styles['express-banner-inner']}>
            <div className={styles['express-banner-text']}>
              <h2>선구매 핫딜 특가</h2>
              <p>조기 계약으로 더 좋은 혜택, 선구매 핫딜 모음</p>
            </div>
            <button className={styles['express-banner-cta']} onClick={()=>window.scrollTo({top:999999, behavior:'smooth'})}>상담 받기</button>
          </div>
        </div>


        <section className={styles['express-top-highlights']}>
          <div className={styles['section-header']}>
            <h3 className={styles['section-title']}>🚨 [특가 마감 임박] 지금 계약 시 특별 할인</h3>
            <button className={styles['section-link']} onClick={()=>navigate('/prepurchase-deals/all')}>전체보기</button>
          </div>
          <div className={styles['top-grid-scroll']}>
            <div className={styles['top-grid']}>
              {dealsTop.map((d, idx) => (
                <PromotionCard
                  key={d.id ?? idx}
                  id={d.id ?? idx}
                  name={d.name}
                  desc={d.brand ? `${d.brand}\n선구매 특가` : '선구매 특가'}
                  img={d.image}
                  brand={d.brand}
                  variant="small"
                  onClick={handleCardClick}
                  buttonText="내 견적 알아보기"
                />
              ))}
            </div>
          </div>
        </section>
        <div className={styles['express-list-sticky']}>
              <div className={styles['express-list-header']}>
                <h2 className={styles['express-list-title']}>선구매 핫딜 리스트</h2>
             
              </div>
            </div>
        <div className={styles['express-layout']}>
          <CarFilterPanel
            manufacturers={manufacturers}
            carTypes={carTypes}
            fuelTypes={fuelTypes}
            minPrice={minPrice}
            maxPrice={maxPrice}
            priceRanges={priceRanges}
            onMinPriceChange={handleMinPriceChange}
            onMaxPriceChange={handleMaxPriceChange}
            selectedManufacturer={manufacturer}
            onSelectManufacturer={handleSelectManufacturer}
            selectedCarType={carType}
            onSelectCarType={handleSelectCarType}
            selectedFuel={fuel}
            onSelectFuel={handleSelectFuel}
          />

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
              
              <SearchBar 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="차량 모델, 제조사를 검색해보세요"
                  variant="long"
                />
              </div>
            </div>

            <div>
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
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default PrepurchaseDeals;


