/**
 * 메인 DB API 서비스
 * VersionDataManagement와 동일한 구조로 통합
 */
import axios from 'axios';

// 기본 API 설정
const batchApi = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
batchApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 처리
batchApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API 캐시 관리
const apiCache = new Map();
const pendingRequests = new Map();

const mainDbAPI = {
  // ==================== 기본 조회 API ====================
  
  // 메인 DB 현황 조회
  getStatus: () => {
    return batchApi.get('/main-db/status');
  },

  // 브랜드별 상세 데이터 조회
  getBrandDetails: (brandId) => {
    return batchApi.get(`/main-db/brands/${brandId}/details`);
  },

  // ==================== CRUD API 함수들 ====================

  // 브랜드 CRUD
  createBrand: (brandData) => {
    return batchApi.post('/main-db/brands', brandData);
  },

  updateBrand: (brandId, brandData) => {
    return batchApi.put(`/main-db/brands/${brandId}`, brandData);
  },

  deleteBrand: (brandId) => {
    return batchApi.delete(`/main-db/brands/${brandId}`);
  },

  // 자동차 라인 CRUD
  createVehicleLine: (vehicleLineData) => {
    return batchApi.post('/main-db/vehicle-lines', vehicleLineData);
  },

  updateVehicleLine: (vehicleLineId, vehicleLineData) => {
    return batchApi.put(`/main-db/vehicle-lines/${vehicleLineId}`, vehicleLineData);
  },

  deleteVehicleLine: (vehicleLineId) => {
    return batchApi.delete(`/main-db/vehicle-lines/${vehicleLineId}`);
  },

  // 모델 CRUD
  createModel: (modelData) => {
    return batchApi.post('/main-db/models', modelData);
  },

  updateModel: (modelId, modelData) => {
    return batchApi.put(`/main-db/models/${modelId}`, modelData);
  },

  deleteModel: (modelId) => {
    return batchApi.delete(`/main-db/models/${modelId}`);
  },

  // 트림 CRUD
  createTrim: (trimData) => {
    return batchApi.post('/main-db/trims', trimData);
  },

  updateTrim: (trimId, trimData) => {
    return batchApi.put(`/main-db/trims/${trimId}`, trimData);
  },

  deleteTrim: (trimId) => {
    return batchApi.delete(`/main-db/trims/${trimId}`);
  },

  // 옵션 CRUD
  createOption: (optionData) => {
    return batchApi.post('/main-db/options', optionData);
  },

  updateOption: (optionId, optionData) => {
    return batchApi.put(`/main-db/options/${optionId}`, optionData);
  },

  deleteOption: (optionId) => {
    return batchApi.delete(`/main-db/options/${optionId}`);
  }
};

export default mainDbAPI;
