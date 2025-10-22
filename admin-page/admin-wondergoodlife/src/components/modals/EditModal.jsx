import { useState } from 'react';

/**
 * 편집 모달 컴포넌트
 * 브랜드, 모델, 트림 등의 편집 기능을 제공
 */
const EditModal = ({ item, onSave, onClose }) => {
  const [formData, setFormData] = useState(item || {});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!item) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">
            {item.type === 'brands' ? '브랜드' : item.type === 'models' ? '모델' : '트림'} 수정
          </h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          {/* 공통 필드 */}
          <div className="form-group">
            <label className="form-label">이름 *</label>
            <input
              className="form-input"
              type="text"
              name="name"
              value={formData.name || ''}
              onChange={handleChange}
              required
            />
          </div>

          {/* 브랜드 전용 필드 */}
          {item.type === 'brands' && (
            <>
              <div className="form-group">
                <label className="form-label">국가</label>
                <input
                  className="form-input"
                  type="text"
                  name="country"
                  value={formData.country || ''}
                  onChange={handleChange}
                  placeholder="예: Korea, United States, Japan"
                  maxLength={50}
                />
              </div>
              <div className="form-group">
                <label className="form-label">로고 URL</label>
                <input
                  className="form-input"
                  type="text"
                  name="logo_url"
                  value={formData.logo_url || ''}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label">관리자</label>
                <input
                  className="form-input"
                  type="text"
                  name="manager"
                  value={formData.manager || ''}
                  onChange={handleChange}
                  placeholder="브랜드 관리자 이름"
                />
              </div>
            </>
          )}

          {/* 모델 전용 필드 */}
          {item.type === 'models' && (
            <>
              <div className="form-group">
                <label className="form-label">코드</label>
                <input
                  className="form-input"
                  type="text"
                  name="code"
                  value={formData.code || ''}
                  onChange={handleChange}
                />
              </div>
            </>
          )}

          {/* 트림 전용 필드 */}
          {item.type === 'trims' && (
            <>
              <div className="form-group">
                <label className="form-label">차량 타입</label>
                <select
                  className="form-input"
                  name="car_type"
                  value={formData.car_type || ''}
                  onChange={handleChange}
                >
                  <option value="">차량 타입을 선택하세요</option>
                  <option value="경_소형승용">경소형승용</option>
                  <option value="중형승용">중형승용</option>
                  <option value="대형승용">대형승용</option>
                  <option value="SUV_RV">SUV/RV</option>
                  <option value="화물_승합">화물/승합</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">연료</label>
                <input
                  className="form-input"
                  type="text"
                  name="fuel_name"
                  value={formData.fuel_name || ''}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label">배기량</label>
                <input
                  className="form-input"
                  type="text"
                  name="cc"
                  value={formData.cc || ''}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label">기본 가격</label>
                <input
                  className="form-input"
                  type="number"
                  name="base_price"
                  value={formData.base_price || ''}
                  onChange={handleChange}
                />
              </div>
            </>
          )}

          <div className="modal-actions">
            <button type="submit" className="btn-save">
              💾 저장
            </button>
            <button type="button" className="btn-cancel" onClick={onClose}>
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditModal;
