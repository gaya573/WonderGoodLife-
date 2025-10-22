import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import versionAPI from '../services/versionApi';
import CRUDModal from '../components/modals/CRUDModal';
import './VersionDataManagement.css';

/**
 * 브랜드 중심 버전 데이터 관리 페이지
 * URL 파라미터로 브랜드를 받고, 초기에 모델을 풀어서 표시
 */
function VersionDataManagement() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // URL 파라미터에서 버전 ID와 브랜드명 추출
  const versionId = parseInt(searchParams.get('version_id')) || null;
  const brandName = searchParams.get('brand') || null;
  
  // 상태 관리
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [brandsData, setBrandsData] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [expandedModels, setExpandedModels] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 검색 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // CRUD 상태
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  
  // 버전 목록 로드
  useEffect(() => {
    const loadVersions = async () => {
      try {
        const response = await versionAPI.getAll({ skip: 0, limit: 50 });
        setVersions(response.data.items);
        
        // URL에 버전 ID가 있으면 해당 버전 선택
        if (versionId) {
          const version = response.data.items.find(v => v.id === versionId);
          if (version) {
            setSelectedVersion(version);
          }
        }
      } catch (err) {
        console.error('버전 목록 로드 실패:', err);
        setError('버전 목록을 불러오는데 실패했습니다.');
      }
    };
    
    loadVersions();
  }, [versionId]);
  
  // 브랜드 데이터 로드
  useEffect(() => {
    if (!selectedVersion?.id) return;
    
    const loadBrandsData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await versionAPI.getBrandsWithFullData(selectedVersion.id, {
          // brand_name: brandName, // 모든 브랜드를 가져오기 위해 필터 제거
          page: 1,
          limit: 50 // 모든 브랜드 로드
        });
        
        // 브랜드를 이름순으로 정렬하고 현대를 맨 앞으로
        const sortedBrands = response.data.brands.sort((a, b) => {
          // 현대를 맨 앞으로
          if (a.name.includes('현대') && !b.name.includes('현대')) return -1;
          if (!a.name.includes('현대') && b.name.includes('현대')) return 1;
          // 나머지는 이름순 정렬
          return a.name.localeCompare(b.name);
        });
        
        setBrandsData(sortedBrands);
        
        // URL에 브랜드명이 있으면 해당 브랜드 선택, 없으면 첫 번째 브랜드(현대) 선택
        let targetBrand = null;
        
        if (brandName) {
          targetBrand = sortedBrands.find(b => 
            b.name.toLowerCase().includes(brandName.toLowerCase())
          );
        }
        
        if (!targetBrand && sortedBrands.length > 0) {
          targetBrand = sortedBrands[0]; // 현대가 첫 번째
          
          // URL 업데이트
          const newParams = new URLSearchParams(searchParams);
          newParams.set('brand', targetBrand.name);
          setSearchParams(newParams);
        }
        
        if (targetBrand) {
          setSelectedBrand(targetBrand);
          
          // 해당 브랜드의 모든 모델을 초기에 펼침
          const allModelIds = new Set();
          targetBrand.vehicle_lines.forEach(vehicleLine => {
            vehicleLine.models.forEach(model => {
              allModelIds.add(model.id);
            });
          });
          setExpandedModels(allModelIds);
        }
      } catch (err) {
        console.error('브랜드 데이터 로드 실패:', err);
        setError('브랜드 데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadBrandsData();
  }, [selectedVersion?.id, brandName, searchParams, setSearchParams]);
  
  // 모델/트림 검색 기능
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    
    if (!query.trim() || !selectedBrand) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    // 선택된 브랜드의 모델과 트림에서 검색
    const results = [];
    
    selectedBrand.vehicle_lines.forEach(vehicleLine => {
      vehicleLine.models.forEach(model => {
        // 모델명으로 검색
        if (model.name.toLowerCase().includes(query.toLowerCase())) {
          results.push({
            type: 'model',
            id: model.id,
            name: model.name,
            vehicleLine: vehicleLine.name,
            model: model
          });
        }
        
        // 트림명으로 검색
        model.trims.forEach(trim => {
          if (trim.name.toLowerCase().includes(query.toLowerCase())) {
            results.push({
              type: 'trim',
              id: trim.id,
              name: trim.name,
              vehicleLine: vehicleLine.name,
              model: model.name,
              trim: trim
            });
          }
        });
      });
    });
    
    setSearchResults(results);
    setShowSearchResults(results.length > 0);
  }, [selectedBrand]);
  
  // 검색 결과 클릭 시 해당 모델/트림으로 스크롤
  const handleSearchResultClick = useCallback((result) => {
    setSearchQuery('');
    setShowSearchResults(false);
    
    // 해당 모델을 펼치고 스크롤
    if (result.type === 'model') {
      setExpandedModels(prev => new Set([...prev, result.id]));
      
      setTimeout(() => {
        const modelElement = document.querySelector(`[data-model-id="${result.id}"]`);
        if (modelElement) {
          modelElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }
      }, 100);
    } else if (result.type === 'trim') {
      // 트림의 모델을 펼치고 스크롤
      const modelId = result.trim.model_id;
      setExpandedModels(prev => new Set([...prev, modelId]));
      
      setTimeout(() => {
        const trimElement = document.querySelector(`[data-trim-id="${result.id}"]`);
        if (trimElement) {
          trimElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }
      }, 200);
    }
  }, []);
  
  // CRUD 기능들
  const handleAddBrand = useCallback(() => {
    setEditingItem({ type: 'brand', action: 'add' });
    setShowAddModal(true);
  }, []);
  
  const handleEditBrand = useCallback((brand) => {
    setEditingItem({ type: 'brand', action: 'edit', item: brand });
    setShowAddModal(true);
  }, []);
  
  const handleAddVehicleLine = useCallback(() => {
    setEditingItem({
      type: 'vehicleLine',
      action: 'add',
      parentItem: selectedBrand
    });
    setShowAddModal(true);
  }, [selectedBrand]);

  const handleEditVehicleLine = useCallback((vehicleLine) => {
    setEditingItem({
      type: 'vehicleLine',
      action: 'edit',
      item: vehicleLine,
      parentItem: selectedBrand
    });
    setShowAddModal(true);
  }, [selectedBrand]);

  const handleAddModel = useCallback((vehicleLine) => {
    setEditingItem({
      type: 'model',
      action: 'add',
      parentItem: {
        ...vehicleLine,
        brand_id: selectedBrand?.id // 브랜드 ID 추가
      }
    });
    setShowAddModal(true);
  }, [selectedBrand]);
  
  const handleEditModel = useCallback((model) => {
    setEditingItem({ type: 'model', action: 'edit', item: model });
    setShowAddModal(true);
  }, []);
  
  const handleAddTrim = useCallback((model) => {
    setEditingItem({ type: 'trim', action: 'add', parentItem: model });
    setShowAddModal(true);
  }, []);
  
  const handleEditTrim = useCallback((trim) => {
    setEditingItem({ type: 'trim', action: 'edit', item: trim });
    setShowAddModal(true);
  }, []);
  
  const handleAddOption = useCallback((trim) => {
    setEditingItem({ type: 'option', action: 'add', parentItem: trim });
    setShowAddModal(true);
  }, []);
  
  const handleEditOption = useCallback((option) => {
    setEditingItem({ type: 'option', action: 'edit', item: option });
    setShowAddModal(true);
  }, []);
  
  // 모달 닫기
  const closeModals = useCallback(() => {
    setShowAddModal(false);
    setEditingItem(null);
  }, []);

  // CRUD API 호출 핸들러들
  const handleCRUDSubmit = useCallback(async (formData) => {
    if (!selectedVersion?.id) {
      throw new Error('버전이 선택되지 않았습니다.');
    }

    const { type, action, item, parentItem } = editingItem;

    try {
        if (action === 'add') {
          // 생성
          switch (type) {
            case 'brand':
              await versionAPI.createBrand(selectedVersion.id, formData);
              break;
            case 'vehicleLine':
              await versionAPI.createVehicleLine(selectedVersion.id, formData);
              break;
            case 'model':
              await versionAPI.createModel(selectedVersion.id, formData);
              break;
            case 'trim':
              await versionAPI.createTrim(selectedVersion.id, formData);
              break;
            case 'option':
              await versionAPI.createOption(selectedVersion.id, formData);
              break;
          }
        } else if (action === 'edit') {
          // 수정
          switch (type) {
            case 'brand':
              await versionAPI.updateBrand(selectedVersion.id, item.id, formData);
              break;
            case 'vehicleLine':
              await versionAPI.updateVehicleLine(selectedVersion.id, item.id, formData);
              break;
            case 'model':
              await versionAPI.updateModel(selectedVersion.id, item.id, formData);
              break;
            case 'trim':
              await versionAPI.updateTrim(selectedVersion.id, item.id, formData);
              break;
            case 'option':
              await versionAPI.updateOption(selectedVersion.id, item.id, formData);
              break;
          }
        }

      // 성공 후 데이터 새로고침
      await refreshBrandsData();
      
    } catch (error) {
      console.error('CRUD 작업 실패:', error);
      throw error;
    }
  }, [selectedVersion?.id, editingItem]);

  const handleCRUDDelete = useCallback(async () => {
    if (!selectedVersion?.id) {
      throw new Error('버전이 선택되지 않았습니다.');
    }

    const { type, item } = editingItem;

    try {
      switch (type) {
        case 'brand':
          await versionAPI.deleteBrand(selectedVersion.id, item.id);
          break;
        case 'vehicleLine':
          await versionAPI.deleteVehicleLine(selectedVersion.id, item.id);
          break;
        case 'model':
          await versionAPI.deleteModel(selectedVersion.id, item.id);
          break;
        case 'trim':
          await versionAPI.deleteTrim(selectedVersion.id, item.id);
          break;
        case 'option':
          await versionAPI.deleteOption(selectedVersion.id, item.id);
          break;
      }

      // 성공 후 데이터 새로고침
      await refreshBrandsData();
      
    } catch (error) {
      console.error('삭제 작업 실패:', error);
      throw error;
    }
  }, [selectedVersion?.id, editingItem]);

  // 브랜드 데이터 새로고침
  const refreshBrandsData = useCallback(async () => {
    if (!selectedVersion?.id) return;

    try {
      // 캐시 무시하고 강제 새로고침을 위해 타임스탬프 추가
      const response = await versionAPI.getBrandsWithFullData(selectedVersion.id, {
        page: 1,
        limit: 50,
        _t: Date.now() // 캐시 무시를 위한 타임스탬프
      });
      
      const sortedBrands = response.data.brands.sort((a, b) => {

        return a.name.localeCompare(b.name);
      });
      
      setBrandsData(sortedBrands);
      
      // 현재 선택된 브랜드가 있으면 업데이트
      if (selectedBrand) {
        const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
        if (updatedBrand) {
          setSelectedBrand(updatedBrand);
          
          // 해당 브랜드의 모든 모델을 펼치기
          const allModelIds = new Set();
          updatedBrand.vehicle_lines.forEach(vehicleLine => {
            vehicleLine.models.forEach(model => {
              allModelIds.add(model.id);
            });
          });
          setExpandedModels(allModelIds);
        } else {
          // 브랜드가 삭제되었거나 변경된 경우, 첫 번째 브랜드 선택
          if (sortedBrands.length > 0) {
            const firstBrand = sortedBrands[0];
            setSelectedBrand(firstBrand);
            
            // URL 업데이트
            const newParams = new URLSearchParams(searchParams);
            newParams.set('brand', firstBrand.name);
            setSearchParams(newParams);
            
            // 모든 모델 펼치기
            const allModelIds = new Set();
            firstBrand.vehicle_lines.forEach(vehicleLine => {
              vehicleLine.models.forEach(model => {
                allModelIds.add(model.id);
              });
            });
            setExpandedModels(allModelIds);
          } else {
            setSelectedBrand(null);
          }
        }
      }
    } catch (error) {
      console.error('데이터 새로고침 실패:', error);
    }
  }, [selectedVersion?.id, selectedBrand, searchParams, setSearchParams]);
  
  // 버전 변경 핸들러
  const handleVersionChange = useCallback((version) => {
    setSelectedVersion(version);
    setBrandsData([]);
    setSelectedBrand(null);
    setExpandedModels(new Set());
    
    // URL 업데이트
    const newParams = new URLSearchParams(searchParams);
    newParams.set('version_id', version.id);
    if (brandName) {
      newParams.set('brand', brandName);
    }
    setSearchParams(newParams);
  }, [searchParams, setSearchParams, brandName]);
  
  // 브랜드 선택 핸들러
  const handleBrandSelect = useCallback((brand) => {
    setSelectedBrand(brand);
    
    // URL 업데이트
    const newParams = new URLSearchParams(searchParams);
    newParams.set('brand', brand.name);
    setSearchParams(newParams);
    
    // 해당 브랜드의 모든 모델을 펼침
    const allModelIds = new Set();
    brand.vehicle_lines.forEach(vehicleLine => {
      vehicleLine.models.forEach(model => {
        allModelIds.add(model.id);
      });
    });
    setExpandedModels(allModelIds);
  }, [searchParams, setSearchParams]);
  
  // 모델 펼치기/접기 핸들러
  const toggleModel = useCallback((modelId) => {
    setExpandedModels(prev => {
      const newSet = new Set(prev);
      if (newSet.has(modelId)) {
        newSet.delete(modelId);
      } else {
        newSet.add(modelId);
      }
      return newSet;
    });
  }, []);
  
  // 모든 모델 펼치기/접기
  const toggleAllModels = useCallback(() => {
    if (!selectedBrand) return;
    
    const allModelIds = new Set();
    selectedBrand.vehicle_lines.forEach(vehicleLine => {
      vehicleLine.models.forEach(model => {
        allModelIds.add(model.id);
      });
    });
    
    setExpandedModels(prev => {
      // 모든 모델이 펼쳐져 있으면 모두 접기, 아니면 모두 펼치기
      const isAllExpanded = allModelIds.size > 0 && 
        Array.from(allModelIds).every(id => prev.has(id));
      
      return isAllExpanded ? new Set() : allModelIds;
    });
  }, [selectedBrand]);
  
  // 통계 계산
  const stats = useMemo(() => {
    if (!selectedBrand) return null;
    
    let totalModels = 0;
    let totalTrims = 0;
    let totalOptions = 0;
    
    selectedBrand.vehicle_lines.forEach(vehicleLine => {
      totalModels += vehicleLine.models.length;
      vehicleLine.models.forEach(model => {
        totalTrims += model.trims.length;
        model.trims.forEach(trim => {
          totalOptions += trim.options.length;
        });
      });
    });
    
    return {
      vehicleLines: selectedBrand.vehicle_lines.length,
      models: totalModels,
      trims: totalTrims,
      options: totalOptions
    };
  }, [selectedBrand]);
  
  if (loading) {
    return (
      <div className="version-data-management">
      <div className="loading-container">
        <div className="loading-spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
  return (
      <div className="version-data-management">
        <div className="error-container">
          <h2>오류 발생</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            새로고침
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="version-data-management">
      <div className="header-section">
        <h1>버전 데이터 관리</h1>
        
        <div className="header-controls">
          {/* 버전 선택 */}
          <div className="version-selector">
            <label>버전 선택:</label>
            <select 
              value={selectedVersion?.id || ''} 
              onChange={(e) => {
                const version = versions.find(v => v.id === parseInt(e.target.value));
                if (version) handleVersionChange(version);
              }}
            >
              {versions.map(version => (
                <option key={version.id} value={version.id}>
                  {version.version_name}
                </option>
              ))}
            </select>
          </div>
          
          {/* 검색창 */}
          <div className="search-container">
            <input
              type="text"
              placeholder="모델명 또는 트림명으로 검색..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              onFocus={() => {
                if (searchResults.length > 0) {
                  setShowSearchResults(true);
                }
              }}
              onBlur={() => {
                // 약간의 지연을 두고 검색 결과를 숨김 (클릭 이벤트 처리용)
                setTimeout(() => {
                  setShowSearchResults(false);
                }, 200);
              }}
              className="search-input"
            />
            {showSearchResults && (
              <div className="search-results">
                {searchResults.map(result => (
                  <div 
                    key={`${result.type}-${result.id}`}
                    className="search-result-item"
                    onClick={() => handleSearchResultClick(result)}
                  >
                    <div className="search-result-name">
                      {result.type === 'model' ? '🚗' : '⚙️'} {result.name}
                    </div>
                    <div className="search-result-details">
                      {result.type === 'model' ? (
                        <span>모델 • {result.vehicleLine}</span>
                      ) : (
                        <span>트림 • {result.model} • {result.vehicleLine}</span>
                      )}
                    </div>
                  </div>
                ))}
          </div>
        )}
          </div>
          
          {/* 브랜드 추가 버튼 */}
          {selectedVersion && (
            <button 
              className="add-brand-btn"
              onClick={handleAddBrand}
            >
              + 브랜드 추가
            </button>
          )}
        </div>
      </div>

      {selectedVersion && (
        <>
          {/* 브랜드 목록 - 상단에 고정 */}
          <div className="brands-section-top">
            <h2>전체 브랜드 목록</h2>
            <div className="brands-horizontal-scroll">
              {brandsData.map(brand => (
                <div 
                  key={brand.id}
                  data-brand-id={brand.id}
                  className={`brand-card-horizontal ${selectedBrand?.id === brand.id ? 'selected' : ''}`}
                >
                  <div className="brand-card-content" onClick={() => handleBrandSelect(brand)}>
                    <div className="brand-logo">
                      {brand.logo_url ? (
                        <img src={brand.logo_url} alt={brand.name} />
                      ) : (
                        <div className="brand-logo-placeholder">
                          {brand.name.charAt(0)}
                        </div>
                      )}
                    </div>
                    <div className="brand-info">
                      <h3>{brand.name}</h3>
                      <p>{brand.country}</p>
                      <div className="brand-stats-small">
                        <span>{brand.vehicle_lines.length}개 라인</span>
                      </div>
                    </div>
                  </div>
                  <div className="brand-actions">
                    <button 
                      className="edit-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditBrand(brand);
                      }}
                      title="브랜드 수정"
                    >
                      ✏️
                    </button>
                  </div>
              </div>
              ))}
            </div>
          </div>

          {/* 선택된 브랜드의 상세 정보 */}
          {selectedBrand && (
            <div className="brand-detail-section">
              <div className="brand-header">
                <h2>{selectedBrand.name} 상세 정보</h2>
                <div className="brand-actions">
                  <button onClick={toggleAllModels}>
                    {expandedModels.size > 0 ? '모든 모델 접기' : '모든 모델 펼치기'}
                  </button>
                </div>
              </div>
              
              {/* 통계 */}
              {stats && (
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>차량 라인</h3>
                    <span className="stat-number">{stats.vehicleLines}</span>
                  </div>
                  <div className="stat-card">
                    <h3>모델</h3>
                    <span className="stat-number">{stats.models}</span>
                  </div>
                  <div className="stat-card">
                    <h3>트림</h3>
                    <span className="stat-number">{stats.trims}</span>
                  </div>
                  <div className="stat-card">
                    <h3>옵션</h3>
                    <span className="stat-number">{stats.options}</span>
                  </div>
                </div>
              )}
              
              {/* 차량 라인별 모델 목록 */}
              <div className="vehicle-lines-section">
                {selectedBrand.vehicle_lines.map(vehicleLine => (
                  <div key={vehicleLine.id} className="vehicle-line-card">
                    <div className="vehicle-line-header">
                      <h3>{vehicleLine.name}</h3>
                      <div className="vehicle-line-actions">
                        <button 
                          className="add-vehicle-line-small-btn"
                          onClick={handleAddVehicleLine}
                          title="새로운 자동차 라인 추가"
                        >
                          🚗 + 라인 추가
                        </button>
                        <button 
                          className="add-btn"
                          onClick={() => handleAddModel(vehicleLine)}
                          title="모델 추가"
                        >
                          + 모델
                        </button>
                        <button 
                          className="edit-btn"
                          onClick={() => handleEditVehicleLine(vehicleLine)}
                          title="자동차 라인 수정"
                        >
                          ✏️ 수정
                        </button>
                        <button 
                          className="delete-btn"
                          onClick={() => {
                            setEditingItem({ type: 'vehicleLine', action: 'delete', item: vehicleLine });
                            setShowDeleteModal(true);
                          }}
                          title="자동차 라인 삭제"
                        >
                          🗑️ 삭제
                        </button>
                      </div>
                    </div>
                    {vehicleLine.description && (
                      <p className="vehicle-line-description">{vehicleLine.description}</p>
                    )}
                    
                    <div className="models-section">
                      {vehicleLine.models.map(model => (
                        <div key={model.id} data-model-id={model.id} className="model-card">
                          <div className="model-header">
                            <div 
                              className="model-title"
                              onClick={() => toggleModel(model.id)}
                            >
                              <h4>{model.name}</h4>
                              <span className="toggle-icon">
                                {expandedModels.has(model.id) ? '▼' : '▶'}
                              </span>
                            </div>
                            <div className="model-actions">
                              <button 
                                className="add-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAddTrim(model);
                                }}
                                title="트림 추가"
                              >
                                + 트림
                              </button>
                              <button 
                                className="edit-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditModel(model);
                                }}
                                title="모델 수정"
                              >
                                ✏️
                              </button>
                            </div>
                          </div>
                          
                          {expandedModels.has(model.id) && (
                            <div className="model-details">
                              <div className="model-info">
                                <p>코드: {model.code || 'N/A'}</p>
                                <p>출시년도: {model.release_year || 'N/A'}</p>
                                <p>가격: {model.price ? `${model.price.toLocaleString()}원` : 'N/A'}</p>
                                <p>수입차: {model.foreign ? 'Yes' : 'No'}</p>
                              </div>
                              
                              {/* 트림 목록 */}
                              <div className="trims-section">
                                <h5>트림 ({model.trims.length}개)</h5>
                                {model.trims.map(trim => (
                                  <div key={trim.id} data-trim-id={trim.id} className="trim-card">
                                    <div className="trim-header">
                                      <h6>{model.name} {trim.name}</h6>
                                      <div className="trim-actions">
                                        <button 
                                          className="add-btn"
                                          onClick={() => handleAddOption(trim)}
                                          title="옵션 추가"
                                        >
                                          + 옵션
                                        </button>
                                        <button 
                                          className="edit-btn"
                                          onClick={() => handleEditTrim(trim)}
                                          title="트림 수정"
                                        >
                                          ✏️
                                        </button>
                                      </div>
          </div>
                                    <div className="trim-info">
                                      <p>차량타입: {trim.car_type || 'N/A'}</p>
                                      <p>연료: {trim.fuel_name || 'N/A'}</p>
                                      <p>배기량: {trim.cc || 'N/A'}</p>
                                      <p>기본가격: {trim.base_price ? `${trim.base_price.toLocaleString()}원` : 'N/A'}</p>
                                      {trim.description && (
                                        <p>설명: {trim.description}</p>
                                      )}
                                    </div>
                                    
                                    {/* 옵션 목록 */}
                                    {trim.options.length > 0 && (
                                      <div className="options-section">
                                        <h6>옵션 ({trim.options.length}개)</h6>
                                        <div className="options-grid">
                                          {trim.options.map(option => (
                                            <div key={option.id} className="option-card">
                                              <div className="option-content">
                                                <div className="option-name">{option.name}</div>
                                                {option.code && (
                                                  <div className="option-code">{option.code}</div>
                                                )}
                                                <div className="option-price">
                                                  {option.price ? `${option.price.toLocaleString()}원` : '가격 미정'}
                                                  {option.discounted_price && option.discounted_price !== option.price && (
                                                    <span className="discounted-price">
                                                      {option.discounted_price.toLocaleString()}원
                                                    </span>
                                                  )}
                                                </div>
                                                {option.category && (
                                                  <div className="option-category">{option.category}</div>
                                                )}
                                              </div>
                                              <div className="option-actions">
          <button 
                                                  className="edit-btn"
                                                  onClick={() => handleEditOption(option)}
                                                  title="옵션 수정"
          >
                                                  ✏️
          </button>
                                              </div>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
        </div>
      )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* CRUD 모달 */}
      <CRUDModal
        isOpen={showAddModal}
        onClose={closeModals}
        type={editingItem?.type}
        action={editingItem?.action}
        item={editingItem?.item}
        parentItem={editingItem?.parentItem}
        onSubmit={handleCRUDSubmit}
        onDelete={handleCRUDDelete}
      />
    </div>  
  );
}

export default VersionDataManagement;