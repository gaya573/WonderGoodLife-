import React from 'react';
import styles from './SearchBar.module.css';

/**
 * 공통 검색창 컴포넌트
 * Header와 CarList에서 동일하게 사용
 * variant: "long" (639px × 56px) | "small" (기본 크기)
 */
const SearchBar = ({ 
  value, 
  onChange, 
  placeholder = "검색어를 입력해 주세요",
  className = "",
  variant = "small" // "long" | "small"
}) => {
  return (
    <div className={`${styles['search-bar']} ${styles[variant]} ${className}`}>
      <input 
        type="text" 
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={styles['search-bar-input']}
      />
      <button className={styles['search-bar-btn']} aria-label="검색">
        <svg
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          viewBox="0 0 24 24"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
    </div>
  );
};

export default SearchBar;

