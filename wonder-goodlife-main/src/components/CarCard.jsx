import React from "react";
import "./CarCard.css";

const CarCard = ({ rank, name, brand, year, mileage, description, image }) => {
    return (
      <div className="car-card-wrapper">
        {/* 차량 이미지 */}
        <div className="car-card-image">
          <img src={image} alt={name} />
        </div>
        
        {/* 정보 영역 */}
        <div className="car-card-content">
          {/* 순위 */}
          <div className="car-card-rank">{rank}</div>
          
          {/* 차량 정보 */}
          <div className="car-card-info">
            <div className="car-card-name">
              {name} <span className="car-card-brand">{brand}</span>
            </div>
            <div className="car-card-meta">
              {year} | {mileage}
            </div>
          </div>
          
          {/* 설명 */}
          <div className="car-card-description">
            {description}
          </div>
        </div>
      </div>
  );
};

export default CarCard;