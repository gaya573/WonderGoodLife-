import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import versionAPI from '../../services/versionApi';

/**
 * 무한 스크롤 관리 커스텀 훅
 * 스크롤 이벤트 감지 및 추가 데이터 로딩을 관리
 */
export const useInfiniteScroll = (selectedVersion, useOptimizedAPI, useSplitAPI, versionData, setVersionData) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [shouldLoadMore, setShouldLoadMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1); // 내부 상태로 페이지 관리
  
  const totalPages = versionData?.pagination?.total_pages || 1;

  // 버전이 변경될 때 페이지 초기화 및 초기 데이터 로드
  useEffect(() => {
    if (selectedVersion) {
      setCurrentPage(1);
      setHasMore(true);
      console.log('🔄 버전 변경으로 페이지 초기화:', selectedVersion.id);
      
      // 초기 데이터 상태 확인
      if (!versionData || !versionData.vehicle_lines || versionData.vehicle_lines.length === 0) {
        console.log('🔄 초기 데이터 없음, 무한 스크롤용 초기 로드 대기 중...');
      } else {
        console.log('🔄 초기 데이터 있음:', {
          자동차라인수: versionData.vehicle_lines.length,
          자동차라인목록: versionData.vehicle_lines.map(vl => vl.name),
          pagination: versionData.pagination
        });
        
        // 초기 데이터가 있을 때 hasMore 상태 설정
        if (versionData.pagination) {
          const apiHasMore = versionData.pagination.has_next || false;
          const apiTotalPages = versionData.pagination.total_pages || 1;
          const newHasMore = apiHasMore && 1 < apiTotalPages;
          setHasMore(newHasMore);
          console.log('🔄 초기 hasMore 상태 설정:', {
            apiHasMore,
            apiTotalPages,
            newHasMore
          });
        }
      }
    }
  }, [selectedVersion?.id, versionData]);

  // versionData에서 페이지네이션 정보 추출 및 상태 업데이트
  useEffect(() => {
    if (versionData?.pagination) {
      // API 응답의 페이지네이션 정보 사용
      const apiTotalPages = versionData.pagination.total_pages || 1;
      const apiHasMore = versionData.pagination.has_next || false;
      
      console.log('📊 페이지네이션 정보 업데이트 (API 기준):', {
        apiTotalPages,
        apiHasMore,
        currentPage,
        calculatedHasMore: currentPage < apiTotalPages,
        totalBrands: versionData.pagination.total_count || 0,
        pagination: versionData.pagination
      });
      
      // API의 has_next를 우선 사용하되, 계산된 값도 고려
      setHasMore(apiHasMore && currentPage < apiTotalPages);
    }
  }, [versionData?.pagination, currentPage]);
  
  const observerRef = useRef();
  
  // 웹워커 제거 - 메인 스레드에서 직접 처리

  // 자동차 라인 중심 무한 스크롤 데이터 처리 함수
  const processVehicleLineInfiniteScrollDataInMainThread = useCallback((vehicle_lines, pagination) => {
    const startTime = performance.now();
    
    // 자동차 라인 중심으로 데이터 구조화
    const processedVehicleLines = [];
    const newAllBrands = [];
    const newAllModels = [];
    const newAllTrims = [];
    const newAllOptionTitles = [];
    const newAllOptionPrices = [];

    vehicle_lines.forEach(vehicleLine => {
      const vehicleLineData = {
        ...vehicleLine,
        brands: vehicleLine.brands || []
      };
      
      // 각 자동차 라인의 브랜드들 처리
      if (vehicleLine.brands && Array.isArray(vehicleLine.brands)) {
        vehicleLine.brands.forEach(brand => {
          newAllBrands.push({
            ...brand,
            vehicle_line_id: vehicleLine.id,
            vehicle_line_name: vehicleLine.name
          });
          
          // 각 브랜드의 모델들 처리
          if (brand.models && Array.isArray(brand.models)) {
            brand.models.forEach(model => {
              const modelData = {
                ...model,
                brand_id: brand.id,
                brand_name: brand.name,
                vehicle_line_id: vehicleLine.id,
                vehicle_line_name: vehicleLine.name
              };
              newAllModels.push(modelData);
              
              // 각 모델의 트림들 처리
              if (model.trims && Array.isArray(model.trims)) {
                model.trims.forEach(trim => {
                  const trimData = {
                    ...trim,
                    model_id: model.id,
                    model_name: model.name,
                    brand_id: brand.id,
                    brand_name: brand.name,
                    vehicle_line_id: vehicleLine.id,
                    vehicle_line_name: vehicleLine.name
                  };
                  newAllTrims.push(trimData);
                  
                  // 각 트림의 옵션들 처리
                  if (trim.options && Array.isArray(trim.options)) {
                    trim.options.forEach(option => {
                      const optionData = {
                        ...option,
                        trim_id: trim.id,
                        trim_name: trim.name,
                        model_id: model.id,
                        model_name: model.name,
                        brand_id: brand.id,
                        brand_name: brand.name,
                        vehicle_line_id: vehicleLine.id,
                        vehicle_line_name: vehicleLine.name
                      };
                      newAllOptionTitles.push(optionData);
                      newAllOptionPrices.push(optionData);
                    });
                  }
                });
              }
            });
          }
        });
      }
      
      processedVehicleLines.push(vehicleLineData);
    });

    const processingTime = performance.now() - startTime;

    return {
      processedVehicleLines,
      newAllBrands,
      newAllModels,
      newAllTrims,
      newAllOptionTitles,
      newAllOptionPrices,
      processingTime,
      stats: {
        vehicleLinesCount: processedVehicleLines.length,
        brandsCount: newAllBrands.length,
        modelsCount: newAllModels.length,
        trimsCount: newAllTrims.length,
        optionTitlesCount: newAllOptionTitles.length,
        optionPricesCount: newAllOptionPrices.length
      }
    };
  }, []);

  // 폴백용 메인 스레드 무한 스크롤 데이터 처리 함수
  const processInfiniteScrollDataInMainThread = useCallback((brands, pagination) => {
    const startTime = performance.now();
    
    // 브랜드 중심으로 데이터 구조화 (초기 로딩과 동일한 로직 적용)
    const uniqueBrands = [];
    const seenBrandIds = new Set();

    brands.forEach(brand => {
      if (!seenBrandIds.has(brand.id)) {
        seenBrandIds.add(brand.id);
        
        // 백엔드에서 브랜드 기준으로 전체 데이터를 보내므로 그대로 사용
        uniqueBrands.push({
          ...brand,
          vehicle_lines: brand.vehicle_lines || [],
          models: [] // BrandCard에서 vehicle_lines를 사용하므로 models는 빈 배열로 초기화
        });
      }
    });
    
    // 플랫 데이터 생성 (새로 추가된 브랜드들에 대해서만)
    const newAllModels = [];
    const newAllTrims = [];
    const newAllOptionTitles = [];
    const newAllOptionPrices = [];

    uniqueBrands.forEach(brand => {
      if (brand.vehicle_lines && Array.isArray(brand.vehicle_lines)) {
        brand.vehicle_lines.forEach(vehicleLine => {
          if (vehicleLine.models && Array.isArray(vehicleLine.models)) {
            vehicleLine.models.forEach(model => {
              newAllModels.push({
                ...model,
                brand_id: brand.id,
                vehicle_line_name: vehicleLine.name
              });
              if (model.trims && Array.isArray(model.trims)) {
                model.trims.forEach(trim => {
                  newAllTrims.push(trim);
                  if (trim.options && Array.isArray(trim.options)) {
                    trim.options.forEach(option => {
                      newAllOptionTitles.push(option);
                      newAllOptionPrices.push(option);
                    });
                  }
                });
              }
            });
          }
        });
      }
    });

    const processingTime = performance.now() - startTime;

    return {
      uniqueBrands,
      newAllModels,
      newAllTrims,
      newAllOptionTitles,
      newAllOptionPrices,
      processingTime,
      stats: {
        brandsCount: uniqueBrands.length,
        modelsCount: newAllModels.length,
        trimsCount: newAllTrims.length,
        optionTitlesCount: newAllOptionTitles.length,
        optionPricesCount: newAllOptionPrices.length
      }
    };
  }, []);

  // 추가 데이터 로드 함수
  const loadMoreData = useCallback(async () => {
    console.log('🔄 loadMoreData 함수 호출됨!');
    
    // 더 엄격한 조건 확인
    if (!selectedVersion || loadingMore || !hasMore || currentPage >= totalPages) {
      console.log('🚫 loadMoreData 조건 불충족:', {
        selectedVersion: !!selectedVersion,
        loadingMore,
        hasMore,
        currentPage,
        totalPages,
        versionDataPagination: versionData?.pagination,
        condition: !selectedVersion ? 'no-version' : 
                  loadingMore ? 'loading' : 
                  !hasMore ? 'no-more' : 
                  currentPage >= totalPages ? 'page-limit' : 'unknown'
      });
      return;
    }
    
    console.log('loadMoreData 시작:', { currentPage, totalPages, hasMore });
    setLoadingMore(true);
    
    try {
      const nextPage = currentPage + 1;
      
      // 새로운 브랜드별 전체 데이터 API 사용
      let response;
      if (useSplitAPI) {
        // 분할된 API 사용 (기존 방식 유지)
        response = await versionAPI.getBrands(selectedVersion.id, {
          page: nextPage,
          limit: 1 // 무한 스크롤: 1개씩 추가 로드
        });
        
        // 브랜드 데이터 구조 변환 - 초기 로딩과 동일한 구조로 맞춤
        response.data = {
          version: { id: selectedVersion.id },
          brands: response.data.brands.map(brand => ({
            ...brand,
            models: [] // 빈 모델 배열로 초기화
          })),
          pagination: response.data.pagination
        };
      } else {
        // 새로운 자동차 라인별 전체 데이터 API 사용 (각 자동차 라인의 모든 브랜드/모델/트림/옵션 포함)
        console.log('🚗 API 호출 - getVehicleLinesWithFullData:', {
          versionId: selectedVersion.id,
          page: nextPage,
          limit: 1
        });
        
        response = await versionAPI.getVehicleLinesWithFullData(selectedVersion.id, {
          page: nextPage,
          limit: 10 // 자동차 라인 단위 무한 스크롤: 10개씩 추가 로드
        });
        
        console.log('📡 API 응답 - getVehicleLinesWithFullData:', {
          status: response.status,
          vehicleLinesCount: response.data?.vehicle_lines?.length || 0,
          pagination: response.data?.pagination
        });
        
        // 새로 로드된 자동차 라인과 브랜드명들만 출력
        if (response.data?.vehicle_lines?.length > 0) {
          const newVehicleLines = [];
          const newBrands = [];
          response.data.vehicle_lines.forEach(vehicleLine => {
            newVehicleLines.push(vehicleLine.name);
            if (vehicleLine.brands?.length > 0) {
              vehicleLine.brands.forEach(brand => {
                newBrands.push(brand.name);
              });
            }
          });
          console.log('🆕 새로 로드된 자동차 라인들:', newVehicleLines);
          console.log('🆕 새로 로드된 브랜드들:', newBrands);
        }
      }
      
      const { version, vehicle_lines, pagination } = response.data;
      
      console.log('loadMoreData 응답 (자동차 라인 중심):', { 
        nextPage, 
        vehicleLinesCount: vehicle_lines?.length || 0, 
        pagination,
        totalPages: pagination?.total_pages,
        firstVehicleLine: vehicle_lines?.[0] ? {
          id: vehicle_lines[0].id,
          name: vehicle_lines[0].name,
          brands: vehicle_lines[0].brands?.length || 0
        } : null
      });
      
      if (vehicle_lines && vehicle_lines.length > 0) {
        // 웹워커 제거 - 메인 스레드에서 직접 처리
        console.log('🔄 메인 스레드에서 무한 스크롤 데이터 처리 중...');
        const processedData = processVehicleLineInfiniteScrollDataInMainThread(vehicle_lines, pagination);

        console.log('loadMoreData 처리된 자동차 라인:', { 
          originalCount: vehicle_lines.length,
          processedCount: processedData.processedVehicleLines.length,
          processedVehicleLines: processedData.processedVehicleLines.map(vl => ({
            id: vl.id,
            name: vl.name,
            brandsCount: vl.brands?.length || 0
          })),
          processingTime: processedData.processingTime
        });
        
        // 기존 데이터에 새 데이터 추가 (자동차 라인과 플랫 데이터 모두)
        console.log('🔄 setVersionData 호출 전 상태:', {
          prevVehicleLinesCount: versionData?.vehicle_lines?.length || 0,
          newVehicleLinesCount: processedData.processedVehicleLines.length,
          newVehicleLineNames: processedData.processedVehicleLines.map(vl => vl.name)
        });
        
        setVersionData(prevData => {
          // prevData가 null이거나 undefined인 경우 기본값 설정
          const safePrevData = prevData || {
            vehicle_lines: [],
            brands: [],
            models: [],
            trims: [],
            optionTitles: [],
            optionPrices: []
          };
          
          // 중복 제거: 기존 vehicle_lines의 ID와 새로운 vehicle_lines의 ID 비교
          const existingVehicleLineIds = new Set((safePrevData.vehicle_lines || []).map(vl => vl.id));
          const newUniqueVehicleLines = processedData.processedVehicleLines.filter(vl => !existingVehicleLineIds.has(vl.id));
          
          console.log('🔄 중복 제거 결과:', {
            기존자동차라인수: safePrevData.vehicle_lines?.length || 0,
            새로받은자동차라인수: processedData.processedVehicleLines.length,
            중복제거후자동차라인수: newUniqueVehicleLines.length,
            중복제거된자동차라인수: processedData.processedVehicleLines.length - newUniqueVehicleLines.length
          });
          
          const newData = {
            ...safePrevData,
            vehicle_lines: [...(safePrevData.vehicle_lines || []), ...newUniqueVehicleLines],
            brands: [...(safePrevData.brands || []), ...processedData.newAllBrands],
            models: [...(safePrevData.models || []), ...processedData.newAllModels],
            trims: [...(safePrevData.trims || []), ...processedData.newAllTrims],
            optionTitles: [...(safePrevData.optionTitles || []), ...processedData.newAllOptionTitles],
            optionPrices: [...(safePrevData.optionPrices || []), ...processedData.newAllOptionPrices],
            // 페이지네이션 정보 업데이트
            pagination: pagination
          };
          
          console.log('✅ setVersionData 새로운 상태:', {
            prevVehicleLinesCount: safePrevData.vehicle_lines?.length || 0,
            newVehicleLinesCount: processedData.processedVehicleLines.length,
            finalVehicleLinesCount: newData.vehicle_lines?.length || 0,
            allVehicleLineNames: newData.vehicle_lines?.map(vl => vl.name) || []
          });
          
          // 현재 로드된 모든 브랜드명들만 출력
          const allCurrentBrands = [];
          newData.vehicle_lines.forEach(vehicleLine => {
            if (vehicleLine.brands?.length > 0) {
              vehicleLine.brands.forEach(brand => {
                allCurrentBrands.push(brand.name);
              });
            }
          });
          console.log('📋 현재 로드된 모든 브랜드들:', allCurrentBrands);
          
          return newData;
        });
        
        // 무한스크롤에서는 URL을 변경하지 않음 (내부 상태만 관리)
        // URL 변경은 페이지 리로딩을 유발하므로 무한스크롤과 맞지 않음
        
        // 내부 페이지 상태 업데이트
        setCurrentPage(nextPage);
        
        // 페이지네이션 상태 업데이트 - API 응답 기준
        const newHasMore = pagination ? nextPage < pagination.total_pages : false;
        setHasMore(newHasMore);
        
        console.log('🔄 페이지네이션 상태 업데이트:', {
          nextPage,
          totalPages: pagination?.total_pages,
          hasMore: newHasMore,
          vehicleLinesAdded: processedData.processedVehicleLines.length
        });
        
        console.log('loadMoreData 성공:', { 
          nextPage, 
          newHasMore, 
          totalPages: pagination?.total_pages,
          addedVehicleLines: processedData.processedVehicleLines.length,
          addedBrands: processedData.newAllBrands.length,
          addedModels: processedData.newAllModels.length,
          addedTrims: processedData.newAllTrims.length,
          addedOptionTitles: processedData.newAllOptionTitles.length,
          addedOptionPrices: processedData.newAllOptionPrices.length
        });
      } else {
        console.log('loadMoreData: 더 이상 데이터 없음');
        setHasMore(false);
      }
    } catch (err) {
      console.error('Failed to load more data:', err);
      setHasMore(false);
    } finally {
      setLoadingMore(false);
    }
  }, [selectedVersion, loadingMore, hasMore, currentPage, totalPages, useOptimizedAPI, useSplitAPI, setVersionData, processVehicleLineInfiniteScrollDataInMainThread]);

  // 스크롤 이벤트로 무한 스크롤 구현
  useEffect(() => {
    let throttleTimer = null;
    
    const handleScroll = () => {
      // throttling으로 성능 최적화
      if (throttleTimer) return;
      
      throttleTimer = setTimeout(() => {
        // 스크롤이 맨 아래에서 1/5 지점에 도달했을 때 (더 빠른 로딩)
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // 전체 문서 높이의 1/5 지점에서 로딩 시작
        const threshold = documentHeight * 0.2; // 20% 지점
        const isNearBottom = scrollTop + windowHeight >= documentHeight - threshold;
        
        console.log('스크롤 이벤트:', {
          scrollTop,
          windowHeight,
          documentHeight,
          scrollBottom: scrollTop + windowHeight,
          threshold: documentHeight - threshold,
          thresholdPercent: '20%',
          isNearBottom,
          hasMore,
          loadingMore,
          currentPage,
          totalPages
        });
        
        if (isNearBottom && hasMore && !loadingMore && currentPage < totalPages) {
          console.log('🚀 스크롤로 추가 로딩 플래그 설정!');
          setShouldLoadMore(true);
        }
        
        throttleTimer = null;
      }, 100); // 100ms throttling
    };

    // 스크롤 이벤트 리스너 추가
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // 컴포넌트 언마운트 시 이벤트 리스너 제거
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (throttleTimer) {
        clearTimeout(throttleTimer);
      }
    };
  }, [hasMore, loadingMore, currentPage, totalPages]);

  // 스크롤로 인한 추가 로딩 처리
  useEffect(() => {
    if (shouldLoadMore && hasMore && !loadingMore && currentPage < totalPages) {
      console.log('🚀 shouldLoadMore 플래그로 loadMoreData 호출!');
      setShouldLoadMore(false); // 플래그 리셋
      loadMoreData(); // 실제로 loadMoreData 호출
    }
  }, [shouldLoadMore, hasMore, loadingMore, currentPage, totalPages, loadMoreData]);

  // Intersection Observer는 비활성화하고 스크롤 이벤트만 사용
  const lastBrandElementRef = useCallback(node => {
    console.log('lastBrandElementRef 호출됨 (스크롤 이벤트 사용):', { 
      node: !!node, 
      hasMore, 
      loadingMore, 
      currentPage, 
      totalPages
    });
    
    // Observer는 사용하지 않음 - 스크롤 이벤트로 대체
    if (observerRef.current) {
      observerRef.current.disconnect();
      observerRef.current = null;
    }
  }, [hasMore, loadingMore, currentPage, totalPages]);

  // 컴포넌트 언마운트 시 observer 정리
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, []);

  // 페이지네이션 상태 리셋
  const resetPagination = useCallback(() => {
    setCurrentPage(1);
    setHasMore(true);
    console.log('🔄 페이지네이션 상태 리셋');
  }, []);

  // 페이지네이션 상태 설정 (사용하지 않음 - 내부 상태로 관리)
  const setPagination = useCallback((pagination) => {
    if (pagination) {
      const totalPages = pagination.total_pages || 1;
      const currentPageNum = pagination.current_page || 1;
      
      // 내부 상태는 자동으로 관리되므로 여기서는 로그만 출력
      console.log('페이지네이션 정보 수신:', {
        currentPage: currentPageNum,
        totalPages,
        hasMore: currentPageNum < totalPages
      });
    } else {
      console.log('페이지네이션 정보 없음');
    }
  }, []);

  return {
    loadingMore,
    hasMore,
    currentPage,
    totalPages,
    shouldLoadMore,
    lastBrandElementRef,
    loadMoreData,
    resetPagination,
    setPagination
  };
};
