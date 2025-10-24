import { useState, useEffect } from 'react';
import { updatePrePurchase } from '../../services/discountApi';
import './EditDiscountPolicyModal.css';

function EditPrePurchaseModal({ policy, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    valid_from: '',
    valid_to: '',
    is_active: true,
    event_type: 'PRE_PURCHASE',
    discount_rate: '',
    discount_amount: '',
    pre_purchase_start: ''
  });

  useEffect(() => {
    if (policy) {
      setFormData({
        title: policy.title || '',
        description: policy.description || '',
        valid_from: policy.valid_from ? new Date(policy.valid_from).toISOString().slice(0, 16) : '',
        valid_to: policy.valid_to ? new Date(policy.valid_to).toISOString().slice(0, 16) : '',
        is_active: policy.is_active !== undefined ? policy.is_active : true,
        event_type: policy.event_type || 'PRE_PURCHASE',
        discount_rate: policy.discount_rate || '',
        discount_amount: policy.discount_amount || '',
        pre_purchase_start: policy.pre_purchase_start ? new Date(policy.pre_purchase_start).toISOString().slice(0, 16) : ''
      });
    }
  }, [policy]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);

      const updateData = {
        event_type: formData.event_type,
        discount_rate: formData.discount_rate ? parseFloat(formData.discount_rate) : null,
        discount_amount: formData.discount_amount ? parseInt(formData.discount_amount) : null,
        title: formData.title,
        description: formData.description,
        pre_purchase_start: formData.pre_purchase_start || null,
        valid_from: formData.valid_from,
        valid_to: formData.valid_to,
        is_active: formData.is_active
      };

      await updatePrePurchase(policy.id, updateData);

      alert('선구매 할인 정책이 성공적으로 수정되었습니다!');
      onSuccess();
    } catch (error) {
      console.error('정책 수정 실패:', error);
      alert('정책 수정에 실패했습니다: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>선구매 할인 수정</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>제목 *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>설명</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>이벤트 타입</label>
              <select
                name="event_type"
                value={formData.event_type}
                onChange={handleChange}
              >
                <option value="PRE_PURCHASE">선구매</option>
                <option value="EARLY_BIRD">얼리버드</option>
              </select>
            </div>

            <div className="form-group">
              <label>할인율 (%)</label>
              <input
                type="number"
                name="discount_rate"
                value={formData.discount_rate}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
              />
            </div>

            <div className="form-group">
              <label>할인금액 (원)</label>
              <input
                type="number"
                name="discount_amount"
                value={formData.discount_amount}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>유효 시작일 *</label>
                <input
                  type="datetime-local"
                  name="valid_from"
                  value={formData.valid_from}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>유효 종료일 *</label>
                <input
                  type="datetime-local"
                  name="valid_to"
                  value={formData.valid_to}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>선구매 시작일</label>
              <input
                type="datetime-local"
                name="pre_purchase_start"
                value={formData.pre_purchase_start}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                />
                활성 상태
              </label>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="cancel-button" onClick={onClose}>
              취소
            </button>
            <button type="submit" className="confirm-button" disabled={loading}>
              {loading ? '저장 중...' : '저장'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditPrePurchaseModal;

