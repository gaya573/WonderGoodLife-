/**
 * 승인 대기 목록 페이지 - 테이블 형태로 승인 대기 버전들을 관리
 */
import React, { useState, useEffect } from 'react';
import versionAPI from '../services/versionApi';
import { useNavigate } from 'react-router-dom';
import './ApprovalList.css';

function ApprovalList() {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    // 사용자 정보 로드
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      try {
        setCurrentUser(JSON.parse(userInfo));
      } catch (e) {
        console.error('사용자 정보 파싱 오류:', e);
      }
    }
    
    loadPendingVersions(true); // 초기 로드
    
    // 30초마다 데이터 새로고침 (Dashboard 로직 활용)
    const interval = setInterval(() => {
      loadPendingVersions(false); // 백그라운드 새로고침
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadPendingVersions = async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      }
      setError(null);
      
      // 승인 대기 상태의 버전만 로드
      const response = await versionAPI.getAll(0, 100, null, 'PENDING');
      const pendingVersions = response.data.items || [];
      
      // 간단한 데이터 개수 계산 (API에서 직접 가져오기)
      const versionsWithCounts = pendingVersions.map(version => ({
        ...version,
        brands_count: version.brands_count || version.total_brands || 0,
        models_count: version.models_count || version.total_models || 0,
        trims_count: version.trims_count || version.total_trims || 0,
        options_count: version.options_count || version.total_options || 0
      }));
      
      setVersions(versionsWithCounts);
    } catch (err) {
      console.error('승인 대기 목록 로드 실패:', err);
      setError('승인 대기 목록을 불러오는데 실패했습니다.');
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      }
    }
  };

  // 승인 권한 체크 함수
  const canApprove = () => {
    if (!currentUser) return false;
    const userRole = currentUser.role;
    const userPosition = currentUser.position;
    return userRole === 'ADMIN' || userPosition === 'MANAGER' || userPosition === 'CEO';
  };

  const handleApproveVersion = async (version) => {
    if (!canApprove()) {
      alert('승인 권한이 없습니다. 관리자, 매니저, 대표만 승인할 수 있습니다.');
      return;
    }

    if (!window.confirm(`버전 '${version.version_name}'을 승인하시겠습니까?\n\n승인 시 기존 메인 DB 데이터가 완전히 삭제되고 새로운 데이터로 덮어쓰여집니다.`)) {
      return;
    }

    try {
      const response = await versionAPI.approveVersion(version.id);
      alert(response.data.message);
      loadPendingVersions(true); // 목록 새로고침
    } catch (err) {
      alert('버전 승인에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRejectVersion = async (version) => {
    if (!canApprove()) {
      alert('거부 권한이 없습니다. 관리자, 매니저, 대표만 거부할 수 있습니다.');
      return;
    }

    const reason = prompt(`버전 '${version.version_name}'을 거부하시겠습니까?\n\n거부 사유를 입력해주세요:`, '');
    if (reason === null) return; // 취소
    
    if (!reason.trim()) {
      alert('거부 사유를 입력해주세요.');
      return;
    }
    
    try {
      const response = await versionAPI.rejectVersion(version.id, reason);
      alert(response.data.message);
      loadPendingVersions(true); // 목록 새로고침
    } catch (err) {
      alert('버전 거부에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleEditVersion = (version) => {
    navigate(`/versions/${version.id}`);
  };

  const handleDeleteVersion = async (version) => {
    if (!window.confirm(`버전 '${version.version_name}'을 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }

    try {
      await versionAPI.delete(version.id);
      alert('버전이 삭제되었습니다.');
      loadPendingVersions(true); // 목록 새로고침
    } catch (err) {
      alert('버전 삭제에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Dashboard 로직 활용한 상태 표시
  const getVersionStatusColor = (status) => {
    switch (status) {
      case 'PENDING': return '#f59e0b'; // 주황
      case 'APPROVED': return '#10b981'; // 초록
      case 'REJECTED': return '#ef4444'; // 빨강
      case 'MIGRATED': return '#3b82f6'; // 파랑
      default: return '#6b7280'; // 회색
    }
  };

  const getVersionStatusText = (status) => {
    switch (status) {
      case 'PENDING': return '승인 대기';
      case 'APPROVED': return '승인됨';
      case 'REJECTED': return '거부됨';
      case 'MIGRATED': return '이전됨';
      default: return status;
    }
  };

  const getStatusBadge = (status) => {
    const color = getVersionStatusColor(status);
    const text = getVersionStatusText(status);
    
    return (
      <span 
        className="status-badge"
        style={{
          color: 'white',
          backgroundColor: color,
          padding: '0.25rem 0.5rem',
          borderRadius: '0.375rem',
          fontSize: '0.75rem',
          fontWeight: '500',
          display: 'inline-block',
          minWidth: '80px',
          textAlign: 'center'
        }}
      >
        {text}
      </span>
    );
  };

  if (loading) return <div className="loading">승인 대기 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="approval-list">
      <div className="header-section">
        <div className="header-content">
          <div>
            <h1>🔍 승인 대기 데이터 (Staging)</h1>
            <p>버전별로 수집된 임시 데이터를 확인하고 승인하세요</p>
          </div>
          <div className="header-controls">
            <button 
              onClick={() => loadPendingVersions(true)}
              className="refresh-btn"
            >
              🔄 새로고침
            </button>
            <button 
              onClick={() => navigate('/versions')}
              className="back-btn"
            >
              ← 버전 관리로 돌아가기
            </button>
          </div>
        </div>
      </div>

      <div className="table-container">
        <table className="approval-table">
          <thead>
            <tr>
              <th>버전명</th>
              <th>설명</th>
              <th>상태</th>
              <th>생성자</th>
              <th>생성일</th>
              <th>브랜드 수</th>
              <th>모델 수</th>
              <th>트림 수</th>
              <th>옵션 수</th>
              <th>액션</th>
            </tr>
          </thead>
          <tbody>
            {versions.length === 0 ? (
              <tr>
                <td colSpan="10" className="empty-message">
                  승인 대기 중인 버전이 없습니다.
                </td>
              </tr>
            ) : (
              versions.map(version => (
                <tr key={version.id}>
                  <td className="version-name">
                    <strong>{version.version_name}</strong>
                  </td>
                  <td className="version-description">
                    {version.description || '-'}
                  </td>
                  <td>
                    {getStatusBadge(version.approval_status)}
                  </td>
                  <td>{version.created_by || '-'}</td>
                  <td>
                    {version.created_at ? 
                      new Date(version.created_at).toLocaleDateString('ko-KR') : 
                      '-'
                    }
                  </td>
                  <td className="stat-number">{version.brands_count || 0}</td>
                  <td className="stat-number">{version.models_count || 0}</td>
                  <td className="stat-number">{version.trims_count || 0}</td>
                  <td className="stat-number">{version.options_count || 0}</td>
                  <td className="action-buttons">
                    {canApprove() && (
                      <>
                        <button 
                          onClick={() => handleApproveVersion(version)}
                          className="approve-btn"
                          title="승인"
                        >
                          ✅ 승인
                        </button>
                        <button 
                          onClick={() => handleRejectVersion(version)}
                          className="reject-btn"
                          title="거부"
                        >
                          ❌ 거부
                        </button>
                      </>
                    )}
                    <button 
                      onClick={() => handleEditVersion(version)}
                      className="edit-btn"
                      title="수정"
                    >
                      ✏️ 수정
                    </button>
                    <button 
                      onClick={() => handleDeleteVersion(version)}
                      className="delete-btn"
                      title="삭제"
                    >
                      🗑️ 삭제
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ApprovalList;
