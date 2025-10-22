import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import SearchBar from '../../components/SearchBar';
import CarGrid from '../../components/grids/CarGrid';
import CarFilterPanel from '../../components/filters/CarFilterPanel';
import './ExpressDeals.css';
import { deals as dataAll } from './data';

const ExpressDealsAll = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(300);

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '즉시출고 특가', link: '/express-deals' },
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

  const handleCardClick = (id) => navigate(`/express-deals/detail/${id ?? 0}`);

  return (
    <div className="express-page">
      <div className="express-container">
        <Breadcrumb items={breadcrumbItems} />
        <div className="section-header">
                <h3 className="section-title">🔔 [긴급] 오늘 놓치면 마감 차량</h3>
              </div>
        <div >
          
        </div>

        <div className="express-layout">
        

          <main className="express-main">
            <div className="express-toolbar">
              <div className="express-sort">
                <select value={sortBy} onChange={(e)=>setSortBy(e.target.value)} className="carlist-sort-select">
                  <option value="recent">최신순</option>
                  <option value="priceLow">가격낮은순</option>
                  <option value="priceHigh">가격높은순</option>
                </select>
              </div>
              <div className="express-search">
                <SearchBar value={searchQuery} onChange={(e)=>setSearchQuery(e.target.value)} placeholder="모델/제조사 검색" />
              </div>
            </div>

            <CarGrid
              cars={filtered.map((d)=>({ id:d.id, name:d.name, img:d.image, priceText:`월 ${d.price}만원~` }))}
              onClickCard={handleCardClick}
              columns={4}
            />
          </main>
        </div>
      </div>
    </div>
  );
};

export default ExpressDealsAll;


