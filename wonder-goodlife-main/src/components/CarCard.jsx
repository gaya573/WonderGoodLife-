import React from "react";
import styles from "./CarCard.module.css";

const CarCard = ({ rank, name, brand, year, mileage, description, image }) => {
    return (
      <div className={styles['car-card-wrapper']}>
        {/* 차량 이미지 */}
        <div className={styles['car-card-image']}>
          <img src={image} alt={name} />
        </div>
        
        {/* 정보 영역 */}
        <div className={styles['car-card-content']}>
          {/* 순위 */}
          <div className={`${styles['car-card-rank']} ${rank <= 3 ? styles['top-three'] : styles['normal-rank']}`}>{rank}</div>
          
          {/* 차량 정보 */}
          <div className={styles['car-card-info']}>
            <div className={styles['car-card-name']}>
              {name} <span className={styles['car-card-brand']}>{brand}</span>
            </div>
            <div className={styles['car-card-meta']}>
              {year} | {mileage}
            </div>
          </div>
          
          {/* 설명 */}
          <div className={styles['car-card-description']}>
            {description}
          </div>
        </div>
      </div>
  );
};

export default CarCard;