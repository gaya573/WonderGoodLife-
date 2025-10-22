import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './PermissionManagement.css';

function PermissionManagement() {
  const [permissions, setPermissions] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreatePermissionModal, setShowCreatePermissionModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  // 권한 매트릭스 상태
  const [permissionMatrix, setPermissionMatrix] = useState({});

  const [permissionFormData, setPermissionFormData] = useState({
    resource: '',
    action: '',
    description: ''
  });

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // 현재 사용자 정보 로드
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setCurrentUser(JSON.parse(userStr));
    }
  }, []);

  useEffect(() => {
    const userId = searchParams.get('user_id');
    if (userId) {
      loadUserInfo(userId);
    }
    loadPermissionData();
  }, [searchParams]);

  const loadUserInfo = async (userId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('사용자 정보를 불러오는데 실패했습니다.');
      }

      const userData = await response.json();
      setSelectedUser(userData);
    } catch (err) {
      console.error('사용자 정보 로드 실패:', err);
    }
  };

  const loadPermissionData = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      // 권한 매트릭스 조회
      const response = await fetch('http://localhost:8000/api/permissions/matrix', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('권한 데이터를 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      setRoles(data.roles);
      setPermissions(data.permissions);
      setPermissionMatrix(data.matrix);
    } catch (err) {
      setError('권한 데이터를 불러오는데 실패했습니다: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePermissionChange = async (roleId, permissionId, checked) => {
    try {
      // 사용자 관리 권한을 일반 사용자(USER) 역할에 할당하려는 경우 제한
      const permission = permissions.find(p => p.id === permissionId);
      const role = roles.find(r => r.id === roleId);
      
      if (permission && permission.resource === 'user_management' && 
          role && role.name === 'USER' && checked) {
        alert('일반 사용자(USER)에게는 사용자 관리 권한을 할당할 수 없습니다.');
        return;
      }

      const token = localStorage.getItem('access_token');
      const url = checked ? 
        'http://localhost:8000/api/permissions/matrix/assign' : 
        'http://localhost:8000/api/permissions/matrix/revoke';
      
      const response = await fetch(url, {
        method: checked ? 'POST' : 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          role_id: roleId,
          permission_id: permissionId
        })
      });

      if (!response.ok) {
        throw new Error(checked ? '권한 할당에 실패했습니다.' : '권한 제거에 실패했습니다.');
      }

      // 로컬 상태 업데이트
      setPermissionMatrix(prev => ({
        ...prev,
        [roleId]: {
          ...prev[roleId],
          [permissionId]: checked
        }
      }));
    } catch (err) {
      alert(err.message);
    }
  };


  const handleCreatePermission = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/permissions/permissions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(permissionFormData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '권한 생성에 실패했습니다.');
      }

      const result = await response.json();
      alert(result.message);
      setShowCreatePermissionModal(false);
      setPermissionFormData({ resource: '', action: '', description: '' });
      loadPermissionData(); // 데이터 새로고침
    } catch (err) {
      alert('권한 생성 실패: ' + err.message);
    }
  };

  const handleDeletePermission = async (permissionId) => {
    if (!window.confirm('이 권한을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/permissions/permissions/${permissionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '권한 삭제에 실패했습니다.');
      }

      const result = await response.json();
      alert(result.message);
      loadPermissionData(); // 데이터 새로고침
    } catch (err) {
      alert('권한 삭제 실패: ' + err.message);
    }
  };

  const getResourceName = (resource) => {
    const resourceNames = {
      'main_carsystem': '메인 자동차 시스템',
      'demo_carsystem': '데모 자동차 시스템',
      'staging_data': 'Staging 데이터',
      'user_management': '사용자 관리',
      'user_role': '사용자 권한 관리',
      'system_admin': '시스템 관리',
      'event_data': '이벤트 데이터'
    };
    return resourceNames[resource] || resource;
  };

  const getActionName = (action) => {
    const actionNames = {
      'read': '조회',
      'write': '생성/수정',
      'delete': '삭제',
      'cdc': '마이그레이션',
      'admin': '관리'
    };
    return actionNames[action] || action;
  };

  const getRoleName = (role) => {
    const roleNames = {
      'ADMIN': '관리자',
      'USER': '일반 사용자',
      'MANAGER': '부장',
      'CEO': '대표'
    };
    return roleNames[role] || role;
  };

  if (loading) return <div className="loading">권한 데이터를 불러오는 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="permission-management">
      <div className="header-section">
        <div className="header-content">
          <div>
            <h1>권한 관리</h1>
            <p>역할별 권한 설정 및 관리</p>
            {selectedUser && (
              <div className="selected-user-info">
                <span className="user-label">선택된 사용자:</span>
                <span className="user-name">{selectedUser.username}</span>
                <span className="user-email">({selectedUser.email})</span>
                <button 
                  onClick={() => {
                    setSelectedUser(null);
                    navigate('/permission-management');
                  }}
                  className="clear-user-btn"
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        
        </div>
      </div>

      <div className="permission-matrix-container">
        <div className="permission-matrix-header">
          <h2>권한 매트릭스</h2>
          <p>각 역할에 대한 권한을 설정하세요</p>
        </div>

        <div className="permission-table-container">
          <table className="permission-table">
            <thead>
              <tr>
                <th className="resource-column">리소스</th>
                <th className="action-column">액션</th>
                <th className="description-column">설명</th>
                {roles.map(role => (
                  <th key={role.id} className="role-column">
                    <div className="role-header">
                      <span className="role-name">{getRoleName(role.name)}</span>
                      <span className={`role-badge ${role.is_system_role ? 'system' : 'custom'}`}>
                        {role.is_system_role ? '시스템' : '사용자'}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {permissions.map(permission => (
                <tr key={permission.id} className="permission-row">
                  <td className="resource-cell">
                    <span className="resource-name">{getResourceName(permission.resource)}</span>
                  </td>
                  <td className="action-cell">
                    <span className="action-name">{getActionName(permission.action)}</span>
                  </td>
                  <td className="description-cell">
                    <span className="description-text">{permission.description}</span>
                    <button 
                      onClick={() => handleDeletePermission(permission.id)}
                      className="delete-permission-btn"
                    >
                      삭제
                    </button>
                  </td>
                  {roles.map(role => (
                    <td key={role.id} className="permission-cell">
                      <label className="permission-checkbox">
                        <input
                          type="checkbox"
                          checked={permissionMatrix[role.id]?.[permission.id] || false}
                          onChange={(e) => handlePermissionChange(role.id, permission.id, e.target.checked)}
                          disabled={
                            role.is_system_role && role.name === 'ADMIN' || // 관리자 권한은 수정 불가
                            (permission.resource === 'user_management' && role.name === 'USER') // 일반 사용자에게 사용자 관리 권한 할당 불가
                          }
                        />
                        <span className="checkmark"></span>
                      </label>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="permission-summary">
          <h3>권한 요약</h3>
          <div className="summary-grid">
            {roles.map(role => {
              const rolePermissions = permissions.filter(permission => 
                permissionMatrix[role.id]?.[permission.id]
              );
              return (
                <div key={role.id} className="summary-card">
                  <div className="summary-header">
                    <h4>{getRoleName(role.name)}</h4>
                    <span className={`role-badge ${role.is_system_role ? 'system' : 'custom'}`}>
                      {role.is_system_role ? '시스템' : '사용자'}
                    </span>
                  </div>
                  <div className="summary-content">
                    <p className="permission-count">
                      총 {rolePermissions.length}개 권한
                    </p>
                    <div className="permission-list">
                      {rolePermissions.map(permission => (
                        <span key={permission.id} className="permission-tag">
                          {getResourceName(permission.resource)} - {getActionName(permission.action)}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 권한 생성 모달 */}
      {showCreatePermissionModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>새 권한 추가</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleCreatePermission(); }}>
              <div className="form-group">
                <label>리소스 *</label>
                <select
                  value={permissionFormData.resource}
                  onChange={(e) => setPermissionFormData({...permissionFormData, resource: e.target.value})}
                  required
                >
                  <option value="">리소스 선택</option>
                  <option value="main_carsystem">메인 자동차 시스템</option>
                  <option value="demo_carsystem">데모 자동차 시스템</option>
                  <option value="staging_data">Staging 데이터</option>
                  <option value="user_management">사용자 관리</option>
                  <option value="user_role">사용자 권한 관리</option>
                  <option value="system_admin">시스템 관리</option>
                  <option value="event_data">이벤트 데이터</option>
                </select>
              </div>
              <div className="form-group">
                <label>액션 *</label>
                <select
                  value={permissionFormData.action}
                  onChange={(e) => setPermissionFormData({...permissionFormData, action: e.target.value})}
                  required
                >
                  <option value="">액션 선택</option>
                  <option value="read">조회</option>
                  <option value="write">생성/수정</option>
                  <option value="delete">삭제</option>
                  <option value="cdc">마이그레이션</option>
                  <option value="admin">관리</option>
                </select>
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea
                  value={permissionFormData.description}
                  onChange={(e) => setPermissionFormData({...permissionFormData, description: e.target.value})}
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button type="submit" className="confirm-btn">추가</button>
                <button 
                  type="button" 
                  onClick={() => {
                    setShowCreatePermissionModal(false);
                    setPermissionFormData({ resource: '', action: '', description: '' });
                  }} 
                  className="cancel-btn"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default PermissionManagement;