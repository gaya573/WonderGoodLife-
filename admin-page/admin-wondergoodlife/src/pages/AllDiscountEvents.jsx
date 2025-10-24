import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { batchApi } from '../services/api';
import versionAPI from '../services/versionApi';
import './AllDiscountEvents.css';

function AllDiscountEvents() {
  const { versionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(null);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [versionId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 버전 정보 로드
      const versionResponse = await versionAPI.getById(versionId);
      setVersion(versionResponse.data);
      
      // 할인 정책 로드
      const eventsResponse = await batchApi.get('/discount/policies/', {
        params: {
          version_id: parseInt(versionId),
          limit: 100
        }
      });
      
      if (eventsResponse.data && eventsResponse.data.items) {
        setEvents(eventsResponse.data.items);
      } else {
        setEvents([]);
      }
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      setError(error.response?.data?.detail || error.message || '데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getPolicyTypeInfo = (type) => {
    const types = {
      'CARD_BENEFIT': { label: '카드사 제휴', icon: '💳', color: '#8b5cf6' },
      'BRAND_PROMO': { label: '브랜드 프로모션', icon: '🏷️', color: '#10b981' },
      'INVENTORY': { label: '재고 할인', icon: '📦', color: '#f59e0b' },
      'PRE_PURCHASE': { label: '선구매 할인', icon: '⏰', color: '#ef4444' }
    };
    return types[type] || { label: type, icon: '📋', color: '#6b7280' };
  };

  const getStatusColor = (isActive) => {
    return isActive ? '#10b981' : '#ef4444';
  };

  const getStatusText = (isActive) => {
    return isActive ? '활성' : '비활성';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('ko-KR');
  };

  if (loading) {
    return (
      <div className="all-discount-events">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="all-discount-events">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2>오류 발생</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/versions')} className="back-button">
            버전 목록으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="all-discount-events">
      <div className="page-header">
        <button onClick={() => navigate('/versions')} className="back-button">
          ← 버전 목록으로
        </button>
        <div>
          <h1>🎉 전체 할인 이벤트</h1>
          {version && (
            <p className="version-info">
              버전: <strong>{version.version_name}</strong>
              {version.description && ` - ${version.description}`}
            </p>
          )}
        </div>
      </div>

      {events.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>등록된 이벤트가 없습니다</h2>
          <p>이 버전에는 아직 할인 정책이 등록되지 않았습니다.</p>
          <button 
            onClick={() => navigate(`/discount-policies/${versionId}`)}
            className="add-event-button"
          >
            할인 정책 추가하기
          </button>
        </div>
      ) : (
        <>
          <div className="stats-summary">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <div className="stat-label">전체 이벤트</div>
                <div className="stat-value">{events.length}</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <div className="stat-label">활성 이벤트</div>
                <div className="stat-value">
                  {events.filter(e => e.is_active).length}
                </div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⏸️</div>
              <div className="stat-content">
                <div className="stat-label">비활성 이벤트</div>
                <div className="stat-value">
                  {events.filter(e => !e.is_active).length}
                </div>
              </div>
            </div>
          </div>

          <div className="events-grid">
            {events.map((event) => {
              const typeInfo = getPolicyTypeInfo(event.policy_type);
              return (
                <div key={event.id} className="event-card">
                  <div className="event-header">
                    <div className="event-type-badge" style={{ backgroundColor: typeInfo.color }}>
                      <span className="event-icon">{typeInfo.icon}</span>
                      <span className="event-type-label">{typeInfo.label}</span>
                    </div>
                    <div 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(event.is_active) }}
                    >
                      {getStatusText(event.is_active)}
                    </div>
                  </div>

                  <div className="event-body">
                    <h3 className="event-title">{event.title}</h3>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}

                    <div className="event-details">
                      <div className="detail-item">
                        <span className="detail-label">유효 시작일:</span>
                        <span className="detail-value">{formatDate(event.valid_from)}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">유효 종료일:</span>
                        <span className="detail-value">{formatDate(event.valid_to)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="event-footer">
                    <button 
                      onClick={() => navigate(`/discount-policies/${versionId}`)}
                      className="manage-button"
                    >
                      관리하기
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default AllDiscountEvents;

