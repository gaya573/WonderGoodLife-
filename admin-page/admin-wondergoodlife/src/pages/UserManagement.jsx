/**
 * 사용자 관리 페이지 - 사용자 CRUD 및 권한 관리
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserManagement.css';

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // 필터 및 검색 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // 폼 데이터
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone_number: '',
    role: 'USER',
    position: 'EMPLOYEE',
    status: 'ACTIVE'
  });
  
  const navigate = useNavigate();
  const searchInputRef = useRef(null); // 검색 입력 필드 참조

  // 초기 로드
  useEffect(() => {
    loadUsers();
  }, []);

  // 검색 디바운싱을 위한 useEffect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadUsers();
    }, 300); // 300ms 디바운싱

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // 필터 변경시 즉시 로드
  useEffect(() => {
    loadUsers();
  }, [roleFilter, statusFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (roleFilter) params.append('role', roleFilter);
      if (statusFilter) params.append('status', statusFilter);
      
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/users/?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('사용자 목록을 불러오는데 실패했습니다.');
      }
      
      const data = await response.json();
      setUsers(data.items || []);
      
    } catch (err) {
      console.error('Failed to load users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      // 검색 완료 후 포커스 유지
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }
  };

  const handleCreate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '사용자 생성에 실패했습니다.');
      }
      
      setShowCreateModal(false);
      setFormData({
        username: '',
        email: '',
        password: '',
        phone_number: '',
        role: 'USER',
        position: 'EMPLOYEE',
        status: 'ACTIVE'
      });
      loadUsers();
      alert('사용자가 성공적으로 생성되었습니다.');
    } catch (err) {
      alert('사용자 생성에 실패했습니다: ' + err.message);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // 비밀번호는 수정 시 빈 값으로 시작
      phone_number: user.phone_number || '',
      role: user.role,
      position: user.position,
      status: user.status
    });
    setShowEditModal(true);
  };

  const handleUpdate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const updateData = { ...formData };
      
      // 비밀번호가 비어있으면 제외, 입력되었으면 포함
      if (!updateData.password || updateData.password.trim() === '') {
        delete updateData.password;
      }
      
      const response = await fetch(`http://localhost:8000/api/users/${editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '사용자 수정에 실패했습니다.');
      }
      
      setShowEditModal(false);
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        password: '',
        phone_number: '',
        role: 'USER',
        position: 'EMPLOYEE',
        status: 'ACTIVE'
      });
      loadUsers();
      alert('사용자가 성공적으로 수정되었습니다.');
    } catch (err) {
      alert('사용자 수정에 실패했습니다: ' + err.message);
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '사용자 삭제에 실패했습니다.');
        }
        
        loadUsers();
        alert('사용자가 성공적으로 삭제되었습니다.');
      } catch (err) {
        alert('사용자 삭제에 실패했습니다: ' + err.message);
      }
    }
  };


  const handleEmailClick = (email) => {
    // 이메일 클릭 시 사용자 프로필 페이지로 이동
    navigate(`/user-profile?email=${encodeURIComponent(email)}`);
  };

  const getRoleText = (role) => {
    switch (role) {
      case 'ADMIN': return '관리자';
      case 'USER': return '사용자';
      default: return role;
    }
  };

  const getPositionText = (position) => {
    switch (position) {
      case 'CEO': return '대표관리';
      case 'MANAGER': return '부장관리';
      case 'EMPLOYEE': return '사원';
      default: return position;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ACTIVE': return '활성';
      case 'INACTIVE': return '비활성';
      case 'SUSPENDED': return '정지';
      default: return status;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return '#10b981';
      case 'INACTIVE': return '#6b7280';
      case 'SUSPENDED': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) return <div className="loading">로딩 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="user-management">
      <div className="header-section">
        <div className="header-content">
          <div>
            <h1>사용자 관리</h1>
            <p>시스템 사용자 및 권한 관리</p>
          </div>
          <div className="header-controls">
            {/* 검색창 */}
            <div className="search-container">
              <div className="search-input-wrapper">
                <div className="search-icon">🔍</div>
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="사용자명 또는 이메일로 검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
                {searchQuery && (
                  <button 
                    onClick={() => setSearchQuery('')}
                    className="search-clear"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
            
            {/* 필터 */}
            <select 
              value={roleFilter} 
              onChange={(e) => setRoleFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">전체 역할</option>
              <option value="ADMIN">관리자</option>
              <option value="USER">사용자</option>
            </select>
            
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">전체 상태</option>
              <option value="ACTIVE">활성</option>
              <option value="INACTIVE">비활성</option>
              <option value="SUSPENDED">정지</option>
            </select>
            
            <button 
              onClick={() => setShowCreateModal(true)}
              className="create-btn"
            >
              새 사용자 생성
            </button>
          </div>
        </div>
      </div>

      {users.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">👥</div>
          <p>사용자 데이터가 없습니다.</p>
        </div>
      ) : (
        <div className="user-table-container">
          <table className="user-table">
            <thead>
              <tr>
                <th>사용자명</th>
                <th>이메일</th>
                <th>역할</th>
                <th>직급</th>
                <th>상태</th>
                <th>전화번호</th>
                <th>가입일</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} className="user-row">
                  <td className="user-name-cell">
                    <span className="user-name">{user.username}</span>
                  </td>
                  <td className="user-email-cell">
                    <span 
                      className="user-email clickable"
                      onClick={() => handleEmailClick(user.email)}
                    >
                      {user.email}
                    </span>
                  </td>
                  <td className="user-role-cell">
                    <span className={`role-badge role-${user.role.toLowerCase()}`}>
                      {getRoleText(user.role)}
                    </span>
                  </td>
                  <td className="user-position-cell">
                    <span className={`position-badge position-${user.position.toLowerCase()}`}>
                      {getPositionText(user.position)}
                    </span>
                  </td>
                  <td className="user-status-cell">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(user.status) }}
                    >
                      {getStatusText(user.status)}
                    </span>
                  </td>
                  <td className="user-phone-cell">
                    {user.phone_number || 'N/A'}
                  </td>
                  <td className="user-date-cell">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="user-actions-cell">
                    <div className="action-buttons">
                      <button 
                        onClick={() => handleEdit(user)}
                        className="edit-btn"
                      >
                        수정
                      </button>
                      <button 
                        onClick={() => handleDelete(user.id)}
                        className="delete-btn"
                      >
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 생성 모달 */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>새 사용자 생성</h3>
            <form onSubmit={(e) => { e.preventDefault(); handleCreate(); }}>
              <div className="form-group">
                <label>사용자명 *</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>이메일 *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>비밀번호 *</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>전화번호</label>
                <input
                  type="text"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>역할</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="USER">사용자</option>
                  <option value="ADMIN">관리자</option>
                </select>
              </div>
              <div className="form-group">
                <label>직급</label>
                <select
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                >
                  <option value="EMPLOYEE">사원</option>
                  <option value="MANAGER">부장관리</option>
                  <option value="CEO">대표관리</option>
                </select>
              </div>
              <div className="form-group">
                <label>상태</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                >
                  <option value="ACTIVE">활성</option>
                  <option value="INACTIVE">비활성</option>
                  <option value="SUSPENDED">정지</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="submit" className="confirm-btn">생성</button>
                <button 
                  type="button" 
                  onClick={() => setShowCreateModal(false)} 
                  className="cancel-btn"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 수정 모달 */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>사용자 수정</h3>
            <form onSubmit={(e) => { e.preventDefault(); handleUpdate(); }}>
              <div className="form-group">
                <label>사용자명 *</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>이메일 *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>비밀번호 (변경 시에만 입력)</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="변경하지 않으려면 비워두세요"
                />
              </div>
              <div className="form-group">
                <label>전화번호</label>
                <input
                  type="text"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>역할</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="USER">사용자</option>
                  <option value="ADMIN">관리자</option>
                </select>
              </div>
              <div className="form-group">
                <label>직급</label>
                <select
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                >
                  <option value="EMPLOYEE">사원</option>
                  <option value="MANAGER">부장관리</option>
                  <option value="CEO">대표관리</option>
                </select>
              </div>
              <div className="form-group">
                <label>상태</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                >
                  <option value="ACTIVE">활성</option>
                  <option value="INACTIVE">비활성</option>
                  <option value="SUSPENDED">정지</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="submit" className="confirm-btn">수정</button>
                <button 
                  type="button" 
                  onClick={() => setShowEditModal(false)} 
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

export default UserManagement;
