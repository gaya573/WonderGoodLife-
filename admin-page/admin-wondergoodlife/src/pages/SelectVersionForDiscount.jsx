import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './SelectVersionForDiscount.css';
import versionAPI from '../services/versionApi';

function SelectVersionForDiscount() {
  const navigate = useNavigate();
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVersions();
  }, []);

  const loadVersions = async () => {
    try {
      setLoading(true);
      const response = await versionAPI.getAll({ skip: 0, limit: 100 });
      console.log('API 응답:', response);
      console.log('응답 데이터:', response.data);
      console.log('응답 items:', response.data?.items);
      
      // response.data가 있는 경우와 없는 경우 모두 처리
      const items = response.data?.items || response.items || [];
      console.log('최종 items:', items);
      setVersions(items);
    } catch (error) {
      console.error('버전 목록 로드 실패:', error);
      console.error('에러 상세:', error.response);
      alert('버전 목록을 불러오는데 실패했습니다: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectVersion = (versionId) => {
    navigate(`/discount-policies/${versionId}`);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PENDING': return '#f59e0b';
      case 'APPROVED': return '#10b981';
      case 'MIGRATED': return '#3b82f6';
      case 'REJECTED': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'PENDING': return '대기중';
      case 'APPROVED': return '승인됨';
      case 'MIGRATED': return '마이그레이션 완료';
      case 'REJECTED': return '거부됨';
      default: return status;
    }
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <div style={{ padding: '2rem', background: '#f9fafb', minHeight: '100vh' }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '1.875rem',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '0.5rem'
            }}>
              💰 할인 정책 추가
            </h1>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '1rem'
            }}>
              총 {versions.length}개의 버전
            </p>
          </div>
          <button 
            onClick={() => navigate('/versions')}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseOver={(e) => e.target.style.background = '#4b5563'}
            onMouseOut={(e) => e.target.style.background = '#6b7280'}
          >
            ← 버전 관리로
          </button>
        </div>
      </div>

      {versions.length === 0 ? (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '3rem',
          textAlign: 'center',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            fontSize: '3rem', 
            marginBottom: '1rem',
            opacity: 0.5
          }}>
            💰
          </div>
          <p style={{ 
            color: '#6b7280', 
            fontSize: '1.125rem', 
            margin: '0 0 0.5rem 0'
          }}>
            등록된 버전이 없습니다.
          </p>
          <p style={{ 
            color: '#9ca3af', 
            fontSize: '0.875rem', 
            margin: '0 0 1.5rem 0'
          }}>
            먼저 버전을 생성한 후 할인 정책을 추가하세요.
          </p>
          <button 
            onClick={() => navigate('/versions')}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseOver={(e) => e.target.style.background = '#2563eb'}
            onMouseOut={(e) => e.target.style.background = '#3b82f6'}
          >
            버전 관리로 이동
          </button>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
          gap: '1.5rem'
        }}>
          {versions.map((version) => (
            <div 
              key={version.id}
              style={{
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                padding: '1.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                transition: 'box-shadow 0.2s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}
              onMouseOut={(e) => e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '1rem'
              }}>
                <h3 style={{
                  margin: 0,
                  fontSize: '1.25rem',
                  fontWeight: '600',
                  color: '#111827'
                }}>
                  {version.version_name}
                </h3>
                <span 
                  style={{ 
                    backgroundColor: getStatusColor(version.approval_status),
                    color: 'white',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: '500'
                  }}
                >
                  {getStatusText(version.approval_status)}
                </span>
              </div>
              
              {version.description && (
                <p style={{
                  color: '#000',
                  fontSize: '1.5rem',
                  fontWeight: 'bold',
                  margin: '0 0 1rem 0',
                  lineHeight: '1.5'
                }}>
                  {version.description}
                </p>
              )}
              
              <div style={{
                fontSize: '0.75rem',
                color: '#6b7280',
                marginBottom: '1.5rem',
                lineHeight: '1.5'
              }}>
                <div>생성자: {version.created_by}</div>
                <div>생성일: {version.created_at ? new Date(version.created_at).toLocaleString() : 'N/A'}</div>
              </div>
              
              <button 
                onClick={() => handleSelectVersion(version.id)}
                style={{
                  width: '100%',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseOver={(e) => e.target.style.background = '#2563eb'}
                onMouseOut={(e) => e.target.style.background = '#3b82f6'}
              >
                💰 할인 정책 추가하기
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SelectVersionForDiscount;
