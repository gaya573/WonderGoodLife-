/**
 * 통계 카드 컴포넌트
 * 숫자와 레이블을 표시하는 재사용 가능한 카드
 */

import React from 'react';
import PropTypes from 'prop-types';
import Card from './Card';
import './StatCard.css';

const StatCard = React.memo(({ 
  value, 
  label, 
  loading = false, 
  color = 'neutral',
  size = 'lg' 
}) => {
  const getValueClasses = () => {
    const classes = ['stat-value', `stat-value-${size}`, `stat-value-${color}`];
    return classes.join(' ');
  };

  // 로딩 중일 때는 안정적인 플레이스홀더 표시
  const displayValue = loading ? '0' : value;

  return (
    <Card padding="lg">
      <div className="stat-card">
        <div className={getValueClasses()}>
          {displayValue}
        </div>
        <div className="stat-label">
          {label}
        </div>
      </div>
    </Card>
  );
});

StatCard.displayName = 'StatCard';

StatCard.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
  color: PropTypes.oneOf(['neutral', 'primary', 'success', 'warning', 'error']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
};

StatCard.defaultProps = {
  loading: false,
  color: 'neutral',
  size: 'lg',
};

export default StatCard;
