import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './AddDiscountPolicy.css';
import { batchApi } from '../services/api';
import versionAPI from '../services/versionApi';

function AddDiscountPolicy() {
  const { versionId, policyType } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [brands, setBrands] = useState([]);
  const [vehicleLines, setVehicleLines] = useState([]);
  const [trims, setTrims] = useState([]);
  const [formData, setFormData] = useState({
    brand_id: '',
    vehicle_line_id: '',
    trim_id: '',
    title: '',
    description: '',
    valid_from: '',
    valid_to: '',
    is_active: true,
    card_partner: '',
    cashback_rate: '',
    discount_rate: '',
    discount_amount: '',
    inventory_level_threshold: '',
    pre_purchase_start: ''
  });

  useEffect(() => {
    loadBrandsAndTrims();
  }, [versionId]);

  const loadBrandsAndTrims = async () => {
    try {
      // 간단한 브랜드 목록 API 사용
      const response = await versionAPI.getBrandsList(versionId);
      console.log('브랜드 데이터:', response.data);
      
      if (response.data && response.data.brands) {
        setBrands(response.data.brands);
      }
    } catch (error) {
      console.error('브랜드/트림 로드 실패:', error);
    }
  };

  const handleBrandChange = async (brandId) => {
    setFormData({ ...formData, brand_id: brandId, vehicle_line_id: '', trim_id: '' });
    setVehicleLines([]);
    setTrims([]);
    
    if (!brandId) return;
    
    try {
      // 브랜드별 Vehicle Line 목록 API 사용
      const response = await versionAPI.getBrandVehicleLines(versionId, brandId);
      console.log('Vehicle Line 데이터:', response.data);
      
      if (response.data && response.data.vehicle_lines) {
        setVehicleLines(response.data.vehicle_lines);
      }
    } catch (error) {
      console.error('Vehicle Line 로드 실패:', error);
    }
  };

  const handleVehicleLineChange = async (vehicleLineId) => {
    setFormData({ ...formData, vehicle_line_id: vehicleLineId, trim_id: '' });
    setTrims([]);
    
    if (!vehicleLineId) return;
    
    try {
      // Vehicle Line별 트림 목록 API 사용
      const response = await versionAPI.getVehicleLineTrims(versionId, formData.brand_id, vehicleLineId);
      console.log('트림 데이터:', response.data);
      
      if (response.data && response.data.trims) {
        setTrims(response.data.trims);
      }
    } catch (error) {
      console.error('트림 로드 실패:', error);
    }
  };

  const policyTypes = {
    CARD_BENEFIT: { label: '카드사 제휴', icon: '💳', color: '#8b5cf6' },
    BRAND_PROMO: { label: '브랜드 프로모션', icon: '🏷️', color: '#10b981' },
    INVENTORY: { label: '재고 할인', icon: '📦', color: '#f59e0b' },
    PRE_PURCHASE: { label: '선구매 할인', icon: '⏰', color: '#ef4444' }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.brand_id || !formData.vehicle_line_id || !formData.trim_id) {
      alert('브랜드, Vehicle Line, 트림을 모두 선택해주세요.');
      return;
    }
    
    try {
      setLoading(true);

      // 통합 API로 한 번에 생성 (트랜잭션 보장)
      const policyData = {
        brand_id: parseInt(formData.brand_id),
        vehicle_line_id: parseInt(formData.vehicle_line_id),
        trim_id: parseInt(formData.trim_id),
        version_id: parseInt(versionId),
        policy_type: policyType,
        title: formData.title,
        description: formData.description,
        valid_from: formData.valid_from,
        valid_to: formData.valid_to,
        is_active: formData.is_active,
        // 세부 정보 추가
        card_partner: formData.card_partner || null,
        cashback_rate: formData.cashback_rate ? parseFloat(formData.cashback_rate) : null,
        discount_rate: formData.discount_rate ? parseFloat(formData.discount_rate) : null,
        discount_amount: formData.discount_amount ? parseInt(formData.discount_amount) : null,
        inventory_level_threshold: formData.inventory_level_threshold ? parseInt(formData.inventory_level_threshold) : null,
        event_type: 'PRE_PURCHASE',
        pre_purchase_start: formData.pre_purchase_start || null
      };

      // 통합 API 호출
      await batchApi.post('/discount/policies/with-details', policyData);

      alert('할인 정책이 성공적으로 생성되었습니다!');
      navigate(`/discount-policies/${versionId}`);
    } catch (error) {
      console.error('할인 정책 생성 실패:', error);
      alert('할인 정책 생성에 실패했습니다: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const policyInfo = policyTypes[policyType];

  return (
    <div className="add-discount-policy">
      <div className="page-header">
        <button onClick={() => navigate(`/discount-policies/${versionId}`)} className="back-button">
          ← 할인 정책 목록으로
        </button>
        <h1>{policyInfo?.icon} {policyInfo?.label} 추가</h1>
      </div>

      <form onSubmit={handleSubmit} className="discount-form">
        <div className="form-section">
          <h2>대상 선택</h2>
          
          <div className="form-group">
            <label>브랜드 *</label>
            <select
              value={formData.brand_id}
              onChange={(e) => handleBrandChange(e.target.value)}
              required
            >
              <option value="">브랜드를 선택하세요</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Vehicle Line *</label>
            <select
              value={formData.vehicle_line_id}
              onChange={(e) => handleVehicleLineChange(e.target.value)}
              required
              disabled={!formData.brand_id}
            >
              <option value="">Vehicle Line을 선택하세요</option>
              {vehicleLines.map((vehicleLine) => (
                <option key={vehicleLine.id} value={vehicleLine.id}>
                  {vehicleLine.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>트림 *</label>
            <select
              value={formData.trim_id}
              onChange={(e) => setFormData({ ...formData, trim_id: e.target.value })}
              required
              disabled={!formData.vehicle_line_id}
            >
              <option value="">트림을 선택하세요</option>
              {trims.map((trim) => (
                <option key={trim.id} value={trim.id}>
                  {trim.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-section">
          <h2>기본 정보</h2>
          
          <div className="form-group">
            <label>제목 *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="예: 현대카드 5% 캐시백"
              required
            />
          </div>

          <div className="form-group">
            <label>설명</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="상세 설명을 입력하세요"
              rows="3"
            />
          </div>
        </div>

        <div className="form-section">
          <h2>할인 정보</h2>
          
          {policyType === 'CARD_BENEFIT' && (
            <>
              <div className="form-group">
                <label>카드사 *</label>
                <select
                  value={formData.card_partner || ''}
                  onChange={(e) => setFormData({ ...formData, card_partner: e.target.value })}
                  required
                >
                  <option value="">카드사를 선택하세요</option>
                  <option value="현대카드">현대카드</option>
                  <option value="신한카드">신한카드</option>
                  <option value="삼성카드">삼성카드</option>
                  <option value="우리카드">우리카드</option>
                  <option value="KB손해보험">KB손해보험</option>
                  <option value="애마존카">애마존카</option>
                  <option value="롯데렌터카">롯데렌터카</option>
                  <option value="하이모빌리티">하이모빌리티</option>
                  <option value="SK렌터카">SK렌터카</option>
                  <option value="아주캐피탈">아주캐피탈</option>
                  <option value="하나캐피탈">하나캐피탈</option>
                  <option value="ORIX">ORIX</option>
                  <option value="KDB캐피탈">KDB캐피탈</option>
                  <option value="JB우리캐피탈">JB우리캐피탈</option>
                  <option value="메리츠캐피탈">메리츠캐피탈</option>
                  <option value="BNK캐피탈">BNK캐피탈</option>
                  <option value="AJ렌터카">AJ렌터카</option>
                  <option value="REDCAP렌터카">REDCAP렌터카</option>
                </select>
              </div>
              <div className="form-group">
                <label>캐시백 비율 (%) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cashback_rate || ''}
                  onChange={(e) => setFormData({ ...formData, cashback_rate: e.target.value })}
                  placeholder="예: 5.0"
                  required
                />
              </div>
            </>
          )}

          {policyType === 'BRAND_PROMO' && (
            <>
              <div className="form-group">
                <label>할인율 (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.discount_rate || ''}
                  onChange={(e) => setFormData({ ...formData, discount_rate: e.target.value })}
                  placeholder="예: 10.0"
                />
              </div>
              <div className="form-group">
                <label>정액 할인 (원)</label>
                <input
                  type="number"
                  value={formData.discount_amount || ''}
                  onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value })}
                  placeholder="예: 100000"
                />
              </div>
              <p className="form-hint">할인율 또는 정액 할인 중 하나를 입력하세요.</p>
            </>
          )}

          {policyType === 'INVENTORY' && (
            <>
              <div className="form-group">
                <label>재고 기준 수량 *</label>
                <input
                  type="number"
                  value={formData.inventory_level_threshold || ''}
                  onChange={(e) => setFormData({ ...formData, inventory_level_threshold: e.target.value })}
                  placeholder="예: 10"
                  required
                />
              </div>
              <div className="form-group">
                <label>할인율 (%) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.discount_rate || ''}
                  onChange={(e) => setFormData({ ...formData, discount_rate: e.target.value })}
                  placeholder="예: 15.0"
                  required
                />
              </div>
            </>
          )}

          {policyType === 'PRE_PURCHASE' && (
            <>
              <div className="form-group">
                <label>할인율 (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.discount_rate || ''}
                  onChange={(e) => setFormData({ ...formData, discount_rate: e.target.value })}
                  placeholder="예: 20.0"
                />
              </div>
              <div className="form-group">
                <label>정액 할인 (원)</label>
                <input
                  type="number"
                  value={formData.discount_amount || ''}
                  onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value })}
                  placeholder="예: 200000"
                />
              </div>
              <p className="form-hint">할인율 또는 정액 할인 중 하나를 입력하세요.</p>
              <div className="form-group">
                <label>사전구매 시작일</label>
                <input
                  type="datetime-local"
                  value={formData.pre_purchase_start || ''}
                  onChange={(e) => setFormData({ ...formData, pre_purchase_start: e.target.value })}
                />
              </div>
            </>
          )}
        </div>

        <div className="form-section">
          <h2>유효 기간</h2>
          
          <div className="form-group">
            <label>유효 시작일 *</label>
            <input
              type="datetime-local"
              value={formData.valid_from}
              onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>유효 종료일 *</label>
            <input
              type="datetime-local"
              value={formData.valid_to}
              onChange={(e) => setFormData({ ...formData, valid_to: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              활성화
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            onClick={() => navigate(`/discount-policies/${versionId}`)} 
            className="cancel-button"
          >
            취소
          </button>
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? '생성 중...' : '생성'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddDiscountPolicy;
