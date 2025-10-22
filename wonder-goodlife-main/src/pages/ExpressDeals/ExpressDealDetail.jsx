import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import EstimateModal from '../../components/modals/EstimateModal';
import './ExpressDealDetail.css';

const ExpressDealDetail = () => {
  const { carId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [selectedColor, setSelectedColor] = useState(Number(searchParams.get('color') || 0));
  const [selectedTrimIndex, setSelectedTrimIndex] = useState(Number(searchParams.get('trim') || 0));
  const [selectedOptions, setSelectedOptions] = useState({
    sunroof: false,
    adas: false,
    leather: false,
    premium: false
  });
  
  // 계약 조건
  const [contractMethod, setContractMethod] = useState('장기렌탈');
  const [contractPeriod, setContractPeriod] = useState(searchParams.get('term') || '24개월');
  const [deposit, setDeposit] = useState(searchParams.get('deposit') || '없음');
  const [prepayment, setPrepayment] = useState(searchParams.get('prepay') || '없음');
  const [mileage, setMileage] = useState(searchParams.get('mileage') || '10,000km');
  const [carTax, setCarTax] = useState(searchParams.get('tax') || '포함');
  const [insuranceAge, setInsuranceAge] = useState(searchParams.get('insure') || '만 21세(이상)');
  const [isEstimateOpen, setIsEstimateOpen] = useState(false);
  
  // 디테일 페이지 진입/차량 변경 시 스크롤을 맨 위로 고정
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
      // 일부 환경에서 즉시 반영 안 되는 경우 보완
      setTimeout(() => window.scrollTo(0, 0), 0);
    }
  }, [carId]);

  // URL 쿼리 동기화
  useEffect(() => {
    const params = new URLSearchParams(searchParams);
    params.set('trim', String(selectedTrimIndex));
    params.set('color', String(selectedColor));
    params.set('term', String(contractPeriod));
    params.set('deposit', String(deposit));
    params.set('prepay', String(prepayment));
    params.set('mileage', String(mileage));
    params.set('tax', String(carTax));
    params.set('insure', String(insuranceAge));
    setSearchParams(params, { replace: true });
  }, [selectedTrimIndex, selectedColor, contractPeriod, deposit, prepayment, mileage, carTax, insuranceAge]);

  // 세부모델(트림) 변경 시 옵션 선택 상태 초기화
  useEffect(() => {
    const reset = carData.options.reduce((acc, opt) => {
      acc[opt.id] = false;
      return acc;
    }, {});
    setSelectedOptions(reset);
  }, [selectedTrimIndex]);
  
  // 접기/펼치기 상태 (초기값: 모두 펼쳐짐)
  const [expandedSections, setExpandedSections] = useState({
    trim: true,
    options: true,
    contract: true
  });
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // 차량 데이터 (임시)
  const carData = {
    name: '더 뉴 아반떼',
    brand: '현대',
    colors: [
      { name: '크리미 화이트 펄', code: '#F5F5F5' },
      { name: '어비스 블랙 펄', code: '#1A1A1A' },
      { name: '문라이트 블루 펄', code: '#4A90E2' },
      { name: '엔진 레드', code: '#D32F2F' },
      { name: '쉬머링 실버', code: '#9E9E9E' },
    ],
    trimGroups: [
      {
        title: '아반떼 2026년형 가솔린 1.6 하이브리드 개별소비세 인하',
        items: [
          { name: '스마트 (A/T)', price: 26180000 },
          { name: '모던 라이트 (A/T)', price: 26440000 },
          { name: '모던 라이트 (A/T)', price: 26440000 },
          { name: '인스퍼레이션 (A/T)', price: 32150000 },
          { name: 'N라인 (A/T)', price: 32840000 },
        ],
      },
      {
        title: '아반떼 2026년형 가솔린 1.6 개별소비세 인하',
        items: [
          { name: '스마트 (A/T)', price: 20340000 },
          { name: '모던 (A/T)', price: 23550000 },
          { name: '인스퍼레이션 (A/T)', price: 27710000 },
          { name: 'N라인 (A/T)', price: 28080000 },
        ],
      },
      {
        title: '아반떼 2026년형 LPG 1.6 (일반판매용) 개별소비세 인하',
        items: [
          { name: '스마트 (A/T)', price: 21720000 },
          { name: '모던 (A/T)', price: 24920000 },
          { name: '인스퍼레이션 (A/T)', price: 28420000 },
        ],
      },
    ],
    options: [
      { id: 'sunroof', name: '선루프 (파노라마)', price: 700000 },
      { id: 'adas', name: '고급 안전 (ADAS)', price: 200000 },
      { id: 'leather', name: '가죽 시트', price: 380000 },
      { id: 'premium', name: '프리미엄 패키지', price: 250000 },
    ],
    features: [
      '스마트키',
      '후방 카메라',
      '전방 충돌 경고',
      '차선 이탈 경고',
      '크루즈 컨트롤',
      '블루투스',
    ]
  };

  const allTrims = carData.trimGroups.flatMap(g => g.items);
  const currentTrim = allTrims[selectedTrimIndex] || allTrims[0];
  
  // 그룹 펼침 상태
  const [expandedTrimGroups, setExpandedTrimGroups] = useState(
    carData.trimGroups.map(() => false)
  );
  const toggleTrimGroup = (idx) => {
    setExpandedTrimGroups(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '즉시출고 특가', link: '/express-deals' },
    { label: carData.name }
  ];

  const calculateTotal = () => {
    let total = currentTrim.price;
    Object.keys(selectedOptions).forEach(key => {
      if (selectedOptions[key]) {
        const option = carData.options.find(opt => opt.id === key);
        if (option) total += option.price;
      }
    });
    return total;
  };

  const estimateMonthly = () => {
    // 아주 단순화된 월 납입액 샘플 계산(시각 비교용)
    const base = calculateTotal();
    const depRate = deposit === '없음' ? 0 : Number(deposit.replace('%',''))/100;
    const preRate = prepayment === '없음' ? 0 : Number(prepayment.replace('%',''))/100;
    const termNum = Number(contractPeriod.replace('개월','')) || 24;
    const financed = base * (1 - depRate - preRate);
    return Math.max(1, Math.round((financed / termNum) / 10000)); // 만원 단위
  };

  const renderPaymentDetails = () => (
    <div className="estimate-body">
      <div className="estimate-block">
        <div className="estimate-block-title">기본 차량가격</div>
        <div className="estimate-row">
          <span className="estimate-sub">{currentTrim.name}</span>
          <span className="estimate-value">{Math.round(currentTrim.price / 10000).toLocaleString()}만원</span>
        </div>
      </div>

      <div className="estimate-divider"></div>

      <div className="estimate-block">
        <div className="estimate-block-title">옵션가격</div>
        <div className="estimate-options-scroll">
          <div className="option-row">
            <span>차량 외장색상 · {carData.colors[selectedColor].name}</span>
            <span className="option-price">+ 0원</span>
          </div>
          {carData.options.map(opt => (
            selectedOptions[opt.id] ? (
              <div className="option-row" key={opt.id}>
                <span>{opt.name}</span>
                <span className="option-price">+ {Math.round(opt.price / 10000)}만원</span>
              </div>
            ) : null
          ))}
        </div>
      </div>

      <div className="estimate-divider"></div>

      <div className="estimate-total">
        <span className="estimate-total-title">합계</span>
        <span className="estimate-total-value">{Math.round(calculateTotal() / 10000).toLocaleString()}만원</span>
      </div>
    </div>
  );

  const handleOptionToggle = (optionId) => {
    setSelectedOptions(prev => ({
      ...prev,
      [optionId]: !prev[optionId]
    }));
  };

  return (
    <div className="deal-detail-page">
      <div className="deal-detail-container">
        <Breadcrumb items={breadcrumbItems} />
        
        <div >
          {/* 왼쪽: 메인 (8컬럼) */}
          <div className="deal-main">
            {/* 차량 이미지 + 오버레이 정보 */}
            <div className="deal-hero car-hero-section">
              <img 
                src="https://images.unsplash.com/photo-1542362567-b07e54358753?w=1200&h=700&fit=crop" 
                alt={carData.name}
                className="car-hero-image"
              />
              
              {/* 우측 상단 정보 오버레이 */}
              <div className="car-info-badge">
                <div>
                <div className="brand-logo-square"> </div>
                <h1 className="car-hero-title">{carData.name}</h1>
                </div>
                <div className="color-info-section">
                  <div className="color-header">
                    
                    <span className="color-label-text">외장색상 선택</span>
                    <span className="selected-color-text">{carData.colors[selectedColor].name}</span>
                  </div>
                  <div className="color-palette">
                    {carData.colors.map((color, idx) => (
                      <button
                        key={idx}
                        className={`color-swatch ${selectedColor === idx ? 'selected' : ''}`}
                        style={{ backgroundColor: color.code }}
                        onClick={() => setSelectedColor(idx)}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>
              </div>  
            </div>

            {/* 견적 비교 섹션 - 히어로 바로 아래 */}
            <section className="compare-section">
              <div className="estimate-card compare-left">
                <div className="estimate-topbar">
                  <span className="estimate-topbar-title">원더굿라이프 즉시출고가</span>
              
                </div>
                {renderPaymentDetails()}
                <button className="estimate-cta" onClick={() => setIsEstimateOpen(true)}>비대면 상담 신청</button>
              </div>
              <div className="compare-vs">VS</div>
              <div className="estimate-card compare-right">
                <div className="estimate-topbar" style={{background:'#f1f3f5', color:'#333'}}>
                  <span className="estimate-topbar-title">일반 할부 견적가</span>
             
                </div>
                {renderPaymentDetails()}
                <button className="estimate-cta" onClick={() => setIsEstimateOpen(true)}>상담으로 혜택 비교</button>
              </div>
            </section>

            {/* 세부모델 제거 → 옵션/계약조건만 두 칼럼 */}
            <div className="config-row">
            {/* 옵션 선택 */}
            <div className="deal-card option-card">
              <div className="option-card-header" onClick={() => toggleSection('options')}>
                <h3 className="option-card-title">옵션 선택</h3>
                <button className="toggle-btn">
                  {expandedSections.options ? '−' : '+'}
                </button>
              </div>
              {expandedSections.options && (
                <div className="option-card-content">
                  <div className="additional-options">
                    {carData.options.map((option) => (
                      <div
                        key={option.id}
                        className={`additional-option ${selectedOptions[option.id] ? 'active' : ''}`}
                        onClick={() => handleOptionToggle(option.id)}
                      >
                        <div className="option-checkbox">
                          {selectedOptions[option.id] && <span>✓</span>}
                        </div>
                        <div className="option-details">
                          <span className="option-name">{option.name}</span>
                          <span className="option-price">+{option.price.toLocaleString()}원</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 계약 조건 선택 */}
            <div className="deal-card option-card contract-conditions">
              <div className="option-card-header" onClick={() => toggleSection('contract')}>
                <h3 className="option-card-title">계약 조건 선택</h3>
                <button className="toggle-btn">
                  {expandedSections.contract ? '−' : '+'}
                </button>
              </div>
              
              {expandedSections.contract && (
                <div className="option-card-content">
                  {/* 이용방법 */}
                  <div className="contract-row">
                <label className="contract-label">이용방법</label>
                <div className="contract-options">
                  <button 
                    className={`contract-btn ${contractMethod === '장기렌탈' ? 'active' : ''}`}
                    onClick={() => setContractMethod('장기렌탈')}
                  >
                    장기렌탈
                  </button>
                  <button 
                    className={`contract-btn ${contractMethod === '리스' ? 'active' : ''}`}
                    onClick={() => setContractMethod('리스')}
                  >
                    리스
                  </button>
                </div>
              </div>

              {/* 이용기간 */}
              <div className="contract-row">
                <label className="contract-label">이용기간</label>
                <div className="contract-options-grid">
                  {['24개월', '36개월', '48개월', '72개월'].map((period) => (
                    <button
                      key={period}
                      className={`contract-btn ${contractPeriod === period ? 'active' : ''}`}
                      onClick={() => setContractPeriod(period)}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              {/* 보증금 */}
              <div className="contract-row">
                <label className="contract-label">보증금</label>
                <div className="contract-options-grid">
                  {['없음', '10%', '20%', '30%', '40%'].map((dep) => (
                    <button
                      key={dep}
                      className={`contract-btn ${deposit === dep ? 'active' : ''}`}
                      onClick={() => setDeposit(dep)}
                    >
                      {dep}
                    </button>
                  ))}
                </div>
              </div>

              {/* 선납금 */}
              <div className="contract-row">
                <label className="contract-label">선납금</label>
                <div className="contract-options-grid">
                  {['없음', '10%', '20%', '30%', '40%'].map((pre) => (
                    <button
                      key={pre}
                      className={`contract-btn ${prepayment === pre ? 'active' : ''}`}
                      onClick={() => setPrepayment(pre)}
                    >
                      {pre}
                    </button>
                  ))}
                </div>
              </div>

              {/* 연간 약정운행거리 */}
              <div className="contract-row">
                <label className="contract-label">연간 약정운행거리</label>
                <div className="contract-options-grid">
                  {['10,000km', '20,000km', '30,000km', '40,000km', '50,000km'].map((mile) => (
                    <button
                      key={mile}
                      className={`contract-btn ${mileage === mile ? 'active' : ''}`}
                      onClick={() => setMileage(mile)}
                    >
                      {mile}
                    </button>
                  ))}
                </div>
              </div>

              {/* 자동차세 */}
              <div className="contract-row">
                <label className="contract-label">자동차세</label>
                <div className="contract-options">
                  <button 
                    className={`contract-btn ${carTax === '포함' ? 'active' : ''}`}
                    onClick={() => setCarTax('포함')}
                  >
                    포함
                  </button>
                  <button 
                    className={`contract-btn ${carTax === '미포함' ? 'active' : ''}`}
                    onClick={() => setCarTax('미포함')}
                  >
                    미포함
                  </button>
                </div>
              </div>

              {/* 보험 면제 */}
              <div className="contract-row">
                <label className="contract-label">보험 면제</label>
                <div className="contract-options">
                  <button 
                    className={`contract-btn ${insuranceAge === '만 21세(이상)' ? 'active' : ''}`}
                    onClick={() => setInsuranceAge('만 21세(이상)')}
                  >
                    만 21세(이상)
                  </button>
                  <button 
                    className={`contract-btn ${insuranceAge === '만 26세(이상)' ? 'active' : ''}`}
                    onClick={() => setInsuranceAge('만 26세(이상)')}
                  >
                    만 26세(이상)
                  </button>
                </div>
              </div>
                </div>
              )}
            </div>
            </div>{/* /.config-row */}
          </div>

          {/* 우측 간편상담 패널 제거: 비교형 레이아웃으로 통합 */}
        </div>
      </div>


      {/* 오늘 마감 출고 섹션 */}
      <section className="today-release">
        <h3 className="today-title">🔔 오늘 마감 출고</h3>
        <div className="today-grid">
          {[1,2,3,4].map((n) => (
            <div key={n} className="today-card">
              <img src="https://images.unsplash.com/photo-1542362567-b07e54358753?w=480&h=280&fit=crop" alt="deal" />
              <div className="today-info">
                <strong>{carData.name}</strong>
                <span>월 {estimateMonthly()}만원~</span>
              </div>
              <button className="today-cta" onClick={() => setIsEstimateOpen(true)}>빠른 견적</button>
            </div>
          ))}
        </div>
      </section>
      <EstimateModal
        open={isEstimateOpen}
        onClose={() => setIsEstimateOpen(false)}
        carName={carData.name}
        trimName={currentTrim?.name}
      />
    </div>
  );
};

export default ExpressDealDetail;

