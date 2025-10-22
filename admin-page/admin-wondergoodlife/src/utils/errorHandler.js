/**
 * 간단한 에러 처리 유틸리티
 */

export const logError = (error, context = '') => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[ERROR] ${context}:`, error);
  }
};

export const normalizeApiError = (error) => {
  if (!error.response) {
    return new Error('네트워크 연결을 확인해주세요.');
  }

  const { status, data } = error.response;
  const message = data?.detail || data?.message || '서버 오류가 발생했습니다.';

  return new Error(message);
};

export const getUserFriendlyMessage = (error) => {
  if (typeof error === 'string') {
    return error;
  }
  
  return error?.message || '알 수 없는 오류가 발생했습니다.';
};