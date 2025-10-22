/**
 * 통계 데이터 관리를 위한 커스텀 훅
 * 통계 조회 로직을 분리하여 재사용성 향상
 */

import { useState, useEffect, useCallback } from 'react';
import versionAPI from '../services/versionApi';
import { batchApi } from '../services/api';

export const useStatistics = (selectedVersion, versionData, totalPages, searchStats = null) => {
  const [statistics, setStatistics] = useState({
    brands: 0,
    models: 0,
    trims: 0,
    options: 0,
    total: 0,
    totalPages: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 전체 통계 데이터 가져오기 함수를 메모이제이션
  const fetchTotalStatistics = useCallback(async () => {
    if (!selectedVersion?.id) {
      setStatistics({
        brands: 0,
        models: 0,
        trims: 0,
        options: 0,
        total: 0,
        totalPages: 0
      });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. 현재 버전의 각 테이블별 개수 가져오기
      console.log('🔍 현재 버전 통계 API 호출 시작...');
      let totalBrandsCount = 0;
      let totalModelsCount = 0;
      let totalTrimsCount = 0;
      let totalOptionsCount = 0;
      
      try {
        // 현재 버전의 summary API를 사용해서 개수 가져오기
        // console.log('📊 현재 버전 통계 조회 시작...');
        const summaryResponse = await batchApi.get(`/staging/summary?version_id=${selectedVersion.id}`);
   
        if (summaryResponse?.data?.summary) {
          totalBrandsCount = summaryResponse.data.summary.brand_count || 0;
          totalModelsCount = summaryResponse.data.summary.models || 0;
          totalTrimsCount = summaryResponse.data.summary.trims || 0;
          totalOptionsCount = summaryResponse.data.summary.options || 0;
          
     
        } else {
          console.error('❌ API 응답에서 summary 데이터를 찾을 수 없습니다');
          console.error('❌ 전체 응답:', summaryResponse);
          console.error('❌ 응답 데이터:', summaryResponse?.data);
          totalBrandsCount = 0;
          totalModelsCount = 0;
          totalTrimsCount = 0;
          totalOptionsCount = 0;
        }
        
      } catch (error) {
        console.error('❌ 현재 버전 통계 조회 실패:', error);
        console.error('❌ 에러 메시지:', error.message);
        console.error('❌ 에러 응답:', error.response);
        totalBrandsCount = 0;
        totalModelsCount = 0;
        totalTrimsCount = 0;
        totalOptionsCount = 0;
      }
      
      // 2. 현재 버전의 데이터 통계 계산
      // console.log('🔍 현재 버전 데이터 계산 시작...');
      let brands = [];
      if (versionData?.brands) {
        brands = versionData.brands;
        // console.log('📊 versionData에서 브랜드 사용:', brands.length);
      } else {
        // console.log('🔍 API에서 브랜드 데이터 가져오기...');
        const data = await versionAPI.getBrandsWithFullData(selectedVersion.id, { page: 1, limit: 1 });
        brands = data?.data?.brands || [];
        // console.log('📊 API에서 가져온 브랜드:', brands.length);
      }
      
      // 실제 데이터에서 통계 계산
      let actualModels = 0;
      let actualTrims = 0;
      let actualOptions = 0;
      
      brands.forEach(brand => {
        brand.vehicle_lines?.forEach(vl => {
          actualModels += vl.models?.length || 0;
          vl.models?.forEach(model => {
            actualTrims += model.trims?.length || 0;
            model.trims?.forEach(trim => {
              actualOptions += trim.options?.length || 0;
            });
          });
        });
      });
      
      // 검색 상태가 있으면 검색 결과 통계 사용 (검색 결과가 0개여도 검색 중이면 0으로 표시)
      if (searchStats && searchStats.totalItems !== undefined) {
        setStatistics({
          brands: searchStats.totalBrands || 0,
          models: searchStats.totalModels || 0,
          trims: searchStats.totalTrims || 0,
          options: searchStats.totalOptions || 0,
          total: searchStats.totalItems || 0,
          totalPages: totalPages || 0
        });
      } else {
        setStatistics({
          brands: totalBrandsCount,   // 전체 시스템의 브랜드 수
          models: totalModelsCount,   // 전체 시스템의 모델 수
          trims: totalTrimsCount,     // 전체 시스템의 트림 수
          options: totalOptionsCount, // 전체 시스템의 옵션 수
          total: brands.length + actualModels + actualTrims + actualOptions, // 현재 버전의 전체 데이터 수
          totalPages: totalPages || 0
        });
      }
    } catch (error) {
      console.error('통계 데이터 로드 실패:', error);
      setError(error.message || '통계 데이터를 불러오는 데 실패했습니다.');
      
      // 에러 발생 시 기본값으로 설정
      setStatistics({
        brands: 0,
        models: 0,
        trims: 0,
        options: 0,
        total: 0,
        totalPages: 0
      });
    } finally {
      setLoading(false);
    }
  }, [selectedVersion?.id, versionData, totalPages, searchStats]);

  // 전체 통계 데이터 가져오기
  useEffect(() => {
    fetchTotalStatistics();
  }, [fetchTotalStatistics]);

  return {
    statistics,
    loading,
    error,
    refetch: fetchTotalStatistics,
  };
};

export default useStatistics;
