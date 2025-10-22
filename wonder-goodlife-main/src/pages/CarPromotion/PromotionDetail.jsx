import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Breadcrumb from '../../components/Breadcrumb';
import EstimateModal from '../../components/modals/EstimateModal';
import { findCardById } from './data';
import './PromotionDetail.css';

const PromotionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [selectedColor, setSelectedColor] = useState(0);
  const [selectedTrimIndex, setSelectedTrimIndex] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState({
    sunroof: false,
    adas: false,
    leather: false,
    premium: false
  });
  
  // 계약 조건
  const [contractMethod, setContractMethod] = useState('장기렌탈');
  const [contractPeriod, setContractPeriod] = useState('24개월');
  const [deposit, setDeposit] = useState('없음');
  const [prepayment, setPrepayment] = useState('없음');
  const [mileage, setMileage] = useState('10,000km');
  const [carTax, setCarTax] = useState('포함');
  const [insuranceAge, setInsuranceAge] = useState('만 21세(이상)');
  const [isEstimateOpen, setIsEstimateOpen] = useState(false);
  
  const card = findCardById(id);
  
  // 디테일 페이지 진입/차량 변경 시 스크롤을 맨 위로 고정
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
      // 일부 환경에서 즉시 반영 안 되는 경우 보완
      setTimeout(() => window.scrollTo(0, 0), 0);
    }
  }, [id]);

  // 세부모델(트림) 변경 시 옵션 선택 상태 초기화
  useEffect(() => {
    const reset = cardData.options.reduce((acc, opt) => {
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

  // 카드 데이터 (프로모션용으로 수정)
  const cardData = {
    name: card?.name || '프로모션 카드',
    brand: card?.brand || '브랜드',
    colors: [
      { name: '클래식 블랙', code: '#1A1A1A' },
      { name: '프리미엄 골드', code: '#FFD700' },
      { name: '엘레강트 실버', code: '#C0C0C0' },
      { name: '모던 화이트', code: '#FFFFFF' },
      { name: '럭셔리 블루', code: '#4169E1' },
    ],
    trimGroups: [
      {
        title: '프로모션 카드 2026년형 신규 발급 혜택',
        items: [
          { name: '기본 카드', price: 0 },
          { name: '프리미엄 카드', price: 50000 },
          { name: '골드 카드', price: 100000 },
          { name: '플래티넘 카드', price: 200000 },
          { name: '다이아몬드 카드', price: 500000 },
        ],
      },
      {
        title: '프로모션 카드 2026년형 연회비 혜택',
        items: [
          { name: '연회비 면제', price: 0 },
          { name: '연회비 50% 할인', price: 25000 },
          { name: '연회비 30% 할인', price: 35000 },
          { name: '연회비 정상', price: 50000 },
        ],
      },
    ],
    options: [
      { id: 'sunroof', name: '추가 혜택 패키지', price: 0 },
      { id: 'adas', name: '포인트 적립 혜택', price: 0 },
      { id: 'leather', name: '캐시백 혜택', price: 0 },
      { id: 'premium', name: '프리미엄 서비스', price: 0 },
    ],
    features: [
      '무이자 할부',
      '포인트 적립',
      '캐시백',
      '연회비 혜택',
      '추가 혜택',
      '프리미엄 서비스',
    ]
  };

  const allTrims = cardData.trimGroups.flatMap(g => g.items);
  const currentTrim = allTrims[selectedTrimIndex] || allTrims[0];
  
  // 그룹 펼침 상태
  const [expandedTrimGroups, setExpandedTrimGroups] = useState(
    cardData.trimGroups.map(() => false)
  );
  const toggleTrimGroup = (idx) => {
    setExpandedTrimGroups(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '카드 프로모션', link: '/card-promotion' },
    { label: '카드 브랜드별 혜택 전체', link: '/card-promotion/brands' },
    { label: cardData.name }
  ];

  const calculateTotal = () => {
    let total = currentTrim.price;
    Object.keys(selectedOptions).forEach(key => {
      if (selectedOptions[key]) {
        const option = cardData.options.find(opt => opt.id === key);
        if (option) total += option.price;
      }
    });
    return total;
  };

  const handleOptionToggle = (optionId) => {
    setSelectedOptions(prev => ({
      ...prev,
      [optionId]: !prev[optionId]
    }));
  };

  if (!card) {
    return (
      <div className="car-detail-page">
        <div className="car-detail-container">
          <Breadcrumb items={breadcrumbItems} />
          <p>해당 프로모션을 찾을 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="car-detail-page">
      <div className="car-detail-container">
        <Breadcrumb items={breadcrumbItems} />
        
        {/* 상단 프로모션 배너 (빨간색 박스 1) */}
        <div className="promotion-banner">
          <div className="promotion-banner-content">
            <div className="promotion-banner-text">
              <h2>{card.name} 프로모션</h2>
              <p>{card.desc}</p>
            </div>
            <div className="promotion-banner-image">
              <div className="gray-box"></div>
            </div>
          </div>
        </div>
        
        <div className="car-detail-layout">
          {/* 왼쪽: 차량 이미지 + 옵션들 */}
          <div className="car-detail-left">
            {/* 차량 이미지 + 오버레이 정보 */}
            <div className="car-hero-section">
              <div className="gray-box car-hero-image"></div>
              
              {/* 우측 상단 정보 오버레이 */}
              <div className="car-info-badge">
                <div>
                <div className="brand-logo-square"> </div>
                <h1 className="car-hero-title">{cardData.name}</h1>
                </div>
                <div className="color-info-section">
                  <div className="color-header">
                    
                    <span className="color-label-text">카드 디자인 선택</span>
                    <span className="selected-color-text">{cardData.colors[selectedColor].name}</span>
                  </div>
                  <div className="color-palette">
                    {cardData.colors.map((color, idx) => (
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

            {/* 세부모델 선택 */}
            <div className="option-card">
              <div className="option-card-header" >
                <h3 className="option-card-title">세부모델 선택</h3>
                    
              </div>
              {expandedSections.trim && (
                <div className="option-card-content">
                  <div className="trim-selector">
                    {cardData.trimGroups.map((group, gidx) => (
                      <div key={gidx} className="trim-group">
                        <div className="trim-group-header" onClick={() => toggleTrimGroup(gidx)}>
                          <span className="trim-group-title">{group.title}</span>
                          <button className="group-toggle">{expandedTrimGroups[gidx] ? '−' : '+'}</button>
                        </div>
                        {expandedTrimGroups[gidx] && (
                          <div className="trim-list">
                            {group.items.map((item, idx) => {
                              const baseIndex = cardData.trimGroups
                                .slice(0, gidx)
                                .reduce((sum, g) => sum + g.items.length, 0);
                              const globalIndex = baseIndex + idx;
                              const active = selectedTrimIndex === globalIndex;
                              return (
                                <div
                                  key={globalIndex}
                                  className={`trim-option ${active ? 'active' : ''}`}
                                  tabIndex={0}
                                  onClick={() => setSelectedTrimIndex(globalIndex)}
                                >
                                  <div className="trim-radio">{active && <span className="trim-check">✓</span>}</div>
                                  <div className="trim-name">{item.name}</div>
                                  <div className="trim-price">{item.price.toLocaleString()}원</div>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 옵션 선택 */}
            <div className="option-card">
              <div className="option-card-header" onClick={() => toggleSection('options')}>
                <h3 className="option-card-title">옵션 선택</h3>
                <button className="toggle-btn">
                  {expandedSections.options ? '−' : '+'}
                </button>
              </div>
              {expandedSections.options && (
                <div className="option-card-content">
                  <div className="additional-options">
                    {cardData.options.map((option) => (
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

            {/* 이벤트 섹션을 왼쪽 그리드 내부로 이동 */}
            <div className="event-section">
              <h3 className="event-section-title">이벤트 및 프로모션 (선택)</h3>
              <div className="event-content">
         
              </div>
            </div>

          </div>

          {/* 오른쪽: 간편상담 스타일의 견적 카드 */}
          <div className="car-detail-right">
            <div className="estimate-card">
              <div className="estimate-topbar">
                <span className="estimate-topbar-title">간편상담</span>
                <span className="estimate-topbar-arrow">→</span>
              </div>

              <div className="estimate-body">
                <div className="estimate-block">
                  <div className="estimate-block-title">기본 카드가격</div>
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
                      <span>카드 디자인 · {cardData.colors[selectedColor].name}</span>
                      <span className="option-price">+ 0원</span>
                    </div>
                    {cardData.options.map(opt => (
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

                <button className="estimate-cta" onClick={() => setIsEstimateOpen(true)}>비대면 견적 확인</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <EstimateModal
        open={isEstimateOpen}
        onClose={() => setIsEstimateOpen(false)}
        carName={cardData.name}
        trimName={currentTrim?.name}
      />
    </div>
  );
};

export default PromotionDetail;


