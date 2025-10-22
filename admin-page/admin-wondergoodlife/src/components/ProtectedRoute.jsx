import { Navigate } from 'react-router-dom';

/**
 * 로그인 체크 컴포넌트
 * 토큰이 없으면 무조건 로그인 페이지로 리다이렉트
 */
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;

