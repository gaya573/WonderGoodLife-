import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import versionAPI from '../services/versionApi';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVersions(true); // 초기 로드
    
    // 30초마다 데이터 새로고침 (깜빡임 방지)
    const interval = setInterval(() => {
      loadVersions(false); // 백그라운드 새로고침
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadVersions = async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      }
      const response = await versionAPI.getAll({ limit: 3 });
      setVersions(response.data.items || []);
    } catch (error) {
      console.error('버전 데이터 로드 실패:', error);
      setVersions([]);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      }
    }
  };


  const getVersionStatusColor = (status) => {
    switch (status) {
      case 'DRAFT': return '#f59e0b'; // 주황
      case 'APPROVED': return '#10b981'; // 초록
      case 'MIGRATED': return '#3b82f6'; // 파랑
      case 'FAILED': return '#ef4444'; // 빨강
      default: return '#6b7280'; // 회색
    }
  };

  const getVersionStatusText = (status) => {
    switch (status) {
      case 'DRAFT': return '작업 대기';
      case 'APPROVED': return '승인 완료';
      case 'MIGRATED': return '이동 완료';
      case 'FAILED': return '실패';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Celery 작업 모니터링</h1>
        </div>
        <div className="loading">작업 데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-main-header">
        <h1 className="dashboard-main-title">
          Celery 작업 모니터링
        </h1>
      </div>

      {/* Flower 대시보드 링크 */}
      <div className="flower-dashboard-section">
        <h3 className="flower-dashboard-title">Celery 작업 모니터링</h3>
        <a 
          href="http://localhost:5555" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flower-dashboard-link"
        >
          🌸 Flower 대시보드에서 자세히 보기
        </a>
      </div>

      {/* 버전별 작업 진행 상황 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{
          margin: '0 0 0.5rem 0',
          fontSize: '1.25rem',
          fontWeight: '600',
          color: '#111827'
        }}>
          버전별 작업 진행 상황
        </h2>
        <p style={{
          margin: '0 0 1.5rem 0',
          fontSize: '0.875rem',
          color: '#6b7280',
          lineHeight: '1.5'
        }}>
          각 버전의 브랜드, 모델, 트림 데이터 현황을 확인하고<br/>
          데이터 관리 버튼을 클릭하여 상세 정보를 조회하세요.
        </p>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {versions.length === 0 ? (
            <div style={{
              gridColumn: '1 / -1',
              textAlign: 'center',
              padding: '3rem',
              color: '#6b7280'
            }}>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem' }}>
                등록된 버전이 없습니다.
              </p>
              <p style={{ margin: 0, fontSize: '0.875rem' }}>
                새 버전을 생성하여 작업을 시작하세요.
              </p>
            </div>
          ) : (
            versions.map(version => (
              <div key={version.id} style={{
                background: '#f8fafc',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                padding: '1.5rem',
                transition: 'box-shadow 0.2s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}
              onMouseOut={(e) => e.currentTarget.style.boxShadow = 'none'}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '1rem'
                }}>
                  <h3 style={{
                    margin: 0,
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    color: '#111827'
                  }}>
                    {version.version_name}
                  </h3>
                  <button
                    onClick={() => navigate(`/version-data?version_id=${version.id}`)}
                    style={{
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
                  >
                    데이터 관리
                  </button>
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{
                        fontSize: '1.25rem',
                        fontWeight: '700',
                        color: '#111827',
                        marginBottom: '0.25rem'
                      }}>
                        {version.total_brands || 0}
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#6b7280',
                        fontWeight: '500'
                      }}>
                        브랜드
                      </div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{
                        fontSize: '1.25rem',
                        fontWeight: '700',
                        color: '#111827',
                        marginBottom: '0.25rem'
                      }}>
                        {version.total_models || 0}
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#6b7280',
                        fontWeight: '500'
                      }}>
                        모델
                      </div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{
                        fontSize: '1.25rem',
                        fontWeight: '700',
                        color: '#111827',
                        marginBottom: '0.25rem'
                      }}>
                        {version.total_trims || 0}
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#6b7280',
                        fontWeight: '500'
                      }}>
                        트림
                      </div>
                    </div>
                  </div>
                  
                  {version.status === 'DRAFT' && (
                    <div style={{
                      background: '#e5e7eb',
                      borderRadius: '9999px',
                      height: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        background: '#3b82f6',
                        height: '100%',
                        width: `${Math.min(((version.total_trims || 0) / Math.max(version.total_models || 1, 1)) * 100, 100)}%`,
                        transition: 'width 0.3s ease'
                      }}></div>
                    </div>
                  )}
                </div>
                
                <div style={{
                  fontSize: '0.75rem',
                  color: '#6b7280',
                  lineHeight: '1.5'
                }}>
                  <div>생성: {new Date(version.created_at).toLocaleDateString('ko-KR')}</div>
                  {version.approved_by && <div>승인자: {version.approved_by}</div>}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}

export default Dashboard;

