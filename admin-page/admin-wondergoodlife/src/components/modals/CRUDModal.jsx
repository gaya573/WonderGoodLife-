import React, { useState, useEffect } from 'react';
import './CRUDModal.css';

/**
 * CRUD 모달 컴포넌트 - 브랜드, 모델, 트림, 옵션 생성/수정/삭제
 */
function CRUDModal({ 
  isOpen, 
  onClose, 
  type, 
  action, 
  item, 
  parentItem, 
  onSubmit, 
  onDelete 
}) {
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 폼 데이터 초기화
  useEffect(() => {
    if (isOpen) {
      setError(null);
      
      if (action === 'edit' && item) {
        // 수정 모드: 기존 데이터로 폼 초기화
        setFormData({
          name: item.name || '',
          ...getTypeSpecificFields(item, type)
        });
      } else {
        // 생성 모드: 빈 폼으로 초기화
        setFormData({
          name: '',
          ...getTypeSpecificFields({}, type)
        });
      }
    }
  }, [isOpen, action, item, type]);

  // 타입별 필드 설정
  function getTypeSpecificFields(item, type) {
    switch (type) {
      case 'brand':
        return {
          country: item.country || 'KR',
          logo_url: item.logo_url || '',
          manager: item.manager || ''
        };
      case 'model':
        return {
          code: item.code || '',
          release_year: item.release_year || '',
          price: item.price || '',
          foreign: item.foreign || false
        };
      case 'trim':
        return {
          car_type: item.car_type || '',
          fuel_name: item.fuel_name || '',
          cc: item.cc || '',
          base_price: item.base_price || '',
          description: item.description || ''
        };
      case 'option':
        return {
          code: item.code || '',
          description: item.description || '',
          category: item.category || '',
          price: item.price || '',
          discounted_price: item.discounted_price || ''
        };
      default:
        return {};
    }
  }

  // 입력 변경 핸들러
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // 데이터 검증
      if (!formData.name?.trim()) {
        throw new Error('이름은 필수입니다.');
      }

      // 타입별 추가 검증 (생성 시에만)
      if (type === 'model' && !parentItem?.id && action === 'add') {
        throw new Error('차량 라인을 선택해주세요.');
      }
      if (type === 'trim' && !parentItem?.id && action === 'add') {
        throw new Error('모델을 선택해주세요.');
      }
      if (type === 'option' && !parentItem?.id && action === 'add') {
        throw new Error('트림을 선택해주세요.');
      }

      // 제출 데이터 준비
      const submitData = { ...formData };
      
      // 수정 시에는 불필요한 필드 제거
      if (action === 'edit') {
        // 브랜드 수정 시 version_id 제거
        if (type === 'brand') {
          delete submitData.version_id;
        }
        // 자동차 라인 수정 시 관계 필드 제거
        else if (type === 'vehicleLine') {
          delete submitData.brand_id;
        }
        // 모델 수정 시 관계 필드들 제거
        else if (type === 'model') {
          delete submitData.vehicle_line_id;
          delete submitData.brand_id;
        }
        // 트림 수정 시 관계 필드 제거
        else if (type === 'trim') {
          delete submitData.model_id;
        }
        // 옵션 수정 시 관계 필드 및 불필요한 필드 제거
        else if (type === 'option') {
          delete submitData.trim_id;
          delete submitData.release_year; // 옵션에는 없는 필드
        }
      }
      
      // 부모 ID 추가
      if (type === 'vehicleLine') {
        if (action === 'add') {
          submitData.brand_id = parentItem.id; // 브랜드 ID 추가
        }
        // 수정 시에는 brand_id를 제거 (백엔드에서 업데이트하지 않음)
      } else if (type === 'model') {
        if (action === 'add') {
          submitData.vehicle_line_id = parentItem.id;
          submitData.brand_id = parentItem.brand_id; // 브랜드 ID 추가
        }
        // 수정 시에는 vehicle_line_id와 brand_id를 제거 (백엔드에서 업데이트하지 않음)
      } else if (type === 'trim') {
        if (action === 'add') {
          submitData.model_id = parentItem.id;
        }
        // 수정 시에는 model_id를 제거 (백엔드에서 업데이트하지 않음)
      } else if (type === 'option') {
        if (action === 'add') {
          submitData.trim_id = parentItem.id;
        }
        // 수정 시에는 trim_id를 제거 (백엔드에서 업데이트하지 않음)
      }

      await onSubmit(submitData);
      
      // 새로고침 완료 후 모달 닫기
      setTimeout(() => {
        onClose();
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 삭제 핸들러
  const handleDelete = async () => {
    if (!window.confirm('정말로 삭제하시겠습니까?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onDelete();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // 삭제 액션인 경우 바로 삭제 처리
  if (action === 'delete') {
    handleDelete();
    return null;
  }

  const getTitle = () => {
    const actionText = action === 'edit' ? '수정' : '추가';
    const typeText = {
      brand: '브랜드',
      vehicleLine: '자동차 라인',
      model: '모델',
      trim: '트림',
      option: '옵션'
    }[type];
    return `${typeText} ${actionText}`;
  };

  const getFormFields = () => {
    const baseFields = [
      {
        key: 'name',
        label: '이름',
        type: 'text',
        required: true,
        placeholder: `${type === 'brand' ? '브랜드' : type === 'vehicleLine' ? '자동차 라인' : type === 'model' ? '모델' : type === 'trim' ? '트림' : '옵션'}명을 입력하세요`
      }
    ];

    switch (type) {
      case 'brand':
        return [
          ...baseFields,
          { key: 'country', label: '국가', type: 'text', placeholder: 'KR' },
          { key: 'logo_url', label: '로고 URL', type: 'url', placeholder: 'https://...' },
          { key: 'manager', label: '담당자', type: 'text', placeholder: '담당자명' }
        ];
      
      case 'vehicleLine':
        return [
          ...baseFields,
          { key: 'description', label: '설명', type: 'textarea', placeholder: '자동차 라인 설명' }
        ];
      
      case 'model':
        return [
          ...baseFields,
          { key: 'code', label: '코드', type: 'text', placeholder: '모델 코드' },
          { key: 'release_year', label: '출시년도', type: 'number', placeholder: '2024' },
          { key: 'price', label: '가격', type: 'number', placeholder: '30000000' },
          { key: 'foreign', label: '수입차', type: 'checkbox' }
        ];
      
      case 'trim':
        return [
          ...baseFields,
          { key: 'car_type', label: '차량타입', type: 'text', placeholder: '경_소형승용' },
          { key: 'fuel_name', label: '연료', type: 'text', placeholder: '가솔린' },
          { key: 'cc', label: '배기량', type: 'text', placeholder: '2.5' },
          { key: 'base_price', label: '기본가격', type: 'number', placeholder: '30000000' },
          { key: 'description', label: '설명', type: 'textarea', placeholder: '트림 설명' }
        ];
      
      case 'option':
        return [
          ...baseFields,
          { key: 'code', label: '코드', type: 'text', placeholder: '옵션 코드' },
          { key: 'description', label: '설명', type: 'textarea', placeholder: '옵션 설명' },
          { key: 'category', label: '카테고리', type: 'text', placeholder: '프리미엄' },
          { key: 'price', label: '가격', type: 'number', placeholder: '1000000' },
          { key: 'discounted_price', label: '할인가격', type: 'number', placeholder: '800000' }
        ];
      
      default:
        return baseFields;
    }
  };

  return (
    <div className="crud-modal-overlay" onClick={onClose}>
      <div className="crud-modal" onClick={(e) => e.stopPropagation()}>
        <div className="crud-modal-header">
          <h3>{getTitle()}</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="crud-modal-body">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {getFormFields().map(field => (
              <div key={field.key} className="form-field">
                <label>
                  {field.label}
                  {field.required && <span className="required">*</span>}
                </label>
                
                {field.type === 'textarea' ? (
                  <textarea
                    value={formData[field.key] || ''}
                    onChange={(e) => handleInputChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    required={field.required}
                    rows={3}
                  />
                ) : field.type === 'checkbox' ? (
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData[field.key] || false}
                      onChange={(e) => handleInputChange(field.key, e.target.checked)}
                    />
                    <span>{field.label}</span>
                  </label>
                ) : (
                  <input
                    type={field.type}
                    value={formData[field.key] || ''}
                    onChange={(e) => handleInputChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    required={field.required}
                  />
                )}
              </div>
            ))}

            <div className="form-actions">
              <button 
                type="button" 
                className="cancel-btn" 
                onClick={onClose}
                disabled={loading}
              >
                취소
              </button>
              
              {action === 'edit' && (
                <button 
                  type="button" 
                  className="delete-btn" 
                  onClick={handleDelete}
                  disabled={loading}
                >
                  {loading ? '삭제 중...' : '삭제'}
                </button>
              )}
              
              <button 
                type="submit" 
                className="submit-btn" 
                disabled={loading}
              >
                {loading ? '처리 중...' : (action === 'edit' ? '수정' : '추가')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CRUDModal;