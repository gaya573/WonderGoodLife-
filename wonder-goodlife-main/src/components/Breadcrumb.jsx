import React from 'react';
import { Link } from 'react-router-dom';
import './Breadcrumb.css';

/**
 * Breadcrumb 네비게이션 컴포넌트
 * 현재 페이지 위치를 표시
 */
const Breadcrumb = ({ items }) => {
  return (
    <nav className="breadcrumb">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {item.link ? (
            <Link to={item.link} className="breadcrumb-item">
              {item.label}
            </Link>
          ) : (
            <span className="breadcrumb-item active">{item.label}</span>
          )}
          {index < items.length - 1 && (
            <span className="breadcrumb-separator">›</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumb;

