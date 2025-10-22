/**
 * 통계 그리드 레이아웃 컴포넌트
 * 통계 카드들을 그리드 형태로 배치
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import StatCard from './ui/StatCard';
import './StatisticsGrid.css';

const StatisticsGrid = React.memo(({ 
  statistics, 
  loading, 
  currentPage, 
  totalPages 
}) => {
  // 통계 데이터가 없을 때만 로딩 표시, 한번 로드된 후에는 깜빡이지 않음
  const isInitialLoading = loading && statistics.total === 0;
  
  const statItems = useMemo(() => [
    {
      key: 'brands',
      value: statistics.brands,
      label: '브랜드',
      color: 'neutral',
      loading: isInitialLoading
    },
    {
      key: 'models',
      value: statistics.models,
      label: '모델',
      color: 'neutral',
      loading: isInitialLoading
    },
    {
      key: 'trims',
      value: statistics.trims,
      label: '트림',
      color: 'neutral',
      loading: isInitialLoading
    },
    {
      key: 'options',
      value: statistics.options,
      label: '옵션',
      color: 'neutral',
      loading: isInitialLoading
    },
    {
      key: 'total',
      value: statistics.total,
      label: '전체 데이터 수',
      color: 'neutral',
      loading: isInitialLoading
    },
    {
      key: 'pages',
      value: `${currentPage}/${totalPages}`,
      label: '페이지',
      color: 'primary',
      loading: false // 페이지는 항상 로딩하지 않음
    }
  ], [statistics, currentPage, totalPages, isInitialLoading]);

  return (
    <div className="statistics-grid">
      {statItems.map((item) => (
        <StatCard
          key={item.key}
          value={item.value}
          label={item.label}
          loading={item.loading}
          color={item.color}
        />
      ))}
    </div>
  );
});

StatisticsGrid.displayName = 'StatisticsGrid';

StatisticsGrid.propTypes = {
  statistics: PropTypes.shape({
    brands: PropTypes.number,
    models: PropTypes.number,
    trims: PropTypes.number,
    options: PropTypes.number,
    total: PropTypes.number,
    totalPages: PropTypes.number,
  }).isRequired,
  loading: PropTypes.bool,
  currentPage: PropTypes.number,
  totalPages: PropTypes.number,
};

StatisticsGrid.defaultProps = {
  loading: false,
  currentPage: 1,
  totalPages: 0,
};

export default StatisticsGrid;
