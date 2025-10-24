import { useState, useEffect } from 'react';
import { updateCardBenefit } from '../../services/discountApi';
import './EditDiscountPolicyModal.css';

function EditCardBenefitModal({ policy, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    valid_from: '',
    valid_to: '',
    is_active: true,
    card_partner: '',
    cashback_rate: ''
  });

  useEffect(() => {
    if (policy) {
      setFormData({
        title: policy.title || '',
        description: policy.description || '',
        valid_from: policy.valid_from ? new Date(policy.valid_from).toISOString().slice(0, 16) : '',
        valid_to: policy.valid_to ? new Date(policy.valid_to).toISOString().slice(0, 16) : '',
        is_active: policy.is_active !== undefined ? policy.is_active : true,
        card_partner: policy.card_partner || '',
        cashback_rate: policy.cashback_rate || ''
      });
    }
  }, [policy]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);

      const updateData = {
        card_partner: formData.card_partner || null,
        cashback_rate: formData.cashback_rate ? parseFloat(formData.cashback_rate) : null,
        title: formData.title,
        description: formData.description,
        valid_from: formData.valid_from,
        valid_to: formData.valid_to,
        is_active: formData.is_active
      };

      await updateCardBenefit(policy.id, updateData);

      alert('카드사 제휴 정책이 성공적으로 수정되었습니다!');
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
          <h2>카드사 제휴 수정</h2>
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
              <label>카드사</label>
              <input
                type="text"
                name="card_partner"
                value={formData.card_partner}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>캐시백율 (%)</label>
              <input
                type="number"
                name="cashback_rate"
                value={formData.cashback_rate}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
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

export default EditCardBenefitModal;

