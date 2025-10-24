import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Layout.css';

function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
  }, []);

  const handleLogout = () => {
    if (confirm('로그아웃하시겠습니까?')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  // 사용자 역할에 따른 메뉴 필터링
  const getMenuItems = () => {
    const allMenuItems = [
      { path: '/', label: '대시보드', icon: '📊', requiredRole: null }, // 모든 사용자 접근 가능
      { path: '/versions', label: '버전 관리', icon: '📋', requiredRole: null }, // 모든 사용자 접근 가능
      { path: '/add-discount', label: '할인 정책 추가', icon: '💰', requiredRole: null }, // 모든 사용자 접근 가능
      { path: '/user-management', label: '사용자 관리', icon: '👥', requiredRole: 'ADMIN' }, // ADMIN만 접근 가능
      { path: '/permission-management', label: '권한 관리', icon: '🔑', requiredRole: 'ADMIN' }, // ADMIN만 접근 가능
    ];

    // 사용자 정보가 없으면 기본 메뉴만 표시
    if (!user) {
      return allMenuItems.filter(item => item.requiredRole === null);
    }

    // 사용자 역할에 따라 메뉴 필터링
    return allMenuItems.filter(item => {
      if (item.requiredRole === null) return true; // 모든 사용자 접근 가능
      
      // ADMIN 역할이거나 MANAGER/CEO 직급이면 모든 메뉴 접근 가능
      if (user.role === 'ADMIN' || user.position === 'MANAGER' || user.position === 'CEO') {
        return true;
      }
      
      // 일반 사용자(USER)는 사용자 관리 메뉴 접근 불가
      return false;
    });
  };

  const menuItems = getMenuItems();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>🚘 WonderGoodLife</h2>
          <p>관리자 페이지</p>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">👤</div>
            <div className="user-details">
              <p className="user-name">{user?.username || '사용자'}</p>
              <p 
                className="user-email" 
                onClick={() => navigate('/user-profile')}
                style={{ cursor: 'pointer', color: '#3b82f6' }}
              >
                {user?.email || 'user@example.com'}
              </p>
            </div>
          </div>
          <button onClick={handleLogout} className="logout-button">
            🚪 로그아웃
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;

