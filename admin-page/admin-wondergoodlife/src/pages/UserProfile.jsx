/**
 * 사용자 프로필 페이지 (Me 페이지)
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import './UserProfile.css';

function UserProfile() {
  const [searchParams] = useSearchParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone_number: '',
    role: '',
    position: '',
    status: ''
  });

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/me/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('프로필을 불러오는데 실패했습니다.');
      }
      
      const userData = await response.json();
      setUser(userData);
      setFormData({
        username: userData.username,
        email: userData.email,
        phone_number: userData.phone_number || '',
        role: userData.role,
        position: userData.position,
        status: userData.status
      });
      
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/me/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '프로필 수정에 실패했습니다.');
      }
      
      setShowEditModal(false);
      loadUserProfile();
      alert('프로필이 성공적으로 수정되었습니다.');
    } catch (err) {
      alert('프로필 수정에 실패했습니다: ' + err.message);
    }
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

  if (loading) return <div className="loading">프로필을 불러오는 중...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!user) return <div className="error-message">사용자 정보를 찾을 수 없습니다.</div>;

  return (
    <div className="user-profile">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user.username.charAt(0).toUpperCase()}
            </div>
          </div>
          <div className="profile-info">
            <h1>{user.username}</h1>
            <p className="profile-email">{user.email}</p>
            <div className="profile-status">
              <span 
                className="status-badge"
                style={{ backgroundColor: getStatusColor(user.status) }}
              >
                {getStatusText(user.status)}
              </span>
            </div>
          </div>
          <div className="profile-actions">
            <button 
              onClick={() => setShowEditModal(true)}
              className="edit-profile-btn"
            >
              프로필 수정
            </button>
          </div>
        </div>

        <div className="profile-content">
          <div className="profile-section">
            <h2>기본 정보</h2>
            <div className="info-grid">
              <div className="info-item">
                <label>사용자명</label>
                <span>{user.username}</span>
              </div>
              <div className="info-item">
                <label>이메일</label>
                <span>{user.email}</span>
              </div>
              <div className="info-item">
                <label>전화번호</label>
                <span>{user.phone_number || '미입력'}</span>
              </div>
              <div className="info-item">
                <label>역할</label>
                <span className="role-badge">{getRoleText(user.role)}</span>
              </div>
              <div className="info-item">
                <label>직급</label>
                <span className="position-badge">{getPositionText(user.position)}</span>
              </div>
              <div className="info-item">
                <label>상태</label>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(user.status) }}
                >
                  {getStatusText(user.status)}
                </span>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h2>계정 정보</h2>
            <div className="info-grid">
              <div className="info-item">
                <label>계정 생성일</label>
                <span>{new Date(user.created_at).toLocaleDateString('ko-KR')}</span>
              </div>
              <div className="info-item">
                <label>마지막 수정일</label>
                <span>{user.updated_at ? new Date(user.updated_at).toLocaleDateString('ko-KR') : '수정 이력 없음'}</span>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h2>권한 정보</h2>
            <div className="permissions-info">
              <p>현재 계정의 권한 및 역할에 대한 정보입니다.</p>
              <div className="permission-tags">
                <span className="permission-tag role">{getRoleText(user.role)}</span>
                <span className="permission-tag position">{getPositionText(user.position)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 수정 모달 */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>프로필 수정</h3>
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

export default UserProfile;
