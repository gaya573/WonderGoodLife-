import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { batchApi } from '../services/api';
import './AllDiscountEvents.css';

function MainDBDiscountPolicies() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [policies, setPolicies] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Main DB 할인 정책 로드
      const response = await batchApi.get('/main-db/discount-policies');
      
      if (response.data) {
        setPolicies(response.data.policies || []);
        setStats(response.data.stats || {});
      } else {
        setPolicies([]);
        setStats({ total: 0, card_benefit: 0, brand_promo: 0, inventory: 0, pre_purchase: 0, active: 0 });
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
          <h1>🎉 메인 DB 전체 할인 목록</h1>
          <p className="version-info">
            현재 메인 데이터베이스에 저장된 모든 할인 정책을 확인할 수 있습니다.
          </p>
        </div>
      </div>

      {policies.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>등록된 할인 정책이 없습니다</h2>
          <p>메인 DB에는 아직 할인 정책이 등록되지 않았습니다.</p>
        </div>
      ) : (
        <>
          {stats && (
            <div className="stats-summary">
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <div className="stat-label">전체 정책</div>
                  <div className="stat-value">{stats.total}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">💳</div>
                <div className="stat-content">
                  <div className="stat-label">카드사 제휴</div>
                  <div className="stat-value">{stats.card_benefit}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🏷️</div>
                <div className="stat-content">
                  <div className="stat-label">브랜드 프로모션</div>
                  <div className="stat-value">{stats.brand_promo}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📦</div>
                <div className="stat-content">
                  <div className="stat-label">재고 할인</div>
                  <div className="stat-value">{stats.inventory}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⏰</div>
                <div className="stat-content">
                  <div className="stat-label">선구매 할인</div>
                  <div className="stat-value">{stats.pre_purchase}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-content">
                  <div className="stat-label">활성 정책</div>
                  <div className="stat-value">{stats.active}</div>
                </div>
              </div>
            </div>
          )}

          <div className="events-grid">
            {policies.map((policy) => {
              const typeInfo = getPolicyTypeInfo(policy.policy_type);
              return (
                <div key={policy.id} className="event-card">
                  <div className="event-header">
                    <div className="event-type-badge" style={{ backgroundColor: typeInfo.color }}>
                      <span className="event-icon">{typeInfo.icon}</span>
                      <span className="event-type-label">{typeInfo.label}</span>
                    </div>
                    <div 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(policy.is_active) }}
                    >
                      {getStatusText(policy.is_active)}
                    </div>
                  </div>

                  <div className="event-body">
                    <h3 className="event-title">{policy.title}</h3>
                    {policy.description && (
                      <p className="event-description">{policy.description}</p>
                    )}

                    <div className="event-details">
                      <div className="detail-item">
                        <span className="detail-label">브랜드:</span>
                        <span className="detail-value">{policy.brand_name || 'N/A'}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">차량 라인:</span>
                        <span className="detail-value">{policy.vehicle_line_name || 'N/A'}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">트림:</span>
                        <span className="detail-value">{policy.trim_name || 'N/A'}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">유효 시작일:</span>
                        <span className="detail-value">{formatDate(policy.valid_from)}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">유효 종료일:</span>
                        <span className="detail-value">{formatDate(policy.valid_to)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="event-footer">
                    <div className="policy-id">
                      ID: {policy.id}
                    </div>
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

export default MainDBDiscountPolicies;

