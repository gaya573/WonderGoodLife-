import axios from 'axios';

// FastAPI (배치 서비스) - Staging 데이터
const BATCH_API_URL = 'http://localhost:8000/api';

// Spring Boot (CRUD 서비스) - Main 데이터
const CRUD_API_URL = 'http://localhost:8080/api';

const batchApi = axios.create({
  baseURL: BATCH_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const crudApi = axios.create({
  baseURL: CRUD_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== 토큰 인터셉터 설정 =====

// 요청 인터셉터: 모든 요청에 토큰 자동 추가
batchApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // 토큰 만료 확인
    
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

crudApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // 토큰 만료 확인
     
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 로그인 페이지로 리다이렉트
batchApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

crudApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ===== 배치 작업 API (FastAPI) =====

// 엑셀 비동기 업로드
export const uploadExcelAsync = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${BATCH_API_URL}/jobs/excel/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// 작업 상태 조회
export const getJobStatus = async (jobId) => {
  const response = await batchApi.get(`/jobs/${jobId}`);
  return response.data;
};

// 작업 목록 조회
export const getJobs = async (params) => {
  const response = await batchApi.get('/jobs/', { params });
  return response.data;
};

// ===== Staging CRUD API (FastAPI) =====

// Staging 브랜드
export const stagingBrandAPI = {
  getAll: (params) => batchApi.get('/staging/brands/', { params }),
  getById: (id) => batchApi.get(`/staging/brands/${id}`),
  create: (data) => batchApi.post('/staging/brands/', data),
  update: (id, data) => batchApi.put(`/staging/brands/${id}`, data),
  delete: (id) => batchApi.delete(`/staging/brands/${id}`),
  approve: (id, approvedBy) => batchApi.post(`/staging/brands/${id}/approve`, { approved_by: approvedBy }),
  reject: (id, approvedBy, reason) => batchApi.post(`/staging/brands/${id}/reject`, { 
    approved_by: approvedBy,
    rejection_reason: reason 
  }),
};

// Staging 모델
export const stagingModelAPI = {
  getAll: (params) => batchApi.get('/staging/models/', { params }),
  create: (data) => batchApi.post('/staging/models/', data),
  update: (id, data) => batchApi.put(`/staging/models/${id}`, data),
  approve: (id, approvedBy) => batchApi.post(`/staging/models/${id}/approve`, { approved_by: approvedBy }),
};

// Staging 트림
export const stagingTrimAPI = {
  getAll: (params) => batchApi.get('/staging/trims/', { params }),
  create: (data) => batchApi.post('/staging/trims/', data),
  update: (id, data) => batchApi.put(`/staging/trims/${id}`, data),
  approve: (id, approvedBy) => batchApi.post(`/staging/trims/${id}/approve`, { approved_by: approvedBy }),
};

// Staging 옵션 타이틀
export const stagingOptionTitleAPI = {
  getAll: (params) => batchApi.get('/staging/option-titles', { params }),
  create: (data) => batchApi.post('/staging/option-titles', data),
  update: (id, data) => batchApi.put(`/staging/option-titles/${id}`, data),
};

// Staging 옵션 가격
export const stagingOptionPriceAPI = {
  getAll: (params) => batchApi.get('/staging/option-prices', { params }),
  create: (data) => batchApi.post('/staging/option-prices', data),
  update: (id, data) => batchApi.put(`/staging/option-prices/${id}`, data),
};

// 통합된 옵션 API
export const stagingOptionAPI = {
  getAll: (params) => batchApi.get('/staging/options/', { params }),
  getById: (id) => batchApi.get(`/staging/options/${id}`),
  create: (data) => batchApi.post('/staging/options/', data),
  update: (id, data) => batchApi.put(`/staging/options/${id}`, data),
  delete: (id) => batchApi.delete(`/staging/options/${id}`),
};

// 일괄 승인
export const approveAll = async (approvedBy) => {
  const response = await batchApi.post('/staging/approve-all', { approved_by: approvedBy });
  return response.data;
};

// ===== Main 데이터 API (Spring Boot) =====

// 브랜드 API
export const brandAPI = {
  getAll: () => crudApi.get('/brands'),
  getById: (id) => crudApi.get(`/brands/${id}`),
  create: (data) => crudApi.post('/brands', data),
  update: (id, data) => crudApi.put(`/brands/${id}`, data),
  delete: (id) => crudApi.delete(`/brands/${id}`),
};

// 모델 API
export const modelAPI = {
  getAll: () => crudApi.get('/models'),
  getById: (id) => crudApi.get(`/models/${id}`),
  create: (data) => crudApi.post('/models', data),
  update: (id, data) => crudApi.put(`/models/${id}`, data),
  delete: (id) => crudApi.delete(`/models/${id}`),
};

// 트림 API
export const trimAPI = {
  getAll: (params) => crudApi.get('/trims', { params }),
  getById: (id) => crudApi.get(`/trims/${id}`),
  create: (data) => crudApi.post('/trims', data),
  update: (id, data) => crudApi.put(`/trims/${id}`, data),
  delete: (id) => crudApi.delete(`/trims/${id}`),
};

// 색상 API
export const colorAPI = {
  getAll: (params) => crudApi.get('/colors', { params }),
  getById: (id) => crudApi.get(`/colors/${id}`),
  create: (data) => crudApi.post('/colors', data),
  update: (id, data) => crudApi.put(`/colors/${id}`, data),
  delete: (id) => crudApi.delete(`/colors/${id}`),
};

// 옵션 API (기존 방식)
export const optionAPI = {
  getTitles: (params) => crudApi.get('/options/titles', { params }),
  getPrices: (params) => crudApi.get('/options/prices', { params }),
  createTitle: (data) => crudApi.post('/options/titles', data),
  createPrice: (data) => crudApi.post('/options/prices', data),
  updateTitle: (id, data) => crudApi.put(`/options/titles/${id}`, data),
  updatePrice: (id, data) => crudApi.put(`/options/prices/${id}`, data),
  deleteTitle: (id) => crudApi.delete(`/options/titles/${id}`),
  deletePrice: (id) => crudApi.delete(`/options/prices/${id}`),
};

// 통합 옵션 API (새로운 방식)
export const unifiedOptionAPI = {
  getByTrim: (versionId, trimId, params) => crudApi.get(`/versions/${versionId}/trims/${trimId}/options-simple`, { params }),
  create: (data) => crudApi.post('/options', data),
  update: (id, data) => crudApi.put(`/options/${id}`, data),
  delete: (id) => crudApi.delete(`/options/${id}`),
};

export { batchApi, crudApi };
export default { batchApi, crudApi };

