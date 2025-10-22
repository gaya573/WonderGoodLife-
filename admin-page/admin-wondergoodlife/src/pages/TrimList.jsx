import { useState, useEffect } from 'react';
import { trimAPI, modelAPI } from '../services/api';
import './DataList.css';

const CAR_TYPES = ['경_소형승용', '중형승용', '대형승용', 'SUV_RV', '화물_승합'];

function TrimList() {
  const [trims, setTrims] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTrim, setEditingTrim] = useState(null);
  const [formData, setFormData] = useState({
    modelId: '',
    carType: 'SUV_RV',
    name: '',
    fuelName: '',
    cc: '',
    basePrice: '',
    description: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [trimsRes, modelsRes] = await Promise.all([
        trimAPI.getAll(),
        modelAPI.getAll(),
      ]);
      setTrims(trimsRes.data);
      setModels(modelsRes.data);
    } catch (error) {
      alert('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingTrim(null);
    setFormData({
      modelId: models[0]?.id || '',
      carType: 'SUV_RV',
      name: '',
      fuelName: '',
      cc: '',
      basePrice: '',
      description: '',
    });
    setShowModal(true);
  };

  const handleEdit = (trim) => {
    setEditingTrim(trim);
    setFormData({
      modelId: trim.modelId || trim.model?.id || '',
      carType: trim.carType || 'SUV_RV',
      name: trim.name || '',
      fuelName: trim.fuelName || '',
      cc: trim.cc || '',
      basePrice: trim.basePrice || '',
      description: trim.description || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까? 관련된 색상과 옵션도 함께 삭제됩니다.')) return;

    try {
      await trimAPI.delete(id);
      alert('삭제되었습니다.');
      loadData();
    } catch (error) {
      alert('삭제에 실패했습니다.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.modelId || !formData.carType) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    const submitData = {
      ...formData,
      modelId: parseInt(formData.modelId),
      basePrice: formData.basePrice ? parseInt(formData.basePrice.replace(/,/g, '')) : null,
    };

    try {
      if (editingTrim) {
        await trimAPI.update(editingTrim.id, submitData);
        alert('수정되었습니다.');
      } else {
        await trimAPI.create(submitData);
        alert('생성되었습니다.');
      }
      setShowModal(false);
      loadData();
    } catch (error) {
      alert('저장에 실패했습니다.');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getModelName = (trim) => {
    if (trim.modelName) return trim.modelName;
    if (trim.model?.name) return trim.model.name;
    const model = models.find(m => m.id === trim.modelId);
    return model?.name || '알 수 없음';
  };

  if (loading) {
    return <div className="loading">데이터를 불러오는 중...</div>;
  }

  return (
    <div className="data-list">
      <div className="page-header">
        <div>
          <h1>트림 관리</h1>
          <p>차량 트림 정보를 관리합니다</p>
        </div>
        <button className="create-btn" onClick={handleCreate}>
          + 새 트림 등록
        </button>
      </div>

      <div className="data-grid">
        {trims.length === 0 ? (
          <div className="empty-state">
            <p>등록된 트림이 없습니다.</p>
            <button className="create-btn" onClick={handleCreate}>
              첫 트림 등록하기
            </button>
          </div>
        ) : (
          trims.map((trim) => (
            <div key={trim.id} className="data-card">
              <div className="card-content">
                <h3>{trim.name}</h3>
                <p className="card-detail">
                  <span className="card-badge badge-primary">{getModelName(trim)}</span>
                  <span className="card-badge badge-success">{trim.carType}</span>
                </p>
                {trim.fuelName && (
                  <p className="card-detail">연료: {trim.fuelName}</p>
                )}
                {trim.cc && (
                  <p className="card-detail">배기량: {trim.cc}cc</p>
                )}
                {trim.basePrice && (
                  <p className="card-detail">
                    가격: {trim.basePrice.toLocaleString()}원
                  </p>
                )}
                {trim.description && (
                  <p className="card-detail" style={{ fontSize: '0.8rem', color: '#999' }}>
                    {trim.description}
                  </p>
                )}
              </div>
              <div className="card-actions">
                <button className="edit-btn" onClick={() => handleEdit(trim)}>
                  수정
                </button>
                <button className="delete-btn" onClick={() => handleDelete(trim.id)}>
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
              <h2>{editingTrim ? '트림 수정' : '새 트림 등록'}</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>모델 *</label>
                <select
                  name="modelId"
                  value={formData.modelId}
                  onChange={handleChange}
                  required
                >
                  <option value="">선택하세요</option>
                  {models.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>차종 *</label>
                <select
                  name="carType"
                  value={formData.carType}
                  onChange={handleChange}
                  required
                >
                  {CAR_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>트림명 *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="예: 프리미엄, 노블레스"
                  required
                />
              </div>
              <div className="form-group">
                <label>연료</label>
                <input
                  type="text"
                  name="fuelName"
                  value={formData.fuelName}
                  onChange={handleChange}
                  placeholder="예: 가솔린, 디젤, LPG"
                />
              </div>
              <div className="form-group">
                <label>배기량</label>
                <input
                  type="text"
                  name="cc"
                  value={formData.cc}
                  onChange={handleChange}
                  placeholder="예: 2000"
                />
              </div>
              <div className="form-group">
                <label>기본 가격</label>
                <input
                  type="text"
                  name="basePrice"
                  value={formData.basePrice}
                  onChange={handleChange}
                  placeholder="예: 35000000"
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="트림에 대한 상세 설명"
                  rows="4"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowModal(false)}>
                  취소
                </button>
                <button type="submit" className="submit-btn">
                  {editingTrim ? '수정' : '등록'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrimList;

