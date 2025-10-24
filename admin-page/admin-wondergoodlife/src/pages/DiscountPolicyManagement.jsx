import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './DiscountPolicyManagement.css';
import { 
  getVersionDiscountSummary,
  getCardBenefits,
  getPromos,
  getInventoryDiscounts,
  getPrePurchases,
  deleteDiscountPolicyWithDetails
} from '../services/discountApi';
import EditCardBenefitModal from '../components/modals/EditCardBenefitModal';
import EditPromoModal from '../components/modals/EditPromoModal';
import EditInventoryDiscountModal from '../components/modals/EditInventoryDiscountModal';
import EditPrePurchaseModal from '../components/modals/EditPrePurchaseModal';
import DeleteConfirmModal from '../components/modals/DeleteConfirmModal';

function DiscountPolicyManagement() {
  const { versionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [policies, setPolicies] = useState({
    cardBenefits: [],
    promos: [],
    inventoryDiscounts: [],
    prePurchases: []
  });
  
  // 모달 상태
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editModalType, setEditModalType] = useState(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState(null);

  useEffect(() => {
    loadSummary();
    loadAllPolicies();
  }, [versionId]);

  const loadSummary = async () => {
    try {
      const data = await getVersionDiscountSummary(versionId);
      setSummary(data);
    } catch (error) {
      console.error('할인 정책 요약 로드 실패:', error);
    }
  };

  const loadAllPolicies = async () => {
    try {
      setLoading(true);
      
      // 각 카테고리별 정책 목록 가져오기
      const [cardBenefitsRes, promosRes, inventoryRes, prePurchasesRes] = await Promise.all([
        getCardBenefits({ policy_id: null }),
        getPromos({ policy_id: null }),
        getInventoryDiscounts({ policy_id: null }),
        getPrePurchases({ policy_id: null })
      ]);

      setPolicies({
        cardBenefits: cardBenefitsRes.items || [],
        promos: promosRes.items || [],
        inventoryDiscounts: inventoryRes.items || [],
        prePurchases: prePurchasesRes.items || []
      });
    } catch (error) {
      console.error('정책 목록 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const policyTypes = {
    CARD_BENEFIT: { label: '카드사 제휴', icon: '💳', color: '#8b5cf6' },
    BRAND_PROMO: { label: '브랜드 프로모션', icon: '🏷️', color: '#10b981' },
    INVENTORY: { label: '재고 할인', icon: '📦', color: '#f59e0b' },
    PRE_PURCHASE: { label: '선구매 할인', icon: '⏰', color: '#ef4444' }
  };

  const handleAddDiscount = (policyType) => {
    navigate(`/discount-policies/${versionId}/add/${policyType}`);
  };

  const handleEdit = (policy) => {
    // 정책 데이터를 직접 전달 (상세 조회 불필요)
    setSelectedPolicy(policy);
    // policy_type에 따라 어떤 모달을 열지 결정
    if (policy.card_partner !== undefined) {
      setEditModalType('CARD_BENEFIT');
    } else if (policy.inventory_level_threshold !== undefined) {
      setEditModalType('INVENTORY');
    } else if (policy.event_type !== undefined) {
      setEditModalType('PRE_PURCHASE');
    } else {
      setEditModalType('BRAND_PROMO');
    }
    setEditModalOpen(true);
  };

  const handleDelete = (policy) => {
    setSelectedPolicy(policy);
    setDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!selectedPolicy) return;
    
    try {
      const policyId = selectedPolicy.discount_policy_id || selectedPolicy.id;
      await deleteDiscountPolicyWithDetails(policyId);
      alert('정책이 성공적으로 삭제되었습니다.');
      setDeleteModalOpen(false);
      setSelectedPolicy(null);
      loadAllPolicies(); // 목록 새로고침
      loadSummary(); // 요약도 새로고침
    } catch (error) {
      console.error('정책 삭제 실패:', error);
      alert('정책 삭제에 실패했습니다: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
  };

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return `${amount.toLocaleString()}원`;
  };

  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return '-';
    return `${rate}%`;
  };

  const formatDescription = (desc) => {
    if (!desc) return '-';
    return desc.length > 50 ? desc.substring(0, 50) + '...' : desc;
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <div className="discount-policy-management">
      <div className="page-header">
        <h1>💰 할인 정책 관리</h1>
        <p>버전 ID: {versionId}</p>
        <button onClick={() => navigate('/versions')} className="back-button">
          ← 버전 목록으로
        </button>
      </div>

      {summary && (
        <div className="summary-section">
          <div className="summary-card">
            <h3>정책 요약</h3>
            <div className="summary-stats">
              <div className="stat-item">
                <span className="stat-label">전체 정책</span>
                <span className="stat-value">{summary.total_policies}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">카드사 제휴</span>
                <span className="stat-value">{summary.total_card_benefits}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">브랜드 프로모션</span>
                <span className="stat-value">{summary.total_promos}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">재고 할인</span>
                <span className="stat-value">{summary.total_inventory_discounts}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">선구매 할인</span>
                <span className="stat-value">{summary.total_pre_purchases}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 카드사 제휴 섹션 */}
      <div className="policy-section">
        <div className="policy-section-header" style={{ borderColor: policyTypes.CARD_BENEFIT.color }}>
          <div className="policy-section-title">
            <span className="policy-icon" style={{ color: policyTypes.CARD_BENEFIT.color }}>
              {policyTypes.CARD_BENEFIT.icon}
            </span>
            <h2>{policyTypes.CARD_BENEFIT.label}</h2>
            <span className="policy-count">({policies.cardBenefits.length})</span>
          </div>
          <button 
            className="add-button-small"
            style={{ backgroundColor: policyTypes.CARD_BENEFIT.color }}
            onClick={() => handleAddDiscount('CARD_BENEFIT')}
          >
            + 추가
          </button>
        </div>
        
        <div className="policy-table-container">
          <table className="policy-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>제목</th>
                <th>설명</th>
                <th>카드사</th>
                <th>캐시백율</th>
                <th>유효기간</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {policies.cardBenefits.length > 0 ? (
                policies.cardBenefits.map((policy) => (
                  <tr key={policy.id}>
                    <td>{policy.id}</td>
                    <td>{policy.title}</td>
                    <td>{formatDescription(policy.description)}</td>
                    <td>{policy.card_partner}</td>
                    <td>{formatRate(policy.cashback_rate)}</td>
                    <td>{formatDate(policy.valid_from)} ~ {formatDate(policy.valid_to)}</td>
                    <td>
                      <span className={`status-badge ${policy.is_active ? 'active' : 'inactive'}`}>
                        {policy.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td>
                      <button className="action-button edit" onClick={() => handleEdit(policy)}>수정</button>
                      <button className="action-button delete" onClick={() => handleDelete(policy)}>삭제</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="empty-row">등록된 카드사 제휴 정책이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 브랜드 프로모션 섹션 */}
      <div className="policy-section">
        <div className="policy-section-header" style={{ borderColor: policyTypes.BRAND_PROMO.color }}>
          <div className="policy-section-title">
            <span className="policy-icon" style={{ color: policyTypes.BRAND_PROMO.color }}>
              {policyTypes.BRAND_PROMO.icon}
            </span>
            <h2>{policyTypes.BRAND_PROMO.label}</h2>
            <span className="policy-count">({policies.promos.length})</span>
          </div>
          <button 
            className="add-button-small"
            style={{ backgroundColor: policyTypes.BRAND_PROMO.color }}
            onClick={() => handleAddDiscount('BRAND_PROMO')}
          >
            + 추가
          </button>
        </div>
        
        <div className="policy-table-container">
          <table className="policy-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>제목</th>
                <th>설명</th>
                <th>할인율</th>
                <th>할인금액</th>
                <th>유효기간</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {policies.promos.length > 0 ? (
                policies.promos.map((policy) => (
                  <tr key={policy.id}>
                    <td>{policy.id}</td>
                    <td>{policy.title}</td>
                    <td>{formatDescription(policy.description)}</td>
                    <td>{formatRate(policy.discount_rate)}</td>
                    <td>{formatCurrency(policy.discount_amount)}</td>
                    <td>{formatDate(policy.valid_from)} ~ {formatDate(policy.valid_to)}</td>
                    <td>
                      <span className={`status-badge ${policy.is_active ? 'active' : 'inactive'}`}>
                        {policy.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td>
                      <button className="action-button edit" onClick={() => handleEdit(policy)}>수정</button>
                      <button className="action-button delete" onClick={() => handleDelete(policy)}>삭제</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="empty-row">등록된 브랜드 프로모션 정책이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 재고 할인 섹션 */}
      <div className="policy-section">
        <div className="policy-section-header" style={{ borderColor: policyTypes.INVENTORY.color }}>
          <div className="policy-section-title">
            <span className="policy-icon" style={{ color: policyTypes.INVENTORY.color }}>
              {policyTypes.INVENTORY.icon}
            </span>
            <h2>{policyTypes.INVENTORY.label}</h2>
            <span className="policy-count">({policies.inventoryDiscounts.length})</span>
          </div>
          <button 
            className="add-button-small"
            style={{ backgroundColor: policyTypes.INVENTORY.color }}
            onClick={() => handleAddDiscount('INVENTORY')}
          >
            + 추가
          </button>
        </div>
        
        <div className="policy-table-container">
          <table className="policy-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>제목</th>
                <th>설명</th>
                <th>재고기준</th>
                <th>할인율</th>
                <th>유효기간</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {policies.inventoryDiscounts.length > 0 ? (
                policies.inventoryDiscounts.map((policy) => (
                  <tr key={policy.id}>
                    <td>{policy.id}</td>
                    <td>{policy.title}</td>
                    <td>{formatDescription(policy.description)}</td>
                    <td>{policy.inventory_level_threshold}대 이상</td>
                    <td>{formatRate(policy.discount_rate)}</td>
                    <td>{formatDate(policy.valid_from)} ~ {formatDate(policy.valid_to)}</td>
                    <td>
                      <span className={`status-badge ${policy.is_active ? 'active' : 'inactive'}`}>
                        {policy.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td>
                      <button className="action-button edit" onClick={() => handleEdit(policy)}>수정</button>
                      <button className="action-button delete" onClick={() => handleDelete(policy)}>삭제</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="empty-row">등록된 재고 할인 정책이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 선구매 할인 섹션 */}
      <div className="policy-section">
        <div className="policy-section-header" style={{ borderColor: policyTypes.PRE_PURCHASE.color }}>
          <div className="policy-section-title">
            <span className="policy-icon" style={{ color: policyTypes.PRE_PURCHASE.color }}>
              {policyTypes.PRE_PURCHASE.icon}
            </span>
            <h2>{policyTypes.PRE_PURCHASE.label}</h2>
            <span className="policy-count">({policies.prePurchases.length})</span>
          </div>
          <button 
            className="add-button-small"
            style={{ backgroundColor: policyTypes.PRE_PURCHASE.color }}
            onClick={() => handleAddDiscount('PRE_PURCHASE')}
          >
            + 추가
          </button>
        </div>
        
        <div className="policy-table-container">
          <table className="policy-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>제목</th>
                <th>설명</th>
                <th>이벤트</th>
                <th>할인율</th>
                <th>할인금액</th>
                <th>선구매시작일</th>
                <th>유효기간</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {policies.prePurchases.length > 0 ? (
                policies.prePurchases.map((policy) => (
                  <tr key={policy.id}>
                    <td>{policy.id}</td>
                    <td>{policy.title}</td>
                    <td>{formatDescription(policy.description)}</td>
                    <td>{policy.event_type}</td>
                    <td>{formatRate(policy.discount_rate)}</td>
                    <td>{formatCurrency(policy.discount_amount)}</td>
                    <td>{formatDate(policy.pre_purchase_start)}</td>
                    <td>{formatDate(policy.valid_from)} ~ {formatDate(policy.valid_to)}</td>
                    <td>
                      <span className={`status-badge ${policy.is_active ? 'active' : 'inactive'}`}>
                        {policy.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td>
                      <button className="action-button edit" onClick={() => handleEdit(policy)}>수정</button>
                      <button className="action-button delete" onClick={() => handleDelete(policy)}>삭제</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10" className="empty-row">등록된 선구매 할인 정책이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 수정 모달 */}
      {editModalOpen && selectedPolicy && (
        <>
          {editModalType === 'CARD_BENEFIT' && (
            <EditCardBenefitModal
              policy={selectedPolicy}
              onClose={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
              }}
              onSuccess={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
                loadAllPolicies();
                loadSummary();
              }}
            />
          )}
          {editModalType === 'BRAND_PROMO' && (
            <EditPromoModal
              policy={selectedPolicy}
              onClose={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
              }}
              onSuccess={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
                loadAllPolicies();
                loadSummary();
              }}
            />
          )}
          {editModalType === 'INVENTORY' && (
            <EditInventoryDiscountModal
              policy={selectedPolicy}
              onClose={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
              }}
              onSuccess={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
                loadAllPolicies();
                loadSummary();
              }}
            />
          )}
          {editModalType === 'PRE_PURCHASE' && (
            <EditPrePurchaseModal
              policy={selectedPolicy}
              onClose={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
              }}
              onSuccess={() => {
                setEditModalOpen(false);
                setEditModalType(null);
                setSelectedPolicy(null);
                loadAllPolicies();
                loadSummary();
              }}
            />
          )}
        </>
      )}

      {/* 삭제 확인 모달 */}
      {deleteModalOpen && selectedPolicy && (
        <DeleteConfirmModal
          title={selectedPolicy.title || '정책'}
          onConfirm={confirmDelete}
          onCancel={() => {
            setDeleteModalOpen(false);
            setSelectedPolicy(null);
          }}
        />
      )}
    </div>
  );
}

export default DiscountPolicyManagement;
