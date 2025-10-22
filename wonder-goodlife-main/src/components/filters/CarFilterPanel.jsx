import React from 'react';
import '../../pages/Car/CarList.css';

const CarFilterPanel = ({
  manufacturers = [],
  carTypes = [],
  fuelTypes = [],
  minPrice,
  maxPrice,
  priceRanges = [],
  onMinPriceChange,
  onMaxPriceChange,
  selectedManufacturer = '전체',
  onSelectManufacturer,
  selectedCarType = '전체',
  onSelectCarType,
  selectedFuel = '전체',
  onSelectFuel,
}) => {
  return (
    <aside className="carlist-filter-panel">
      <div className="carlist-filter-section">
        <h3 className="carlist-filter-title">제조사</h3>
        <div className="carlist-manufacturer-grid">
          {manufacturers.map((manufacturer, i) => (
            <button 
              key={i} 
              className={`carlist-manufacturer-btn ${manufacturer.name === selectedManufacturer ? 'active' : ''}`}
              onClick={() => onSelectManufacturer && onSelectManufacturer(manufacturer.name)}
            >
              {manufacturer.logo && <span className="manufacturer-logo">{manufacturer.logo}</span>}
              <span className="manufacturer-name">{manufacturer.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="carlist-filter-section">
        <div className="carlist-filter-title-row">
          <h3 className="carlist-filter-title">월별 대여료</h3>
          <span className="carlist-filter-value">{minPrice}~{maxPrice}만원</span>
        </div>
        <div className="carlist-range-wrapper">
          <div className="carlist-dual-range">
            <input 
              type="range" 
              min="60" 
              max="240" 
              step="10"
              value={minPrice}
              onChange={onMinPriceChange}
              className="carlist-range-input carlist-range-min" 
            />
            <input 
              type="range" 
              min="60" 
              max="240" 
              step="10"
              value={maxPrice}
              onChange={onMaxPriceChange}
              className="carlist-range-input carlist-range-max" 
            />
          </div>
          <div className="carlist-range-labels">
            {priceRanges.map((price, i) => (
              <span key={i}>{price}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="carlist-filter-section">
        <h3 className="carlist-filter-title">차량종류</h3>
        <div className="carlist-filter-grid-2">
          {carTypes.map((type, i) => (
            <button 
              key={i} 
              className={`carlist-filter-btn ${type === selectedCarType ? 'active' : ''}`}
              onClick={() => onSelectCarType && onSelectCarType(type)}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="carlist-filter-section">
        <h3 className="carlist-filter-title">연료</h3>
        <div className="carlist-filter-grid-2">
          {fuelTypes.map((fuel, i) => (
            <button 
              key={i} 
              className={`carlist-filter-btn ${fuel === selectedFuel ? 'active' : ''}`}
              onClick={() => onSelectFuel && onSelectFuel(fuel)}
            >
              {fuel}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default CarFilterPanel;


