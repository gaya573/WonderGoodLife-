import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import "./CarList.css";
import Breadcrumb from "../../components/Breadcrumb";
import TabNav from "../../components/TabNav";
import CarFilterPanel from "../../components/filters/CarFilterPanel";
import SearchBar from "../../components/SearchBar";
import PromotionCard from "../../components/PromotionCard";

/**
 * WonderGoodLife – 왼쪽 고정 필터 + 차량 리스트 페이지
 * - 왼쪽 전체 필터 패널 고정 (제조사/할부/차종/연료)
 * - 오른쪽은 차량 카드 리스트 그리드 3열
 */

const CarList = () => {
  const { carType } = useParams(); // 'domestic' or 'imported'
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [minPrice, setMinPrice] = useState(Number(searchParams.get('min') || 60));
  const [maxPrice, setMaxPrice] = useState(Number(searchParams.get('max') || 240));
  const [sortBy, setSortBy] = useState('popular');
  const [searchQuery, setSearchQuery] = useState('');
  const [manufacturer, setManufacturer] = useState(searchParams.get('maker') || '전체');
  const [typeSelected, setTypeSelected] = useState(searchParams.get('type') || '전체');
  const [fuel, setFuel] = useState(searchParams.get('fuel') || '전체');

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: `${carType === 'domestic' ? '국산차' : '수입차'} 견적내기` }
  ];

  const tabs = [
    { label: '국산차', path: '/carlist/domestic' },
    { label: '수입차', path: '/carlist/imported' }
  ];

  // 카테고리(domestic/imported) 전환 시 필터/URL 완전 초기화
  useEffect(() => {
    setSearchQuery('');
    setManufacturer('전체');
    setTypeSelected('전체');
    setFuel('전체');
    setMinPrice(60);
    setMaxPrice(240);
    setSearchParams(new URLSearchParams(), { replace: true });
  }, [carType]);

  // 차량 데이터 (실제로는 API에서 가져와야 함)
  const domesticCars = [
    { id: 1, name: "더 뉴 팰리세이드", price: 45, priceText: "월 45만원~", img: "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=300&h=200&fit=crop", brand: "현대", desc: "대형 SUV\n최고급 사양" },
    { id: 2, name: "쏘렌토 하이브리드", price: 42, priceText: "월 42만원~", img: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=300&h=200&fit=crop", brand: "기아", desc: "중형 SUV\n하이브리드" },
    { id: 3, name: "투싼 하이브리드", price: 39, priceText: "월 39만원~", img: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=300&h=200&fit=crop", brand: "현대", desc: "소형 SUV\n하이브리드" },
    { id: 4, name: "GV80", price: 89, priceText: "월 89만원~", img: "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=300&h=200&fit=crop", brand: "제네시스", desc: "대형 SUV\n럭셔리 사양" },
    { id: 5, name: "K8", price: 44, priceText: "월 44만원~", img: "https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=300&h=200&fit=crop", brand: "기아", desc: "중형 세단\n프리미엄" },
    { id: 6, name: "그랜저 IG", price: 40, priceText: "월 40만원~", img: "https://images.unsplash.com/photo-1617531653520-bd466e19bc3e?w=300&h=200&fit=crop", brand: "현대", desc: "중형 세단\n고급 사양" },
  ];

  const importedCars = [
    { id: 7, name: "BMW X5", price: 95, priceText: "월 95만원~", img: "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=300&h=200&fit=crop", brand: "BMW", desc: "중형 SUV\n럭셔리 브랜드" },
    { id: 8, name: "Mercedes-Benz E-Class", price: 85, priceText: "월 85만원~", img: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=300&h=200&fit=crop", brand: "Mercedes-Benz", desc: "중형 세단\n프리미엄" },
    { id: 9, name: "Audi Q7", price: 92, priceText: "월 92만원~", img: "https://images.unsplash.com/photo-1606016159991-5de14d7a9ac0?w=300&h=200&fit=crop", brand: "Audi", desc: "대형 SUV\n쿠페 스타일" },
    { id: 10, name: "Lexus RX", price: 75, priceText: "월 75만원~", img: "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=300&h=200&fit=crop", brand: "Lexus", desc: "중형 SUV\n하이브리드" },
    { id: 11, name: "Volvo XC90", price: 80, priceText: "월 80만원~", img: "https://images.unsplash.com/photo-1617654112368-307921291f42?w=300&h=200&fit=crop", brand: "Volvo", desc: "대형 SUV\n안전 사양" },
    { id: 12, name: "Porsche Cayenne", price: 120, priceText: "월 120만원~", img: "https://images.unsplash.com/photo-1614200187524-dc4b892acf16?w=300&h=200&fit=crop", brand: "Porsche", desc: "대형 SUV\n스포츠카" },
  ];

  const allCars = carType === 'domestic' ? domesticCars : importedCars;

  // 정렬 및 검색 필터링
  const filteredAndSortedCars = React.useMemo(() => {
    let result = [...allCars];

    // 검색 필터
    if (searchQuery) {
      result = result.filter(car => 
        car.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // 정렬
    switch (sortBy) {
      case 'priceHigh':
        result.sort((a, b) => b.price - a.price);
        break;
      case 'priceLow':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'popular':
      default:
        // 인기순은 기본 순서 유지
        break;
    }

    return result;
  }, [searchQuery, sortBy]);

  const manufacturers = [
    { name: '전체', logo: null },
    { name: '현대', logo: '🚗' },
    { name: '기아', logo: '🚙' },
    { name: '제네시스', logo: '🚘' },
    { name: '쉐보레', logo: '🚐' },
    { name: 'KGM', logo: '🚕' },
    { name: '르노코리아', logo: '🚖' }
  ];
  
  const priceRanges = ['60만원', '120만원', '240만원'];
  
  // 듀얼 슬라이더 핸들러
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
  
  const carTypes = [
    '전체',
    '경·소형SUV',
    '중·대형SUV',
    'SUV·RV',
    '외제·수입',
    '대형·승합'
  ];
  
  const fuelTypes = [
    '전체',
    '가솔린',
    '디젤(경유)',
    'LPG',
    '하이브리드',
    '전기·수소'
  ];

  const handleCarClick = (carId) => {
    navigate(`/car-detail/${carId}`);
  };

  return (
    <div className="carlist-page">
      {/* 상단 배너 */}
      <div className="carlist-banner">
        <div className="carlist-banner-content">
          <div className="carlist-banner-text">
            <h2 className="carlist-banner-title">심사완료율 독보적 1위 원더굿라이프</h2>
            <p className="carlist-banner-subtitle">전 차종 비교견적! 최고의 조건으로!</p>
          </div>
          <img 
            src="https://images.unsplash.com/photo-1542362567-b07e54358753?w=200&h=120&fit=crop" 
            alt="banner car" 
            className="carlist-banner-img" 
          />
        </div>
      </div>

      {/* 본문 레이아웃 */}
      <div className="carlist-container">
        {/* Breadcrumb & Tab */}
        <div className="carlist-top-section">
          <Breadcrumb items={breadcrumbItems} />
          <TabNav tabs={tabs} />
        </div>

        {/* 메인 레이아웃 (필터 + 콘텐츠) */}
        <div className="carlist-main-layout">
          {/* 왼쪽 필터 전체 (컴포넌트화) */}
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
            onSelectManufacturer={(v)=>{ setManufacturer(v); syncParams({ maker: v }); }}
            selectedCarType={typeSelected}
            onSelectCarType={(v)=>{ setTypeSelected(v); syncParams({ type: v }); }}
            selectedFuel={fuel}
            onSelectFuel={(v)=>{ setFuel(v); syncParams({ fuel: v }); }}
          />

          {/* 오른쪽 콘텐츠 */}
          <main className="carlist-main">
            {/* 정렬 및 검색 바 */}
            <div className="carlist-toolbar">
              <div className="carlist-sort">
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  className="carlist-sort-select"
                >
                  <option value="popular">인기순</option>
                  <option value="priceHigh">가격높은순</option>
                  <option value="priceLow">가격낮은순</option>
                </select>
              </div>
              <div className="carlist-search-wrapper">
                <SearchBar 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="차량 모델, 제조사를 검색해보세요"
                  variant="long"
                />
              </div>
            </div>

            {/* 차량 카드 리스트 */}
            <div className="carlist-grid">
              {filteredAndSortedCars.map((car) => (
                <PromotionCard
                  key={car.id}
                  id={car.id}
                  name={car.name}
                  desc={car.desc}
                  img={car.img}
                  brand={car.brand}
                  onClick={handleCarClick}
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

export default CarList;

