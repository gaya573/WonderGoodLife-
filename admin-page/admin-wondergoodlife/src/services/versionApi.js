/**
 * Version API 서비스
 */
import { batchApi } from './api';

// API 호출 디바운싱을 위한 캐시
const apiCache = new Map();
const pendingRequests = new Map();

// Version API
export const versionAPI = {
  // 버전 목록 조회 (페이지네이션) - 디바운싱 및 중복 요청 방지
  getAll: (offset = 0, limit = 10, search = null, status = null) => {
    const params = { offset, limit };
    if (search) params.search = search;
    if (status) params.status = status;
    
    console.log('versionAPI.getAll called with params:', params);
    
    // 캐시 키 생성
    const cacheKey = `/versions/?${new URLSearchParams(params).toString()}`;
    
    // 이미 진행 중인 요청이 있으면 해당 요청 반환
    if (pendingRequests.has(cacheKey)) {
      console.log('🔄 중복 요청 방지:', cacheKey);
      return pendingRequests.get(cacheKey);
    }
    
    // 캐시된 결과가 있으면 반환 (5분간 유효)
    const cached = apiCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
      console.log('📦 캐시된 결과 사용:', cacheKey);
      return Promise.resolve(cached.data);
    }
    
    // 새로운 요청 생성
    const request = batchApi.get('/versions/', { params })
      .then(response => {
        // 성공 시 캐시에 저장
        apiCache.set(cacheKey, {
          data: response,
          timestamp: Date.now()
        });
        return response;
      })
      .finally(() => {
        // 요청 완료 후 pending에서 제거
        pendingRequests.delete(cacheKey);
      });
    
    // pending 요청에 추가
    pendingRequests.set(cacheKey, request);
    
    return request;
  },
  
  // 버전 상세 조회
  getById: (id) => batchApi.get(`/versions/${id}`),
  
  // 새 버전 생성
  create: (data) => batchApi.post('/versions/', data),
  
  // 버전 수정
  update: (id, data) => batchApi.put(`/versions/${id}`, data),
  
  // 버전 삭제
  delete: (id) => batchApi.delete(`/versions/${id}`),
  
  // 버전에 Staging 데이터 추가
  addStagingData: (id, stagingBrandIds) => batchApi.post(`/versions/${id}/add-staging-data?${stagingBrandIds.map(id => `staging_brand_ids=${id}`).join('&')}`),
  
  // 버전 승인 (Staging → 메인 DB)
  approve: (id) => batchApi.post(`/versions/${id}/approve`),
  
  // 버전 마이그레이션
  migrate: (id) => batchApi.post(`/versions/${id}/migrate`),

  // ==================== CRUD API 함수들 ====================

  // 브랜드 CRUD
  createBrand: (versionId, brandData) => {
    return batchApi.post(`/staging/brands/`, { ...brandData, version_id: versionId });
  },

  // 자동차 라인 CRUD
  createVehicleLine: (versionId, vehicleLineData) => {
    return batchApi.post(`/staging/vehicle-lines/`, vehicleLineData); // vehicleLineData should already contain brand_id
  },

  updateVehicleLine: (versionId, vehicleLineId, vehicleLineData) => {
    return batchApi.put(`/staging/vehicle-lines/${vehicleLineId}`, vehicleLineData);
  },

  deleteVehicleLine: (versionId, vehicleLineId) => {
    return batchApi.delete(`/staging/vehicle-lines/${vehicleLineId}`);
  },

  updateBrand: (versionId, brandId, brandData) => {
    return batchApi.put(`/staging/brands/${brandId}`, brandData);
  },

  deleteBrand: (versionId, brandId) => {
    return batchApi.delete(`/staging/brands/${brandId}`);
  },

  // 모델 CRUD
  createModel: (versionId, modelData) => {
    return batchApi.post(`/staging/models/`, modelData);
  },

  updateModel: (versionId, modelId, modelData) => {
    return batchApi.put(`/staging/models/${modelId}`, modelData);
  },

  deleteModel: (versionId, modelId) => {
    return batchApi.delete(`/staging/models/${modelId}`);
  },

  // 트림 CRUD
  createTrim: (versionId, trimData) => {
    return batchApi.post(`/staging/trims/`, trimData);
  },

  updateTrim: (versionId, trimId, trimData) => {
    return batchApi.put(`/staging/trims/${trimId}`, trimData);
  },

  deleteTrim: (versionId, trimId) => {
    return batchApi.delete(`/staging/trims/${trimId}`);
  },

  // 옵션 CRUD
  createOption: (versionId, optionData) => {
    return batchApi.post(`/staging/options/`, optionData);
  },

  updateOption: (versionId, optionId, optionData) => {
    return batchApi.put(`/staging/options/${optionId}`, optionData);
  },

  deleteOption: (versionId, optionId) => {
    return batchApi.delete(`/staging/options/${optionId}`);
  },
  
  // 버전별 완전한 데이터 조회 (JOIN으로 한번에, 페이지네이션 지원)
  getCompleteData: (id, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${id}/complete-data${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // 최적화된 완전한 데이터 조회 (단일 쿼리)
  getCompleteDataOptimized: (id, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${id}/complete-data-optimized${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // ===== 분할된 API 엔드포인트들 =====
  
  // 브랜드 목록만 조회
  getBrands: (id, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${id}/brands${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // 특정 브랜드의 모델 목록 조회
  getBrandModels: (versionId, brandId, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${versionId}/brands/${brandId}/models${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // 특정 모델의 트림 목록 조회
  getModelTrims: (versionId, modelId, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${versionId}/models/${modelId}/trims${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // 특정 트림의 통합된 옵션 목록 조회
  getTrimOptions: (versionId, trimId, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${versionId}/trims/${trimId}/options${queryString ? `?${queryString}` : ''}`;
    
    return batchApi.get(url);
  },

  // 브랜드별 전체 데이터 조회 (모델/트림/옵션 포함) - 디바운싱 적용
  getBrandsWithFullData: (id, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.brand_name) queryParams.append('brand_name', params.brand_name);
    if (params._t) queryParams.append('_t', params._t); // 캐시 무시를 위한 타임스탬프
    
    const queryString = queryParams.toString();
    const url = `/versions/${id}/brands-with-full-data${queryString ? `?${queryString}` : ''}`;
    
    const cacheKey = url;
    
    // 캐시 무시 옵션이 있으면 캐시를 사용하지 않음
    const ignoreCache = params._t;
    
    if (!ignoreCache && pendingRequests.has(cacheKey)) {
      console.log('🔄 중복 요청 방지 (getBrandsWithFullData):', cacheKey);
      return pendingRequests.get(cacheKey);
    }
    
    if (!ignoreCache) {
      const cached = apiCache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < 2 * 60 * 1000) {
        console.log('📦 캐시된 결과 사용 (getBrandsWithFullData):', cacheKey);
        return Promise.resolve(cached.data);
      }
    }
    
    const request = batchApi.get(url)
      .then(response => {
        // 캐시 무시 옵션이 없을 때만 캐시에 저장
        if (!ignoreCache) {
          apiCache.set(cacheKey, {
            data: response,
            timestamp: Date.now()
          });
        }
        return response;
      })
      .finally(() => {
        pendingRequests.delete(cacheKey);
      });
    
    pendingRequests.set(cacheKey, request);
    
    return request;
  },

  // 자동차 라인별 전체 데이터 조회 (무한스크롤용 - 각 자동차 라인의 모든 브랜드/모델/트림/옵션 포함) - 디바운싱 적용
  getVehicleLinesWithFullData: (id, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const queryString = queryParams.toString();
    const url = `/versions/${id}/vehicle-lines-with-full-data${queryString ? `?${queryString}` : ''}`;
    
    // 캐시 키 생성
    const cacheKey = url;
    
    // 이미 진행 중인 요청이 있으면 해당 요청 반환
    if (pendingRequests.has(cacheKey)) {
      console.log('🔄 중복 요청 방지 (getVehicleLinesWithFullData):', cacheKey);
      return pendingRequests.get(cacheKey);
    }
    
    // 캐시된 결과가 있으면 반환 (2분간 유효 - 무한스크롤이므로 짧게)
    const cached = apiCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < 2 * 60 * 1000) {
      console.log('📦 캐시된 결과 사용 (getVehicleLinesWithFullData):', cacheKey);
      return Promise.resolve(cached.data);
    }
    
    // 새로운 요청 생성
    const request = batchApi.get(url)
      .then(response => {
        // 성공 시 캐시에 저장
        apiCache.set(cacheKey, {
          data: response,
          timestamp: Date.now()
        });
        return response;
      })
      .finally(() => {
        // 요청 완료 후 pending에서 제거
        pendingRequests.delete(cacheKey);
      });
    
    // pending 요청에 추가
    pendingRequests.set(cacheKey, request);
    
    return request;
  },

  // 데이터베이스 전체 검색 (간단한 버전)
  searchData: (versionId, query, searchType = 'all', limit = 20) => {
    // 새로운 간단한 검색 API 사용
    const url = `/versions/${versionId}/simple-search?query=${encodeURIComponent(query)}&limit=${limit}`;
    
    console.log('🔍 간단한 검색 API 호출 URL:', url);
    console.log('🔍 검색 쿼리:', query);
    
    return batchApi.get(url);
  },

  // 디버그용 데이터 조회
  getDebugData: (versionId) => {
    return batchApi.get(`/versions/${versionId}/debug-data`);
  },

  // 전체 데이터 요약 통계 조회
  getAllDataSummary: (versionId) => {
    return batchApi.get(`/versions/${versionId}/all-data-summary`);
  },

  // 검색 결과에 따른 필터링된 데이터 조회 (파라미터 분리)
  getFilteredData: (versionId, filters) => {
    const queryParams = new URLSearchParams();
    
    if (filters.brand) queryParams.append('brand', filters.brand);
    if (filters.model) queryParams.append('model', filters.model);
    if (filters.trim) queryParams.append('trim', filters.trim);
    
    const queryString = queryParams.toString();
    const url = `/versions/${versionId}/filtered-data?${queryString}`;
    
    console.log('🔍 필터링 API 호출:', url);
    return batchApi.get(url);
  },

  // 메인 DB에서 데이터 다운로드
  downloadFromMain: (versionId) => {
    return batchApi.post(`/versions/${versionId}/download-from-main`);
  },

  // 메인 DB로 데이터 업로드
  uploadToMain: (versionId) => {
    return batchApi.post(`/versions/${versionId}/upload-to-main`);
  },

  // 버전 승인/거부
  approveVersion: (versionId) => {
    return batchApi.post(`/versions/${versionId}/approve`);
  },

  rejectVersion: (versionId, reason) => {
    return batchApi.post(`/versions/${versionId}/reject`, { reason });
  },
};

// Staging CRUD API
export const stagingAPI = {
  // 브랜드 CRUD
  brands: {
    getAll: (params) => batchApi.get('/staging/brands/', { params }),
    getById: (id) => batchApi.get(`/staging/brands/${id}`),
    create: (data) => batchApi.post('/staging/brands/', data),
    update: (id, data) => batchApi.put(`/staging/brands/${id}`, data),
    delete: (id) => batchApi.delete(`/staging/brands/${id}`)
  },
  
  // 차량라인 CRUD
  vehicleLines: {
    getAll: (params) => batchApi.get('/staging/vehicle-lines/', { params }),
    getById: (id) => batchApi.get(`/staging/vehicle-lines/${id}`),
    create: (data) => batchApi.post('/staging/vehicle-lines/', data),
    update: (id, data) => batchApi.put(`/staging/vehicle-lines/${id}`, data),
    delete: (id) => batchApi.delete(`/staging/vehicle-lines/${id}`)
  },
  
  // 모델 CRUD
  models: {
    getAll: (params) => batchApi.get('/staging/models/', { params }),
    getById: (id) => batchApi.get(`/staging/models/${id}`),
    create: (data) => batchApi.post('/staging/models/', data),
    update: (id, data) => batchApi.put(`/staging/models/${id}`, data),
    delete: (id) => batchApi.delete(`/staging/models/${id}`)
  },
  
  // 트림 CRUD
  trims: {
    getAll: (params) => batchApi.get('/staging/trims/', { params }),
    getById: (id) => batchApi.get(`/staging/trims/${id}`),
    create: (data) => batchApi.post('/staging/trims/', data),
    update: (id, data) => batchApi.put(`/staging/trims/${id}`, data),
    delete: (id) => batchApi.delete(`/staging/trims/${id}`)
  },
  
  // 옵션 CRUD
  options: {
    getAll: (params) => batchApi.get('/staging/options/', { params }),
    getById: (id) => batchApi.get(`/staging/options/${id}`),
    create: (data) => batchApi.post('/staging/options/', data),
    update: (id, data) => batchApi.put(`/staging/options/${id}`, data),
    delete: (id) => batchApi.delete(`/staging/options/${id}`)
  },

  // 전체 시스템 통계 조회 (모든 버전의 데이터)
  getTotalStatistics: () => {
    return batchApi.get('/staging/summary/');
  },

  // ==================== CRUD API 함수들 ====================

  // 브랜드 CRUD
  createBrand: (versionId, brandData) => {
    return batchApi.post(`/versions/${versionId}/brands`, brandData);
  },

  updateBrand: (versionId, brandId, brandData) => {
    return batchApi.put(`/versions/${versionId}/brands/${brandId}`, brandData);
  },

  deleteBrand: (versionId, brandId) => {
    return batchApi.delete(`/versions/${versionId}/brands/${brandId}`);
  },

  // 모델 CRUD
  createModel: (versionId, modelData) => {
    return batchApi.post(`/versions/${versionId}/models`, modelData);
  },

  updateModel: (versionId, modelId, modelData) => {
    return batchApi.put(`/versions/${versionId}/models/${modelId}`, modelData);
  },

  deleteModel: (versionId, modelId) => {
    return batchApi.delete(`/versions/${versionId}/models/${modelId}`);
  },

  // 트림 CRUD
  createTrim: (versionId, trimData) => {
    return batchApi.post(`/versions/${versionId}/trims`, trimData);
  },

  updateTrim: (versionId, trimId, trimData) => {
    return batchApi.put(`/versions/${versionId}/trims/${trimId}`, trimData);
  },

  deleteTrim: (versionId, trimId) => {
    return batchApi.delete(`/versions/${versionId}/trims/${trimId}`);
  },

  // 옵션 CRUD
  createOption: (versionId, optionData) => {
    return batchApi.post(`/versions/${versionId}/options`, optionData);
  },

  updateOption: (versionId, optionId, optionData) => {
    return batchApi.put(`/versions/${versionId}/options/${optionId}`, optionData);
  },

  deleteOption: (versionId, optionId) => {
    return batchApi.delete(`/versions/${versionId}/options/${optionId}`);
  },

  // 메인서버 업로드/다운로드
  uploadToMain: (versionId) => {
    return batchApi.post(`/versions/${versionId}/upload-to-main`);
  },

  downloadFromMain: (versionId) => {
    return batchApi.post(`/versions/${versionId}/download-from-main`);
  },

  // 버전 네비게이션
  getNavigation: () => {
    return batchApi.get('/versions/navigation');
  },

  switchVersion: (versionId) => {
    return batchApi.post(`/versions/switch-version/${versionId}`);
  }
};


export default versionAPI;
