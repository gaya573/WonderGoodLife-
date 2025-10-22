import { useState, useEffect, useCallback } from 'react';
import versionAPI from '../../services/versionApi';
import { stagingBrandAPI, stagingModelAPI, stagingTrimAPI, stagingOptionTitleAPI, stagingOptionPriceAPI } from '../../services/api';

/**
 * 버전 데이터 관리 커스텀 훅
 * 버전 목록, 선택된 버전, 데이터 로딩 등을 관리
 */
export const useVersionData = (searchParams) => {
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [versionData, setVersionData] = useState({
    vehicle_lines: [],
    brands: [],
    models: [],
    trims: [],
    optionTitles: [],
    optionPrices: []
  });
  const [loading, setLoading] = useState(true);
  const [useOptimizedAPI, setUseOptimizedAPI] = useState(true);
  const [useSplitAPI, setUseSplitAPI] = useState(false);
  const [searchFilter, setSearchFilter] = useState(null);
  
  // 검색 결과에 따른 데이터 필터링
  const applySearchFilter = useCallback((data, searchResults) => {
    if (!searchResults || searchResults.length === 0) {
      return data;
    }
    
    console.log('🔍 검색 필터 적용 시작:', searchResults);
    
    // 검색 결과에서 브랜드 ID들 추출
    const brandIds = new Set();
    searchResults.forEach(result => {
      if (result.type === 'brand' && result.id) {
        brandIds.add(result.id);
      }
    });
    
    console.log('🔍 필터링할 브랜드 ID들:', Array.from(brandIds));
    
    // 브랜드 데이터 필터링
    const filteredBrands = data.brands.filter(brand => brandIds.has(brand.id));
    
    console.log('🔍 필터링된 브랜드 수:', filteredBrands.length);
    
    return {
      ...data,
      brands: filteredBrands
    };
  }, []);

  // 자동차 라인 중심 데이터 처리 함수
  const processVehicleLineDataInMainThread = useCallback((version, vehicle_lines, pagination) => {
    const startTime = performance.now();
    
    console.log('🚗 자동차 라인 데이터 처리 시작:', {
      총자동차라인수: vehicle_lines.length,
      자동차라인목록: vehicle_lines.map(vl => ({ id: vl.id, name: vl.name }))
    });

    // 자동차 라인 중심으로 데이터 구조화
    const processedVehicleLines = [];
    const allBrands = [];
    const allModels = [];
    const allTrims = [];
    const allOptionTitles = [];
    const allOptionPrices = [];

    vehicle_lines.forEach((vehicleLine, index) => {
      console.log(`🚗 자동차 라인 ${index + 1} 처리:`, { id: vehicleLine.id, name: vehicleLine.name });
      
      const vehicleLineData = {
        id: vehicleLine.id,
        name: vehicleLine.name,
        description: vehicleLine.description,
        brand: vehicleLine.brand, // 브랜드 정보 직접 포함
        models: vehicleLine.models || []
      };
      
      // 각 자동차 라인의 브랜드 정보 처리
      if (vehicleLine.brand) {
        allBrands.push({
          ...vehicleLine.brand,
          vehicle_line_id: vehicleLine.id,
          vehicle_line_name: vehicleLine.name
        });
      }
      
      // 각 자동차 라인의 모델들 처리
      if (vehicleLine.models && Array.isArray(vehicleLine.models)) {
        vehicleLine.models.forEach(model => {
          const modelData = {
            ...model,
            brand_id: vehicleLine.brand?.id,
            brand_name: vehicleLine.brand?.name,
            vehicle_line_id: vehicleLine.id,
            vehicle_line_name: vehicleLine.name
          };
          allModels.push(modelData);
          
          // 각 모델의 트림들 처리
          if (model.trims && Array.isArray(model.trims)) {
            model.trims.forEach(trim => {
              const trimData = {
                ...trim,
                model_id: model.id,
                model_name: model.name,
                brand_id: vehicleLine.brand?.id,
                brand_name: vehicleLine.brand?.name,
                vehicle_line_id: vehicleLine.id,
                vehicle_line_name: vehicleLine.name
              };
              allTrims.push(trimData);
              
              // 각 트림의 옵션들 처리
              if (trim.options && Array.isArray(trim.options)) {
                trim.options.forEach(option => {
                  const optionData = {
                    ...option,
                    trim_id: trim.id,
                    trim_name: trim.name,
                    model_id: model.id,
                    model_name: model.name,
                    brand_id: vehicleLine.brand?.id,
                    brand_name: vehicleLine.brand?.name,
                    vehicle_line_id: vehicleLine.id,
                    vehicle_line_name: vehicleLine.name
                  };
                  allOptionTitles.push(optionData);
                  allOptionPrices.push(optionData);
                });
              }
            });
          }
        });
      }
      
      processedVehicleLines.push(vehicleLineData);
      console.log(`✅ 자동차 라인 추가됨: ${vehicleLine.name} (ID: ${vehicleLine.id})`);
    });

    const processingTime = performance.now() - startTime;

    return {
      version,
      vehicle_lines: processedVehicleLines,
      allBrands,
      allModels,
      allTrims,
      allOptionTitles,
      allOptionPrices,
      pagination,
      processingTime,
      stats: {
        vehicleLinesCount: processedVehicleLines.length,
        brandsCount: allBrands.length,
        modelsCount: allModels.length,
        trimsCount: allTrims.length,
        optionTitlesCount: allOptionTitles.length,
        optionPricesCount: allOptionPrices.length
      }
    };
  }, []);

  // 폴백용 메인 스레드 데이터 처리 함수
  const processDataInMainThread = useCallback((version, brands, pagination) => {
    const startTime = performance.now();
    
    // 브랜드 중심으로 데이터 구조화
    const uniqueBrands = [];
    const seenBrandIds = new Set();

    console.log('🔍 브랜드 데이터 처리 시작:', {
      총브랜드수: brands.length,
      브랜드목록: brands.map(b => ({ id: b.id, name: b.name }))
    });

    brands.forEach((brand, index) => {
      console.log(`🔍 브랜드 ${index + 1} 처리:`, { id: brand.id, name: brand.name });
      
      if (!seenBrandIds.has(brand.id)) {
        seenBrandIds.add(brand.id);
        
        const models = [];
        if (brand.vehicle_lines && Array.isArray(brand.vehicle_lines)) {
          brand.vehicle_lines.forEach(vehicleLine => {
            if (vehicleLine.models && Array.isArray(vehicleLine.models)) {
              vehicleLine.models.forEach(model => {
                models.push({
                  ...model,
                  brand_id: brand.id,
                  vehicle_line_name: vehicleLine.name
                });
              });
            }
          });
        }

        uniqueBrands.push({
          ...brand,
          vehicle_lines: brand.vehicle_lines || [],
          models: [] // BrandCard에서 vehicle_lines를 사용하므로 models는 빈 배열로 초기화
        });
        
        console.log(`✅ 브랜드 추가됨: ${brand.name} (ID: ${brand.id})`);
      } else {
        console.log(`⚠️ 중복 브랜드 스킵: ${brand.name} (ID: ${brand.id})`);
      }
    });

    // 플랫 데이터로도 저장
    const allModels = [];
    const allTrims = [];
    const allOptionTitles = [];
    const allOptionPrices = [];

    uniqueBrands.forEach(brand => {
      if (brand.vehicle_lines && Array.isArray(brand.vehicle_lines)) {
        brand.vehicle_lines.forEach(vehicleLine => {
          if (vehicleLine.models && Array.isArray(vehicleLine.models)) {
            vehicleLine.models.forEach(model => {
              allModels.push({
                ...model,
                brand_id: brand.id,
                vehicle_line_name: vehicleLine.name
              });
              if (model.trims && Array.isArray(model.trims)) {
                model.trims.forEach(trim => {
                  allTrims.push(trim);
                  if (trim.options && Array.isArray(trim.options)) {
                    trim.options.forEach(option => {
                      allOptionTitles.push(option);
                      allOptionPrices.push(option);
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
      version,
      uniqueBrands,
      allModels,
      allTrims,
      allOptionTitles,
      allOptionPrices,
      pagination,
      processingTime,
      stats: {
        brandsCount: uniqueBrands.length,
        modelsCount: allModels.length,
        trimsCount: allTrims.length,
        optionTitlesCount: allOptionTitles.length,
        optionPricesCount: allOptionPrices.length
      }
    };
  }, []);

  // 버전 목록 로드
  const loadVersions = useCallback(async () => {
    try {
      setLoading(true);
      const response = await versionAPI.getAll({ limit: 100 });
      
      const versionsData = response.data;
      let versions = [];
      if (versionsData && versionsData.items) {
        versions = versionsData.items;
      } else if (Array.isArray(versionsData)) {
        versions = versionsData;
      }
      
      setVersions(versions);
      
      // URL 파라미터 확인
      const versionId = searchParams.get('version_id');
      const searchQuery = searchParams.get('search');
      
      console.log('🔍 초기 로딩 시 URL 파라미터 확인:', { versionId, searchQuery });
      
      if (!versionId && versions && versions.length > 0) {
        const firstVersion = versions[0];
        if (firstVersion && firstVersion.id) {
          setSelectedVersion(firstVersion);
          loadVersionData(firstVersion.id);
        }
      } else if (!versionId) {
        setSelectedVersion(null);
        setVersionData({
          brands: [],
          models: [],
          trims: [],
          optionTitles: [],
          optionPrices: []
        });
      } else if (versionId) {
        // URL에 version_id가 있으면 해당 버전 찾기
        const targetVersion = versions.find(v => v.id == versionId);
        if (targetVersion) {
          console.log('🔍 URL에서 버전 찾음:', targetVersion);
          setSelectedVersion(targetVersion);
          loadVersionData(targetVersion.id);
        }
      }
    } catch (err) {
      console.error('Failed to load versions:', err);
      setVersions([]);
      setSelectedVersion(null);
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  // 기존 loadVersionData 함수 제거 - 무한 루프 방지를 위해
  const loadVersionData = useCallback(async (versionId, reset = true) => {
    console.log('⚠️ 기존 loadVersionData 호출됨 - 사용하지 않음');
    return;
  }, []);

  // 새로운 단일 실행 데이터 로드 함수
  const loadVersionDataNew = useCallback(async (versionId, reset = true) => {
    if (!versionId || versionId === 'undefined' || versionId === undefined) {
      setVersionData({
        brands: [],
        models: [],
        trims: [],
        optionTitles: [],
        optionPrices: []
      });
      return;
    }

    try {
      if (reset) {
        setLoading(true);
      }

      // URL 파라미터에서 검색어 확인
      const searchQuery = searchParams.get('search');
      console.log('🔍 ===== loadVersionData 시작 =====');
      console.log('🔍 검색어 확인:', searchQuery);
      console.log('🔍 versionId:', versionId);
      console.log('🔍 reset:', reset);
      
      // 검색어가 있으면 검색 필터링된 데이터 가져오기
      if (searchQuery && searchQuery.trim()) {
        console.log('🔍 검색어가 있음, 검색 필터링된 데이터 가져오기');
        console.log('🔍 API 호출 파라미터:', { versionId, searchQuery });
        
        try {
          const searchResponse = await versionAPI.getSearchFilteredData(versionId, searchQuery);
          console.log('🔍 검색 필터링된 데이터 응답:', searchResponse);
          console.log('🔍 검색 필터링된 데이터 brands:', searchResponse.data?.brands);
          console.log('🔍 검색 필터링된 데이터 brands 개수:', searchResponse.data?.brands?.length || 0);
          
          // 검색 필터링된 데이터를 그대로 사용
          const filteredData = {
            brands: searchResponse.data.brands || [],
            models: [],
            trims: [],
            optionTitles: [],
            optionPrices: [],
            filtered_by_search: true,
            search_query: searchQuery
          };
          
          console.log('🔍 ===== 필터링된 데이터 설정 =====');
          console.log('🔍 설정할 필터링된 데이터:', filteredData);
          console.log('🔍 브랜드 개수:', filteredData.brands.length);
          console.log('🔍 첫 번째 브랜드:', filteredData.brands[0]);
          
          setVersionData(filteredData);
          console.log('✅ setVersionData 호출 완료');
          return;
        } catch (error) {
          console.error('🔍 검색 필터링된 데이터 가져오기 실패:', error);
          console.error('🔍 에러 상세:', error.response?.data || error.message);
          // 검색 실패 시 전체 데이터 로드로 폴백
        }
      }
      
      console.log('🔍 loadVersionData - 전체 데이터 로드');
      
      // API 선택 로직 - 새로운 브랜드별 전체 데이터 API 사용
      let response;
      if (useSplitAPI) {
        // 분할된 API 사용 - 브랜드 목록만 먼저 조회
        response = await versionAPI.getBrands(versionId, {
          page: reset ? 1 : 1,
          limit: 1 // 초기 로딩: 1개 브랜드만 로드
        });
        
        // 브랜드 데이터 구조를 기존 형식에 맞게 변환
        response.data = {
          version: { id: versionId },
          brands: response.data.brands.map(brand => ({
            ...brand,
            models: [] // 빈 구조로 초기화
          })),
          pagination: response.data.pagination
        };
      } else {
        // 새로운 브랜드별 전체 데이터 API 사용 (각 브랜드의 모든 트림/옵션 포함)
        console.log('🔍 초기 API 호출 - getBrandsWithFullData:', {
          versionId,
          page: reset ? 1 : 1,
          limit: 1
        });
        
        response = await versionAPI.getBrandsWithFullData(versionId, {
          page: reset ? 1 : 1,
          limit: 1 // 페이지네이션: 1개씩 로드
        });
        
        console.log('📡 초기 API 응답 - getBrandsWithFullData:', {
          status: response.status,
          brandsCount: response.data?.brands?.length || 0,
          pagination: response.data?.pagination
        });
        
        // 현재 로드된 모델명들만 출력
        if (response.data?.brands?.length > 0) {
          const allModels = [];
          response.data.brands.forEach(brand => {
            if (brand.vehicle_lines?.length > 0) {
              brand.vehicle_lines.forEach(vehicleLine => {
                if (vehicleLine.models?.length > 0) {
                  vehicleLine.models.forEach(model => {
                    allModels.push(model.name);
                  });
                }
              });
            }
          });
          console.log('🚗 현재 로드된 모델들:', allModels);
        }
      }

      const { version, brands, pagination } = response.data;
      
      console.log('🔍 API 응답 데이터:', {
        versionId,
        useOptimizedAPI,
        useSplitAPI,
        version: version ? {
          id: version.id,
          total_brands: version.total_brands,
          total_models: version.total_models,
          total_trims: version.total_trims
        } : null,
        brandsCount: brands?.length || 0,
        firstBrand: brands?.[0] ? {
          id: brands[0].id,
          name: brands[0].name,
          vehicle_lines: brands[0].vehicle_lines?.length || 0,
          models: brands[0].vehicle_lines?.reduce((total, vl) => total + (vl.models?.length || 0), 0) || 0
        } : null,
        pagination: pagination ? {
          current_page: pagination.current_page,
          total_pages: pagination.total_pages,
          total_count: pagination.total_count,
          has_next: pagination.has_next,
          has_prev: pagination.has_prev
        } : null
      });

      if (!brands || !Array.isArray(brands)) {
        if (reset) {
          setVersionData({
            brands: [],
            models: [],
            trims: [],
            optionTitles: [],
            optionPrices: []
          });
        }
        return;
      }

      // 웹워커 제거 - 메인 스레드에서 직접 처리
      console.log('🔄 메인 스레드에서 데이터 처리 중...');
      const processedData = processDataInMainThread(version, brands, pagination);

      const finalData = {
        brands: processedData.uniqueBrands,
        models: processedData.allModels,
        trims: processedData.allTrims,
        optionTitles: processedData.allOptionTitles,
        optionPrices: processedData.allOptionPrices,
        // 페이지네이션 정보 저장
        pagination: pagination,
        // 전체 통계 정보 저장
        totalStats: {
          totalBrands: version.total_brands || 0,
          totalModels: version.total_models || 0,
          totalTrims: version.total_trims || 0,
          totalOptions: version.total_options || 0, // 백엔드에서 통합된 옵션 개수
          totalData: (version.total_brands || 0) + (version.total_models || 0) + (version.total_trims || 0) + (version.total_options || 0)
        }
      };

      if (reset) {
        setVersionData(finalData);
      }
    } catch (err) {
      console.error('Failed to load version data:', err);
      setVersionData({
        brands: [],
        models: [],
        trims: [],
        optionTitles: [],
        optionPrices: []
      });
    } finally {
      if (reset) {
        setLoading(false);
      }
    }
  }, [useOptimizedAPI, useSplitAPI]);

  // 단일 실행 데이터 로드 함수 (무한 루프 방지)
  const loadVersionDataOnce = useCallback(async (versionId, searchQuery = null) => {
    if (!versionId || versionId === 'undefined' || versionId === undefined) {
      setVersionData({
        brands: [],
        models: [],
        trims: [],
        optionTitles: [],
        optionPrices: []
      });
      return;
    }

    try {
      console.log('🚀 ===== 데이터 로드 시작 =====');
      console.log('🔍 URL 파라미터:', { versionId, searchQuery });
      
      setLoading(true);

      // 검색어가 있으면 검색 API 호출, 없으면 전체 데이터 로드
      if (searchQuery && searchQuery.trim()) {
        console.log('🔍 검색 API 호출:', searchQuery);
        
        const searchResponse = await versionAPI.searchData(versionId, searchQuery, 'all', 20);
        
        const searchData = searchResponse.data;
        console.log('🔍 검색 결과:', searchData);
        
        // 모델 데이터를 브랜드 중심으로 변환
        const brandsMap = new Map();
        
        console.log('🔍 검색 데이터 변환 시작:', {
          modelsCount: searchData.models?.length || 0,
          models: searchData.models
        });
        
        if (searchData.models && searchData.models.length > 0) {
          searchData.models.forEach((model, index) => {
            console.log(`🔍 모델 ${index + 1} 처리:`, model);
            
            const brandId = model.brand_id;
            
            if (!brandsMap.has(brandId)) {
              brandsMap.set(brandId, {
                id: brandId,
                name: model.brand_name,
                country: 'KR', // 기본값
                logo_url: null,
                vehicle_lines: [{
                  id: model.vehicle_line_id,
                  name: model.vehicle_line_name,
                  models: []
                }]
              });
              console.log(`🔍 새 브랜드 생성: ${model.brand_name} (ID: ${brandId})`);
            }
            
            const brand = brandsMap.get(brandId);
            let vehicleLine = brand.vehicle_lines.find(vl => vl.id === model.vehicle_line_id);
            
            if (!vehicleLine) {
              vehicleLine = {
                id: model.vehicle_line_id,
                name: model.vehicle_line_name,
                models: []
              };
              brand.vehicle_lines.push(vehicleLine);
              console.log(`🔍 새 차량라인 추가: ${model.vehicle_line_name} (ID: ${model.vehicle_line_id})`);
            }
            
            vehicleLine.models.push({
              id: model.id,
              name: model.name,
              code: model.code,
              price: model.price,
              foreign: model.foreign,
              trims: model.trims || []
            });
            console.log(`🔍 모델 추가: ${model.name} (ID: ${model.id})`);
          });
        }
        
        const convertedBrands = Array.from(brandsMap.values());
        console.log('🔍 변환된 브랜드 맵:', convertedBrands);
        console.log('🔍 변환된 브랜드 수:', convertedBrands.length);
        
        // 중복 제거 확인
        const uniqueBrandIds = new Set(convertedBrands.map(b => b.id));
        console.log('🔍 고유 브랜드 ID 수:', uniqueBrandIds.size);
        
        const filteredData = {
          brands: convertedBrands, // 브랜드 중심으로 변환
          models: searchData.models || [], // 모델 중심 데이터도 유지
          trims: [],
          optionTitles: [],
          optionPrices: [],
          filtered_by_search: true,
          search_query: searchData.search_query || searchQuery,
          total_count: searchData.total_count || 0,
          pagination: {
            current_page: 1,
            total_pages: 1
          }
        };
        
        console.log('✅ 검색 필터링된 데이터 로드 완료:', { 
          브랜드수: filteredData.brands.length,
          모델수: filteredData.models.length,
          검색어: filteredData.search_query,
          전체데이터수: filteredData.total_count
        });
        setVersionData(filteredData);
        return;
      }
      
      // 전체 데이터 로드 (무한 스크롤용 초기 로드) - 자동차 라인 중심
      console.log('🚗 자동차 라인 중심 데이터 로드 (무한 스크롤용)');
      const response = await versionAPI.getVehicleLinesWithFullData(versionId, {
        page: 1,
        limit: 10  // 초기 로드 시 10개 자동차 라인 로드
      });
      
      const { version, vehicle_lines, pagination } = response.data;
      const processedData = processVehicleLineDataInMainThread(version, vehicle_lines, pagination);
      
      console.log('✅ 자동차 라인 중심 데이터 설정 (무한 스크롤용):', {
        자동차라인수: processedData.vehicle_lines?.length || 0,
        자동차라인목록: processedData.vehicle_lines?.map(vl => vl.name) || [],
        브랜드수: processedData.allBrands?.length || 0,
        페이지네이션: processedData.pagination
      });
      
      const finalData = {
        vehicle_lines: processedData.vehicle_lines,
        brands: processedData.allBrands,
        models: processedData.allModels,
        trims: processedData.allTrims,
        optionTitles: processedData.allOptionTitles,
        optionPrices: processedData.allOptionPrices,
        pagination: pagination,
        totalStats: {
          totalVehicleLines: version.total_vehicle_lines || 0,
          totalBrands: version.total_brands || 0,
          totalModels: version.total_models || 0,
          totalTrims: version.total_trims || 0,
          totalOptions: version.total_options || 0,
          totalData: (version.total_vehicle_lines || 0) + (version.total_brands || 0) + (version.total_models || 0) + (version.total_trims || 0) + (version.total_options || 0)
        }
      };
      
      setVersionData(finalData);
      
    } catch (error) {
      console.error('❌ 데이터 로드 실패:', error);
      setVersionData({
        vehicle_lines: [],
        brands: [],
        models: [],
        trims: [],
        optionTitles: [],
        optionPrices: []
      });
    } finally {
      setLoading(false);
    }
  }, [processVehicleLineDataInMainThread]);

  // 중복된 useEffect 제거됨

  // 버전 변경 핸들러
  const handleVersionChange = useCallback((version) => {
    if (!version || !version.id) {
      console.warn('Invalid version object:', version);
      return;
    }
    setSelectedVersion(version);
    loadVersionData(version.id, true);
  }, [loadVersionData]);

  // 초기 로드
  useEffect(() => {
    loadVersions();
  }, [loadVersions]);

  // URL 파라미터에서 버전 ID 확인 (버전 목록 로드 후)
  useEffect(() => {
    const versionId = searchParams.get('version_id');
    const searchQuery = searchParams.get('search');
    
    console.log('🔄 URL 파라미터 처리:', { versionId, searchQuery, versionsLength: versions.length });
    
    if (versionId && versions.length > 0) {
      const targetId = parseInt(versionId);
      const version = versions.find(v => v.id === targetId);
      
      console.log('🔄 버전 찾기:', { targetId, version: version?.id, selectedVersion: selectedVersion?.id });
      
      if (version) {
        setSelectedVersion(version);
        
        // 검색어가 있으면 검색 API 호출, 없으면 전체 데이터 로드 (무한 스크롤용)
        if (searchQuery && searchQuery.trim()) {
          console.log('🔄 검색어 있음, 검색 API 호출:', searchQuery);
          loadVersionDataOnce(version.id, searchQuery);
        } else {
          console.log('🔄 검색어 없음, 전체 데이터 로드 (무한 스크롤용) - 현대 포함');
          loadVersionDataOnce(version.id, null);
        }
      } else {
        console.error('🔄 버전을 찾을 수 없음:', targetId, '사용 가능한 버전들:', versions.map(v => v.id));
      }
    }
  }, [searchParams, versions, loadVersionDataOnce, selectedVersion?.id]);

  return {
    versions,
    selectedVersion,
    versionData,
    setVersionData,
    loading,
    useOptimizedAPI,
    useSplitAPI,
    setUseOptimizedAPI,
    setUseSplitAPI,
    handleVersionChange,
    loadVersionData: loadVersionDataNew, // 새로운 함수 사용
    applySearchFilter,
    setSearchFilter
  };
};
