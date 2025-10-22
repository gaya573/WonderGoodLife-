import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import mainDbAPI from '../services/mainDbApi';
import CRUDModal from '../components/modals/CRUDModal';
import './MainDBStatus.css';

/**
 * 메인 DB 현황 페이지 - VersionDataManagement와 동일한 구조로 통합
 */
function MainDBStatus() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // URL 파라미터에서 브랜드 ID 추출
  const brandId = parseInt(searchParams.get('brand_id')) || null;
  
  // 상태 관리
  const [mainDBData, setMainDBData] = useState(null);
  const [brandsData, setBrandsData] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [brandDetailsData, setBrandDetailsData] = useState(null);
  const [expandedModels, setExpandedModels] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 검색 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // CRUD 상태
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  
  // 메인 DB 현황 로드
  useEffect(() => {
  const loadMainDBStatus = async () => {
    try {
      setLoading(true);
        setError(null);
        
        const response = await mainDbAPI.getStatus();
        setMainDBData(response.data);
        
        // 브랜드 데이터 설정
        if (response.data.brands && response.data.brands.length > 0) {
          const sortedBrands = response.data.brands.sort((a, b) => {
            return a.name.localeCompare(b.name);
          });
          setBrandsData(sortedBrands);
          
          // URL에 브랜드 ID가 있으면 해당 브랜드 선택, 없으면 첫 번째 브랜드 선택
          let targetBrand = null;
          
          if (brandId) {
            targetBrand = sortedBrands.find(b => b.id === brandId);
          }
          
          if (!targetBrand && sortedBrands.length > 0) {
            targetBrand = sortedBrands[0];
            
            // URL 업데이트
            const newParams = new URLSearchParams(searchParams);
            newParams.set('brand_id', targetBrand.id);
            setSearchParams(newParams);
          }
          
          if (targetBrand) {
            setSelectedBrand(targetBrand);
            await loadBrandDetails(targetBrand.id);
          }
      }
      
    } catch (err) {
      console.error('메인 DB 현황 로드 실패:', err);
        setError('메인 DB 현황을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };
    
    loadMainDBStatus();
  }, [brandId, searchParams, setSearchParams]);

  // 브랜드별 상세 데이터 로드
  const loadBrandDetails = useCallback(async (brandId) => {
    try {
      const response = await mainDbAPI.getBrandDetails(brandId);
      setBrandDetailsData(response.data);
      
      // 해당 브랜드의 모든 모델을 초기에 펼침
      const allModelIds = new Set();
      if (response.data.vehicle_lines) {
        response.data.vehicle_lines.forEach(vehicleLine => {
          if (vehicleLine.models) {
            vehicleLine.models.forEach(model => {
              allModelIds.add(model.id);
            });
          }
        });
      }
      setExpandedModels(allModelIds);
      
      return response.data;
    } catch (err) {
      console.error('브랜드 상세 데이터 로드 실패:', err);
      return null;
    }
  }, []);

  // 모델/트림 검색 기능
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    
    if (!query.trim() || !brandDetailsData) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    // 선택된 브랜드의 모델과 트림에서 검색
    const results = [];
    
    if (brandDetailsData.vehicle_lines) {
      brandDetailsData.vehicle_lines.forEach(vehicleLine => {
        if (vehicleLine.models) {
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
            if (model.trims) {
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
            }
          });
        }
      });
    }
    
    setSearchResults(results);
    setShowSearchResults(results.length > 0);
  }, [brandDetailsData]);

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
        brand_id: selectedBrand?.id
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
    setShowDeleteModal(false);
    setEditingItem(null);
  }, []);

  // CRUD API 호출 핸들러들
  const handleCRUDSubmit = useCallback(async (formData) => {
    const { type, action, item, parentItem } = editingItem;

    try {
      if (action === 'add') {
        // 생성
      switch (type) {
        case 'brand':
            await mainDbAPI.createBrand(formData);
          break;
          case 'vehicleLine':
            await mainDbAPI.createVehicleLine(formData);
          break;
        case 'model':
            await mainDbAPI.createModel(formData);
          break;
        case 'trim':
            await mainDbAPI.createTrim(formData);
          break;
        case 'option':
            await mainDbAPI.createOption(formData);
          break;
        }
      } else if (action === 'edit') {
        // 수정
        switch (type) {
          case 'brand':
            await mainDbAPI.updateBrand(item.id, formData);
            break;
          case 'vehicleLine':
            await mainDbAPI.updateVehicleLine(item.id, formData);
            break;
          case 'model':
            await mainDbAPI.updateModel(item.id, formData);
            break;
          case 'trim':
            await mainDbAPI.updateTrim(item.id, formData);
            break;
          case 'option':
            await mainDbAPI.updateOption(item.id, formData);
            break;
        }
      }

      // 성공 후 데이터 새로고침
      console.log('CRUD 작업 완료, 데이터 새로고침 시작...');
      
      try {
        // 메인 DB 현황 새로고침
        const response = await mainDbAPI.getStatus();
        setMainDBData(response.data);
        
        if (response.data.brands && response.data.brands.length > 0) {
          const sortedBrands = response.data.brands.sort((a, b) => {
            return a.name.localeCompare(b.name);
          });
          setBrandsData(sortedBrands);
          
          // 현재 선택된 브랜드가 있으면 업데이트
          if (selectedBrand) {
            const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
            if (updatedBrand) {
              setSelectedBrand(updatedBrand);
              // 브랜드 상세 정보 새로고침
              await loadBrandDetails(updatedBrand.id);
      } else {
              // 브랜드가 삭제된 경우 첫 번째 브랜드 선택
              if (sortedBrands.length > 0) {
                const firstBrand = sortedBrands[0];
                setSelectedBrand(firstBrand);
                
                // URL 업데이트
                const newParams = new URLSearchParams(searchParams);
                newParams.set('brand_id', firstBrand.id);
                setSearchParams(newParams);
                
                await loadBrandDetails(firstBrand.id);
              } else {
                setSelectedBrand(null);
              }
            }
          }
        }
        
        console.log('데이터 새로고침 완료');
      } catch (error) {
        console.error('데이터 새로고침 실패:', error);
      }
      
    } catch (error) {
      console.error('CRUD 작업 실패:', error);
      throw error;
    }
  }, [editingItem, selectedBrand, loadBrandDetails]);

  const handleCRUDDelete = useCallback(async () => {
    const { type, item } = editingItem;

    try {
      switch (type) {
          case 'brand':
          await mainDbAPI.deleteBrand(item.id);
            break;
        case 'vehicleLine':
          await mainDbAPI.deleteVehicleLine(item.id);
            break;
          case 'model':
          await mainDbAPI.deleteModel(item.id);
            break;
          case 'trim':
          await mainDbAPI.deleteTrim(item.id);
            break;
          case 'option':
          await mainDbAPI.deleteOption(item.id);
            break;
      }

      // 성공 후 데이터 새로고침
      console.log('삭제 작업 완료, 데이터 새로고침 시작...');
      
      try {
        // 메인 DB 현황 새로고침
        const response = await mainDbAPI.getStatus();
        setMainDBData(response.data);
        
        if (response.data.brands && response.data.brands.length > 0) {
          const sortedBrands = response.data.brands.sort((a, b) => {
            return a.name.localeCompare(b.name);
          });
          setBrandsData(sortedBrands);
          
          // 현재 선택된 브랜드가 있으면 업데이트
          if (selectedBrand) {
            const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
            if (updatedBrand) {
              setSelectedBrand(updatedBrand);
              // 브랜드 상세 정보 새로고침
              await loadBrandDetails(updatedBrand.id);
            } else {
              // 브랜드가 삭제된 경우 첫 번째 브랜드 선택
              if (sortedBrands.length > 0) {
                const firstBrand = sortedBrands[0];
                setSelectedBrand(firstBrand);
                
                // URL 업데이트
                const newParams = new URLSearchParams(searchParams);
                newParams.set('brand_id', firstBrand.id);
                setSearchParams(newParams);
                
                await loadBrandDetails(firstBrand.id);
              } else {
                setSelectedBrand(null);
              }
            }
          }
        }
        
        console.log('삭제 후 데이터 새로고침 완료');
      } catch (error) {
        console.error('데이터 새로고침 실패:', error);
      }
      
    } catch (error) {
      console.error('삭제 작업 실패:', error);
      throw error;
    }
  }, [editingItem, selectedBrand, loadBrandDetails, searchParams, setSearchParams]);
      
  // 데이터 새로고침 함수
  const refreshData = useCallback(async () => {
    if (selectedBrand) {
      await loadBrandDetails(selectedBrand.id);
    }
    
    // 메인 DB 현황도 새로고침
    try {
      const response = await mainDbAPI.getStatus();
      setMainDBData(response.data);
      
      if (response.data.brands && response.data.brands.length > 0) {
        const sortedBrands = response.data.brands.sort((a, b) => {
          return a.name.localeCompare(b.name);
        });
        setBrandsData(sortedBrands);
        
        // 현재 선택된 브랜드가 있으면 업데이트
        if (selectedBrand) {
          const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
          if (updatedBrand) {
            setSelectedBrand(updatedBrand);
    } else {
            // 브랜드가 삭제되었거나 변경된 경우, 첫 번째 브랜드 선택
            if (sortedBrands.length > 0) {
              const firstBrand = sortedBrands[0];
              setSelectedBrand(firstBrand);
              
              // URL 업데이트
              const newParams = new URLSearchParams(searchParams);
              newParams.set('brand_id', firstBrand.id);
              setSearchParams(newParams);
              
              await loadBrandDetails(firstBrand.id);
            } else {
              setSelectedBrand(null);
            }
          }
        }
      }
    } catch (error) {
      console.error('데이터 새로고침 실패:', error);
    }
  }, [selectedBrand, loadBrandDetails, searchParams, setSearchParams]);

  // 브랜드 선택 핸들러
  const handleBrandSelect = useCallback(async (brand) => {
    setSelectedBrand(brand);
    
    // URL 업데이트
    const newParams = new URLSearchParams(searchParams);
    newParams.set('brand_id', brand.id);
    setSearchParams(newParams);
    
    await loadBrandDetails(brand.id);
  }, [searchParams, setSearchParams, loadBrandDetails]);

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
    if (!brandDetailsData) return;
    
    const allModelIds = new Set();
    if (brandDetailsData.vehicle_lines) {
      brandDetailsData.vehicle_lines.forEach(vehicleLine => {
        if (vehicleLine.models) {
          vehicleLine.models.forEach(model => {
            allModelIds.add(model.id);
          });
        }
      });
    }
    
    setExpandedModels(prev => {
      // 모든 모델이 펼쳐져 있으면 모두 접기, 아니면 모두 펼치기
      const isAllExpanded = allModelIds.size > 0 && 
        Array.from(allModelIds).every(id => prev.has(id));
      
      return isAllExpanded ? new Set() : allModelIds;
    });
  }, [brandDetailsData]);

  // 통계 계산
  const stats = useMemo(() => {
    if (!brandDetailsData) return null;
    
    let totalModels = 0;
    let totalTrims = 0;
    let totalOptions = 0;
    
    if (brandDetailsData.vehicle_lines) {
      brandDetailsData.vehicle_lines.forEach(vehicleLine => {
        if (vehicleLine.models) {
          totalModels += vehicleLine.models.length;
          vehicleLine.models.forEach(model => {
            if (model.trims) {
              totalTrims += model.trims.length;
              model.trims.forEach(trim => {
                if (trim.options) {
                  totalOptions += trim.options.length;
                }
              });
            }
          });
        }
      });
    }
    
    return {
      vehicleLines: brandDetailsData.vehicle_lines?.length || 0,
      models: totalModels,
      trims: totalTrims,
      options: totalOptions
    };
  }, [brandDetailsData]);

  // 새로고침 핸들러
  const handleRefresh = useCallback(async () => {
    await refreshData();
  }, [refreshData]);

  // 뒤로가기 핸들러
  const handleBackToVersions = useCallback(() => {
    navigate('/versions');
  }, [navigate]);

  if (loading) {
    return (
      <div className="main-db-status">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>메인 DB 현황을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="main-db-status">
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

  if (!mainDBData || mainDBData.is_empty) {
    return (
      <div className="main-db-status">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>데이터베이스에 아무것도 없습니다</h3>
          <p>메인 DB에 저장된 데이터가 없습니다.</p>
          <p>버전 관리 페이지에서 데이터를 메인 DB로 푸시해보세요.</p>
          <div className="empty-actions">
            <button 
              onClick={handleBackToVersions}
              className="go-to-versions-btn"
            >
              📋 버전 관리로 이동
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-db-status">
      <div className="header-section">
        <h1>메인 DB 현황</h1>
        
        <div className="header-controls">
          {/* 새로고침 버튼 */}
          <div className="refresh-section">
            <button 
              onClick={handleRefresh}
              className="refresh-btn"
            >
              🔄 새로고침
            </button>
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
          
          {/* 뒤로가기 버튼 */}
          <button 
            onClick={handleBackToVersions}
            className="back-btn"
          >
            ← 버전 관리로 돌아가기
          </button>
        </div>
      </div>

          {/* 브랜드 목록 - 상단에 고정 */}
      {brandsData.length > 0 && (
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
                          <span>{brand.vehicle_lines_count || 0}개 라인</span>
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
          )}

          {/* 선택된 브랜드의 상세 정보 */}
          {selectedBrand && brandDetailsData && (
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
                {brandDetailsData.vehicle_lines?.map(vehicleLine => (
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
                          onClick={async () => {
                            if (window.confirm(`'${vehicleLine.name}' 자동차 라인을 삭제하시겠습니까?`)) {
                              try {
                                await mainDbAPI.deleteVehicleLine(vehicleLine.id);
                                console.log('자동차 라인 삭제 완료, 새로고침 시작...');
                                
                                // 데이터 새로고침
                                const response = await mainDbAPI.getStatus();
                                setMainDBData(response.data);
                                
                                if (response.data.brands && response.data.brands.length > 0) {
                                  const sortedBrands = response.data.brands.sort((a, b) => {
                                    return a.name.localeCompare(b.name);
                                  });
                                  setBrandsData(sortedBrands);
                                  
                                  if (selectedBrand) {
                                    const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
                                    if (updatedBrand) {
                                      setSelectedBrand(updatedBrand);
                                      await loadBrandDetails(updatedBrand.id);
                                    }
                                  }
                                }
                                console.log('자동차 라인 삭제 후 새로고침 완료');
                              } catch (error) {
                                console.error('자동차 라인 삭제 실패:', error);
                                alert('삭제 중 오류가 발생했습니다: ' + error.message);
                              }
                            }
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
                      {vehicleLine.models?.map(model => (
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
                              <button 
                                className="delete-btn"
                            onClick={async (e) => {
                              e.stopPropagation();
                              if (window.confirm(`'${model.name}' 모델을 삭제하시겠습니까?`)) {
                                try {
                                  await mainDbAPI.deleteModel(model.id);
                                  console.log('모델 삭제 완료, 새로고침 시작...');
                                  
                                  // 데이터 새로고침
                                  const response = await mainDbAPI.getStatus();
                                  setMainDBData(response.data);
                                  
                                  if (response.data.brands && response.data.brands.length > 0) {
                                    const sortedBrands = response.data.brands.sort((a, b) => {
                                      return a.name.localeCompare(b.name);
                                    });
                                    setBrandsData(sortedBrands);
                                    
                                    if (selectedBrand) {
                                      const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
                                      if (updatedBrand) {
                                        setSelectedBrand(updatedBrand);
                                        await loadBrandDetails(updatedBrand.id);
                                      }
                                    }
                                  }
                                  console.log('모델 삭제 후 새로고침 완료');
                                } catch (error) {
                                  console.error('모델 삭제 실패:', error);
                                  alert('삭제 중 오류가 발생했습니다: ' + error.message);
                                }
                              }
                            }}
                                title="모델 삭제"
                              >
                                🗑️
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
                                <h5>트림 ({model.trims?.length || 0}개)</h5>
                                {model.trims?.map(trim => (
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
                                        <button 
                                          className="delete-btn"
                                          onClick={async () => {
                                            if (window.confirm(`'${trim.name}' 트림을 삭제하시겠습니까?`)) {
                                              try {
                                                await mainDbAPI.deleteTrim(trim.id);
                                                console.log('트림 삭제 완료, 새로고침 시작...');
                                                
                                                // 데이터 새로고침
                                                const response = await mainDbAPI.getStatus();
                                                setMainDBData(response.data);
                                                
                                                if (response.data.brands && response.data.brands.length > 0) {
                                                  const sortedBrands = response.data.brands.sort((a, b) => {
                                                    return a.name.localeCompare(b.name);
                                                  });
                                                  setBrandsData(sortedBrands);
                                                  
                                                  if (selectedBrand) {
                                                    const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
                                                    if (updatedBrand) {
                                                      setSelectedBrand(updatedBrand);
                                                      await loadBrandDetails(updatedBrand.id);
                                                    }
                                                  }
                                                }
                                                console.log('트림 삭제 후 새로고침 완료');
                                              } catch (error) {
                                                console.error('트림 삭제 실패:', error);
                                                alert('삭제 중 오류가 발생했습니다: ' + error.message);
                                              }
                                            }
                                          }}
                                          title="트림 삭제"
                                        >
                                          🗑️
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
                                    {trim.options && trim.options.length > 0 && (
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
                                                <button 
                                                  className="delete-btn"
                                              onClick={async () => {
                                                if (window.confirm(`'${option.name}' 옵션을 삭제하시겠습니까?`)) {
                                                  try {
                                                    await mainDbAPI.deleteOption(option.id);
                                                    console.log('옵션 삭제 완료, 새로고침 시작...');
                                                    
                                                    // 데이터 새로고침
                                                    const response = await mainDbAPI.getStatus();
                                                    setMainDBData(response.data);
                                                    
                                                    if (response.data.brands && response.data.brands.length > 0) {
                                                      const sortedBrands = response.data.brands.sort((a, b) => {
                                                        return a.name.localeCompare(b.name);
                                                      });
                                                      setBrandsData(sortedBrands);
                                                      
                                                      if (selectedBrand) {
                                                        const updatedBrand = sortedBrands.find(b => b.id === selectedBrand.id);
                                                        if (updatedBrand) {
                                                          setSelectedBrand(updatedBrand);
                                                          await loadBrandDetails(updatedBrand.id);
                                                        }
                                                      }
                                                    }
                                                    console.log('옵션 삭제 후 새로고침 완료');
                                                  } catch (error) {
                                                    console.error('옵션 삭제 실패:', error);
                                                    alert('삭제 중 오류가 발생했습니다: ' + error.message);
                                                  }
                                                }
                                              }}
                                                  title="옵션 삭제"
                                                >
                                                  🗑️
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

export default MainDBStatus;