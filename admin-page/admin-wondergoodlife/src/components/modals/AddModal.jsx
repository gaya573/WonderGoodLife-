import { useState } from 'react';

/**
 * 추가 모달 컴포넌트
 * 브랜드, 모델, 트림 등의 추가 기능을 제공
 */
const AddModal = ({ addingItem, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    country: '',
    logo_url: '',
    manager: '',
    code: '',
    price: '',
    car_type: '',
    fuel_name: '',
    cc: '',
    base_price: '',
    description: '',
    category: '',
    discounted_price: ''
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ ...formData, type: addingItem.type, parentItem: addingItem.parentItem });
  };

  if (!addingItem) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }} onClick={onClose}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          paddingBottom: '1rem',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <h2 style={{
            margin: 0,
            fontSize: '1.25rem',
            fontWeight: '600',
            color: '#111827'
          }}>
            {addingItem.type === 'brands' ? '브랜드' : addingItem.type === 'models' ? '모델' : addingItem.type === 'trims' ? '트림' : addingItem.type === 'option-titles' ? '옵션 타이틀' : '옵션 가격'} 추가
          </h2>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#6b7280',
              padding: '0.25rem'
            }}
          >
            ×
          </button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          {/* 공통 필드 */}
          <div className="form-group">
            <label className="form-label">이름 *</label>
            <input
              className="form-input"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          {/* 브랜드 전용 필드 */}
          {addingItem.type === 'brands' && (
            <>
              <div className="form-group">
                <label className="form-label">국가</label>
                <input
                  className="form-input"
                  type="text"
                  name="country"
                  value={formData.country}
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
                  value={formData.logo_url}
                  onChange={handleChange}
                  placeholder="https://example.com/logo.png"
                />
              </div>
              <div className="form-group">
                <label className="form-label">관리자</label>
                <input
                  className="form-input"
                  type="text"
                  name="manager"
                  value={formData.manager}
                  onChange={handleChange}
                  placeholder="브랜드 관리자 이름"
                />
              </div>
            </>
          )}

          {/* 모델 전용 필드 */}
          {addingItem.type === 'models' && (
            <>
              <div className="form-group">
                <label className="form-label">코드</label>
                <input
                  className="form-input"
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  placeholder="모델 코드"
                />
              </div>
              <div className="form-group">
                <label className="form-label">부모 브랜드</label>
                <input
                  className="form-input"
                  type="text"
                  value={addingItem.parentItem?.name || ''}
                  disabled
                  style={{ background: '#f3f4f6' }}
                />
              </div>
            </>
          )}

          {/* 트림 전용 필드 */}
          {addingItem.type === 'trims' && (
            <>
              <div className="form-group">
                <label className="form-label">차량 타입</label>
                <select
                  className="form-input"
                  name="car_type"
                  value={formData.car_type}
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
                  value={formData.fuel_name}
                  onChange={handleChange}
                  placeholder="예: 가솔린, 디젤, 하이브리드"
                />
              </div>
              <div className="form-group">
                <label className="form-label">배기량</label>
                <input
                  className="form-input"
                  type="text"
                  name="cc"
                  value={formData.cc}
                  onChange={handleChange}
                  placeholder="예: 2000cc"
                />
              </div>
              <div className="form-group">
                <label className="form-label">기본 가격</label>
                <input
                  className="form-input"
                  type="number"
                  name="base_price"
                  value={formData.base_price}
                  onChange={handleChange}
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label className="form-label">부모 모델</label>
                <input
                  className="form-input"
                  type="text"
                  value={addingItem.parentItem?.name || ''}
                  disabled
                  style={{ background: '#f3f4f6' }}
                />
              </div>
            </>
          )}

          {/* 옵션 타이틀 전용 필드 */}
          {addingItem.type === 'option-titles' && (
            <>
              <div className="form-group">
                <label className="form-label">설명</label>
                <input
                  className="form-input"
                  type="text"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="옵션 타이틀 설명"
                />
              </div>
              <div className="form-group">
                <label className="form-label">카테고리</label>
                <input
                  className="form-input"
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  placeholder="예: 인테리어, 안전, 편의"
                />
              </div>
              <div className="form-group">
                <label className="form-label">부모 트림</label>
                <input
                  className="form-input"
                  type="text"
                  value={addingItem.parentItem?.name || ''}
                  disabled
                  style={{ background: '#f3f4f6' }}
                />
              </div>
            </>
          )}

          {/* 옵션 가격 전용 필드 */}
          {addingItem.type === 'option-prices' && (
            <>
              <div className="form-group">
                <label className="form-label">코드</label>
                <input
                  className="form-input"
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  placeholder="옵션 코드"
                />
              </div>
              <div className="form-group">
                <label className="form-label">설명</label>
                <input
                  className="form-input"
                  type="text"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="옵션 가격 설명"
                />
              </div>
              <div className="form-group">
                <label className="form-label">가격</label>
                <input
                  className="form-input"
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label className="form-label">할인 가격</label>
                <input
                  className="form-input"
                  type="number"
                  name="discounted_price"
                  value={formData.discounted_price}
                  onChange={handleChange}
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label className="form-label">부모 옵션 타이틀</label>
                <input
                  className="form-input"
                  type="text"
                  value={addingItem.parentItem?.name || ''}
                  disabled
                  style={{ background: '#f3f4f6' }}
                />
              </div>
            </>
          )}

          <div style={{
            display: 'flex',
            gap: '0.75rem',
            justifyContent: 'flex-end',
            marginTop: '2rem',
            paddingTop: '1rem',
            borderTop: '1px solid #e5e7eb'
          }}>
            <button 
              type="button" 
              onClick={onClose}
              style={{
                background: 'white',
                color: '#6b7280',
                border: '1px solid #d1d5db',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.target.style.background = '#f9fafb';
                e.target.style.borderColor = '#9ca3af';
              }}
              onMouseOut={(e) => {
                e.target.style.background = 'white';
                e.target.style.borderColor = '#d1d5db';
              }}
            >
              취소
            </button>
            <button 
              type="submit"
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
              추가
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddModal;
