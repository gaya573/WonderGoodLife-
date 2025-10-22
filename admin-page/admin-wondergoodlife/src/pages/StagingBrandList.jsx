import React, { useState, useEffect } from 'react';
import versionAPI from '../services/versionApi';
import { useNavigate } from 'react-router-dom';
import './ApprovalList.css'; // ApprovalList.css 사용

function StagingBrandList() {
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
    
    loadVersions();
  }, []);

  const loadVersions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Dashboard와 동일한 방식으로 모든 버전 로드 (상태 필터 제거)
      const response = await versionAPI.getAll({ limit: 100 });
      const allVersions = response.data.items || [];
      
      // 간단한 데이터 개수 계산 (API에서 직접 가져오기)
      const versionsWithCounts = allVersions.map(version => ({
        ...version,
        brands_count: version.brands_count || version.total_brands || 0,
        models_count: version.models_count || version.total_models || 0,
        trims_count: version.trims_count || version.total_trims || 0,
        options_count: version.options_count || version.total_options || 0
      }));
      
      setVersions(versionsWithCounts);
    } catch (err) {
      console.error('버전 목록 로드 실패:', err);
      setError('버전 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 승인 권한 체크 함수 (모든 사용자가 승인 가능)
  const canApprove = () => {
    return true; // 모든 사용자가 승인 가능하도록 변경
  };

  const handleApproveVersion = async (version) => {
    if (!window.confirm(`버전 '${version.version_name}'을 승인하시겠습니까?\n\n승인 시 기존 메인 DB 데이터가 완전히 삭제되고 새로운 데이터로 덮어쓰여집니다.`)) {
      return;
    }

    try {
      const response = await versionAPI.approveVersion(version.id);
      
      // 푸시 성공 여부에 따라 다른 메시지 표시
      if (response.data.pushed_data) {
        alert(`✅ 승인 완료!\n\n${response.data.message}\n\n푸시된 데이터:\n- 브랜드: ${response.data.pushed_data.brands || 0}개\n- 모델: ${response.data.pushed_data.models || 0}개\n- 트림: ${response.data.pushed_data.trims || 0}개\n- 옵션: ${response.data.pushed_data.options || 0}개`);
      } else if (response.data.push_error) {
        alert(`⚠️ 승인은 완료되었지만 메인 DB 푸시에 실패했습니다.\n\n${response.data.message}\n\n푸시 오류: ${response.data.push_error}\n\n수동으로 "Staging → Main 푸시" 버튼을 사용해주세요.`);
      } else {
        alert(response.data.message);
      }
      
      loadVersions(); // 목록 새로고침
    } catch (err) {
      alert('버전 승인에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRejectVersion = async (version) => {
    const reason = prompt(`버전 '${version.version_name}'을 거부하시겠습니까?\n\n거부 사유를 입력해주세요:`, '');
    if (reason === null) return; // 취소
    
    if (!reason.trim()) {
      alert('거부 사유를 입력해주세요.');
      return;
    }
    
    try {
      const response = await versionAPI.rejectVersion(version.id, reason);
      alert(response.data.message);
      loadVersions(); // 목록 새로고침
    } catch (err) {
      alert('버전 거부에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'PENDING': { text: '승인 대기', color: '#f59e0b', bgColor: '#fef3c7' },
      'APPROVED': { text: '승인됨', color: '#10b981', bgColor: '#d1fae5' },
      'REJECTED': { text: '거부됨', color: '#ef4444', bgColor: '#fee2e2' },
      'MIGRATED': { text: '이전됨', color: '#3b82f6', bgColor: '#dbeafe' }
    };
    
    const config = statusConfig[status] || statusConfig['PENDING'];
    
    return (
      <span 
        className="status-badge"
        style={{
          color: config.color,
          backgroundColor: config.bgColor,
          padding: '0.25rem 0.5rem',
          borderRadius: '0.375rem',
          fontSize: '0.75rem',
          fontWeight: '500'
        }}
      >
        {config.text}
      </span>
    );
  };

  if (loading) return <div className="loading">버전 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="approval-list">
      <div className="header-section">
        <div className="header-content">
          <div>
            <h1>🔍 Staging 데이터 관리</h1>
            <p>버전별로 수집된 데이터를 확인하고 승인하세요</p>
          </div>
          <div className="header-controls">
            <button 
              onClick={loadVersions}
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
              <th>상태</th>
              <th>버전명</th>
              <th>설명</th>
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
                  등록된 버전이 없습니다.
                </td>
              </tr>
            ) : (
              versions.map(version => (
                <tr key={version.id}>
                  <td>
                    {getStatusBadge(version.approval_status)}
                  </td>
                  <td className="version-name">
                    <strong>{version.version_name}</strong>
                  </td>
                  <td className="version-description">
                    {version.description || '-'}
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

export default StagingBrandList;