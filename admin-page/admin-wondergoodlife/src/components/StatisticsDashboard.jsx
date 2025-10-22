import React from 'react';
import PropTypes from 'prop-types';
import { useStatistics } from '../hooks/useStatistics';
import StatisticsGrid from './StatisticsGrid';

/**
 * 통계 대시보드 컴포넌트
 * 브랜드, 모델, 트림 등의 통계 정보를 표시
 */
const StatisticsDashboard = ({ selectedVersion, versionData, totalPages, currentPage, searchStats }) => {
  const { statistics, loading } = useStatistics(selectedVersion, versionData, totalPages, searchStats);

  return (
    <StatisticsGrid 
      statistics={statistics}
      loading={loading}
      currentPage={currentPage}
      totalPages={totalPages}
    />
  );
};

StatisticsDashboard.propTypes = {
  selectedVersion: PropTypes.shape({
    id: PropTypes.number.isRequired,
    version_name: PropTypes.string,
    description: PropTypes.string,
  }),
  versionData: PropTypes.object,
  totalPages: PropTypes.number,
  currentPage: PropTypes.number,
  searchStats: PropTypes.object,
};

StatisticsDashboard.defaultProps = {
  selectedVersion: null,
  totalPages: 0,
  currentPage: 1,
  searchStats: null,
};

export default StatisticsDashboard;
