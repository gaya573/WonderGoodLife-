import { useState, useEffect } from 'react';
import { modelAPI, brandAPI } from '../services/api';
import './DataList.css';

function ModelList() {
  const [models, setModels] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingModel, setEditingModel] = useState(null);
  const [formData, setFormData] = useState({
    brandId: '',
    name: '',
    code: '',
    releaseYear: '',
    price: '',
    foreign: false,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [modelsRes, brandsRes] = await Promise.all([
        modelAPI.getAll(),
        brandAPI.getAll(),
      ]);
      setModels(modelsRes.data);
      setBrands(brandsRes.data);
    } catch (error) {
      alert('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingModel(null);
    setFormData({
      brandId: brands[0]?.id || '',
      name: '',
      code: '',
      releaseYear: new Date().getFullYear(),
      price: '',
      foreign: false,
    });
    setShowModal(true);
  };

  const handleEdit = (model) => {
    setEditingModel(model);
    setFormData({
      brandId: model.brandId || model.brand?.id || '',
      name: model.name || '',
      code: model.code || '',
      releaseYear: model.releaseYear || '',
      price: model.price || '',
      foreign: model.foreign || false,
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까? 관련된 트림도 함께 삭제됩니다.')) return;

    try {
      await modelAPI.delete(id);
      alert('삭제되었습니다.');
      loadData();
    } catch (error) {
      alert('삭제에 실패했습니다.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.code || !formData.brandId) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    const submitData = {
      ...formData,
      brandId: parseInt(formData.brandId),
      releaseYear: formData.releaseYear ? parseInt(formData.releaseYear) : null,
      price: formData.price ? parseInt(formData.price.replace(/,/g, '')) : null,
    };

    try {
      if (editingModel) {
        await modelAPI.update(editingModel.id, submitData);
        alert('수정되었습니다.');
      } else {
        await modelAPI.create(submitData);
        alert('생성되었습니다.');
      }
      setShowModal(false);
      loadData();
    } catch (error) {
      alert('저장에 실패했습니다.');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const getBrandName = (model) => {
    if (model.brandName) return model.brandName;
    if (model.brand?.name) return model.brand.name;
    const brand = brands.find(b => b.id === model.brandId);
    return brand?.name || '알 수 없음';
  };

  if (loading) {
    return <div className="loading">데이터를 불러오는 중...</div>;
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
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '1.875rem',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '0.5rem'
            }}>
              모델 관리
            </h1>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '1rem'
            }}>
              차량 모델 정보를 관리합니다
            </p>
          </div>
          <button 
            onClick={handleCreate}
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
            새 모델 등록
          </button>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1.5rem'
      }}>
        {models.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '3rem',
            textAlign: 'center',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            gridColumn: '1 / -1'
          }}>
            <p style={{ 
              color: '#6b7280', 
              fontSize: '1.125rem', 
              margin: '0 0 1.5rem 0' 
            }}>
              등록된 모델이 없습니다.
            </p>
            <button 
              onClick={handleCreate}
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
              첫 모델 등록하기
            </button>
          </div>
        ) : (
          models.map((model) => (
            <div key={model.id} style={{
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
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{
                  margin: '0 0 0.5rem 0',
                  fontSize: '1.25rem',
                  fontWeight: '600',
                  color: '#111827'
                }}>
                  {model.name}
                </h3>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <span style={{
                    background: '#3b82f6',
                    color: 'white',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: '500'
                  }}>
                    {getBrandName(model)}
                  </span>
                  {model.foreign && (
                    <span style={{
                      background: '#f59e0b',
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}>
                      수입차
                    </span>
                  )}
                </div>
                <p style={{
                  margin: '0 0 0.5rem 0',
                  color: '#6b7280',
                  fontSize: '0.875rem'
                }}>
                  코드: {model.code}
                </p>
                {model.releaseYear && (
                  <p style={{
                    margin: '0 0 0.5rem 0',
                    color: '#6b7280',
                    fontSize: '0.875rem'
                  }}>
                    출시년도: {model.releaseYear}년
                  </p>
                )}
                {model.price && (
                  <p style={{
                    margin: '0 0 0.5rem 0',
                    color: '#6b7280',
                    fontSize: '0.875rem'
                  }}>
                    가격: {model.price.toLocaleString()}원
                  </p>
                )}
                {model.trimCount !== undefined && (
                  <p style={{
                    margin: 0,
                    color: '#6b7280',
                    fontSize: '0.875rem'
                  }}>
                    트림 수: {model.trimCount}개
                  </p>
                )}
              </div>
              <div style={{
                display: 'flex',
                gap: '0.5rem'
              }}>
                <button 
                  onClick={() => handleEdit(model)}
                  style={{
                    background: '#6b7280',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    flex: 1
                  }}
                  onMouseOver={(e) => e.target.style.background = '#4b5563'}
                  onMouseOut={(e) => e.target.style.background = '#6b7280'}
                >
                  수정
                </button>
                <button 
                  onClick={() => handleDelete(model.id)}
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    flex: 1
                  }}
                  onMouseOver={(e) => e.target.style.background = '#dc2626'}
                  onMouseOut={(e) => e.target.style.background = '#ef4444'}
                >
                  삭제
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingModel ? '모델 수정' : '새 모델 등록'}</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>브랜드 *</label>
                <select
                  name="brandId"
                  value={formData.brandId}
                  onChange={handleChange}
                  required
                >
                  <option value="">선택하세요</option>
                  {brands.map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>모델명 *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="예: 그랜저, 쏘나타"
                  required
                />
              </div>
              <div className="form-group">
                <label>모델 코드 *</label>
                <input
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  placeholder="예: GRANDEUR_2024"
                  required
                />
              </div>
              <div className="form-group">
                <label>출시년도</label>
                <input
                  type="number"
                  name="releaseYear"
                  value={formData.releaseYear}
                  onChange={handleChange}
                  placeholder="예: 2024"
                  min="1900"
                  max="2100"
                />
              </div>
              <div className="form-group">
                <label>가격</label>
                <input
                  type="text"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  placeholder="예: 35000000"
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="foreign"
                    checked={formData.foreign}
                    onChange={handleChange}
                  />
                  {' '}수입차
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowModal(false)}>
                  취소
                </button>
                <button type="submit" className="submit-btn">
                  {editingModel ? '수정' : '등록'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelList;

