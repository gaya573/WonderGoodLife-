import React from 'react';
import styles from './QuickConsultCard.module.css';

const QuickConsultCard = ({
  carName,
  trimName,
  trimPrice,
  selectedColor,
  selectedOptions = [],
  discountAmount = 0,
  showDiscount = false,
  onEstimateClick
}) => {
  // 기본 차량가격 계산
  const basePrice = trimPrice || 0;
  
  // 옵션 총 가격 계산
  const optionsTotal = selectedOptions.reduce((sum, option) => sum + (option.price || 0), 0);
  
  // 전체 합계 계산
  const totalPrice = basePrice + optionsTotal;
  
  // 최종 합계 계산 (할인 적용)
  const finalTotal = showDiscount ? totalPrice - discountAmount : totalPrice;

  return (
    <div className={styles['quick-consult-card']}>
      <div className={styles['estimate-topbar']}>
        <span className={styles['estimate-topbar-title']}>간편상담</span>
        <span className={styles['estimate-topbar-arrow']}>→</span>
      </div>

      <div className={styles['estimate-body']}>
        {/* 기본 차량가격 */}
        <div className={styles['estimate-block']}>
          <div className={styles['estimate-block-title']}>기본 차량가격</div>
          <div className={styles['estimate-row']}>
            <span className={styles['estimate-sub']}>{trimName}</span>
            <span className={styles['estimate-value']}>
              {Math.round(basePrice / 10000).toLocaleString()}만원
            </span>
          </div>
        </div>

        <div className={styles['estimate-divider']}></div>

        {/* 옵션가격 */}
        <div className={styles['estimate-block']}>
          <div className={styles['estimate-block-title']}>옵션가격</div>
          <div className={styles['estimate-options-scroll']}>
            {/* 외장색상 */}
            <div className={styles['option-row']}>
              <span>차량 외장색상 · {selectedColor}</span>
              <span className={styles['option-price']}>+ 0원</span>
            </div>
            
            {/* 선택된 옵션들 */}
            {selectedOptions.map((option, index) => (
              <div className={styles['option-row']} key={index}>
                <span>{option.name}</span>
                <span className={styles['option-price']}>
                  + {Math.round(option.price / 10000)}만원
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 할인 섹션 (조건부 렌더링) */}
        {showDiscount && discountAmount > 0 && (
          <>
            <div className={styles['estimate-divider']}></div>
            
            <div className={styles['estimate-block']}>
              <div className={styles['estimate-block-title']}>즉시할인가</div>
              <div className={styles['estimate-row']}>
                <span className={styles['estimate-sub']}>즉시 할인 혜택</span>
                <span className={styles['estimate-value']} style={{color: '#ff4444'}}>
                  -{Math.round(discountAmount / 10000).toLocaleString()}만원
                </span>
              </div>
            </div>
          </>
        )}

        <div className={styles['estimate-divider']}></div>

        {/* 최종 합계 */}
        <div className={styles['estimate-total']}>
          <span className={styles['estimate-total-title']}>
            {showDiscount ? '최종 합계' : '합계'}
          </span>
          <span className={styles['estimate-total-value']}>
            {Math.round(finalTotal / 10000).toLocaleString()}만원
          </span>
        </div>

        {/* 견적 확인 버튼 */}
        <button 
          className={styles['estimate-cta']} 
          onClick={onEstimateClick}
        >
          비대면 견적 확인
        </button>
      </div>
    </div>
  );
};

export default QuickConsultCard;
