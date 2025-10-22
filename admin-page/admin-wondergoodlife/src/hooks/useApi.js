/**
 * API 호출을 위한 커스텀 훅
 * 에러 처리와 로딩 상태를 중앙화
 */

import { useState, useCallback } from 'react';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      if (options.onSuccess) {
        options.onSuccess(result);
      }
      
      return result;
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'API 호출 중 오류가 발생했습니다.');
      
      if (options.onError) {
        options.onError(err);
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    execute,
    clearError,
  };
};

/**
 * 특정 API 작업을 위한 훅
 */
export const useApiOperation = (apiFunction, options = {}) => {
  const api = useApi();
  
  const execute = useCallback(async (...args) => {
    return api.execute(() => apiFunction(...args), options);
  }, [api, apiFunction, options]);

  return {
    ...api,
    execute,
  };
};

export default useApi;
