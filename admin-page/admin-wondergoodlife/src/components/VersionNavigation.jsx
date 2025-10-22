/**
 * 버전 네비게이션 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import versionAPI from '../services/versionApi';
import './VersionNavigation.css';

function VersionNavigation({ onVersionSwitch }) {
  const [navigationData, setNavigationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    loadNavigationData();
  }, []);

  const loadNavigationData = async () => {
    try {
      setLoading(true);
      const response = await versionAPI.getNavigation();
      setNavigationData(response.data);
    } catch (err) {
      console.error('버전 네비게이션 로드 실패:', err);
      setError('버전 네비게이션을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleVersionSwitch = async (versionId) => {
    try {
      const response = await versionAPI.switchVersion(versionId);
      alert(response.data.message);
      setShowDropdown(false);
      loadNavigationData(); // 네비게이션 데이터 새로고침
      if (onVersionSwitch) {
        onVersionSwitch(versionId);
      }
    } catch (err) {
      alert('버전 전환에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div className="version-navigation">
        <div className="nav-loading">로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="version-navigation">
        <div className="nav-error">{error}</div>
      </div>
    );
  }

  if (!navigationData) {
    return null;
  }

  const currentVersion = navigationData.current_version;
  const availableVersions = navigationData.available_versions;

  return (
    <div className="version-navigation">
      <div className="nav-header">
        <h3>버전 관리</h3>
        <div className="server-status">
          <span className={`status-indicator ${navigationData.main_server_status}`}>
            {navigationData.main_server_status === 'connected' ? '🟢' : '🔴'}
          </span>
          <span className="status-text">
            메인서버 {navigationData.main_server_status === 'connected' ? '연결됨' : '연결 끊김'}
          </span>
        </div>
      </div>

      <div className="current-version">
        <div className="current-label">현재 버전:</div>
        {currentVersion ? (
          <div className="current-version-info">
            <span className="version-name">{currentVersion.version_name}</span>
            <span className="version-status">{currentVersion.status}</span>
          </div>
        ) : (
          <div className="no-current-version">활성 버전 없음</div>
        )}
      </div>

      <div className="version-dropdown-container">
        <button 
          className="version-dropdown-toggle"
          onClick={() => setShowDropdown(!showDropdown)}
        >
          버전 전환 ▼
        </button>
        
        {showDropdown && (
          <div className="version-dropdown">
            <div className="dropdown-header">사용 가능한 버전</div>
            {availableVersions.map(version => (
              <div 
                key={version.id}
                className={`version-item ${version.is_active ? 'active' : ''}`}
                onClick={() => handleVersionSwitch(version.id)}
              >
                <div className="version-item-header">
                  <span className="version-name">{version.version_name}</span>
                  <span className={`version-status-badge status-${version.status.toLowerCase()}`}>
                    {version.status}
                  </span>
                </div>
                <div className="version-item-details">
                  <span className="version-description">{version.description}</span>
                  <span className="version-date">
                    {new Date(version.created_at).toLocaleDateString()}
                  </span>
                </div>
                {version.is_active && (
                  <div className="active-indicator">현재 활성</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="nav-actions">
        <button 
          className="refresh-btn"
          onClick={loadNavigationData}
        >
          🔄 새로고침
        </button>
      </div>
    </div>
  );
}

export default VersionNavigation;
