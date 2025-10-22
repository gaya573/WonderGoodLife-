
/**
 * 브랜드 카드 컴포넌트
 * 개별 브랜드의 정보와 하위 모델들을 표시
 */
const BrandCard = ({ 
  brand, 
  brandIndex, 
  isLastBrand, 
  lastBrandElementRef,
  useSplitAPI,
  loadBrandModels,
  onAddModel,
  onEdit,
  onDelete,
  // CRUD 함수들
  createVehicleLine,
  editBrand,
  deleteBrand,
  createModel,
  editVehicleLine,
  deleteVehicleLine,
  editModel,
  deleteModel,
  createTrim,
  editTrim,
  deleteTrim,
  createOption,
  editOption,
  deleteOption
}) => {
  // 브랜드 렌더링 로그 제거

  return (
    <div 
      key={brand.id || `brand-${brandIndex}`} 
      ref={isLastBrand ? lastBrandElementRef : null}
      data-brand-id={brand.id}
      style={{
        background: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
        transition: 'box-shadow 0.3s ease'
      }}
    >
      {/* 브랜드 헤더 */}
      <div 
        style={{
          background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
          borderBottom: '1px solid #e5e7eb',
          padding: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: useSplitAPI && (!brand.vehicle_lines || brand.vehicle_lines.reduce((total, vl) => total + (vl.models?.length || 0), 0) === 0) ? 'pointer' : 'default'
        }}
        onClick={() => {
          if (useSplitAPI && (!brand.vehicle_lines || brand.vehicle_lines.reduce((total, vl) => total + (vl.models?.length || 0), 0) === 0)) {
            loadBrandModels(brand.id);
          }
        }}
      >
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '0.5rem'
          }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              padding: '0.25rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              브랜드
            </div>
            <h3 style={{ 
              margin: 0, 
              fontSize: '1.25rem', 
              fontWeight: '600', 
              color: 'white' 
            }}>
              {brand.name}
            </h3>
          </div>
          <p style={{ 
            margin: 0, 
            color: 'rgba(255, 255, 255, 0.9)', 
            fontSize: '0.875rem' 
          }}>
            국가: {brand.country} | 관리자: {brand.manager || 'N/A'} | 모델: {brand.vehicle_lines?.reduce((total, vl) => total + (vl.models?.length || 0), 0) || 0}개
            {useSplitAPI && (!brand.vehicle_lines || brand.vehicle_lines.reduce((total, vl) => total + (vl.models?.length || 0), 0) === 0) && (
              <span style={{ 
                marginLeft: '0.5rem', 
                fontSize: '0.75rem', 
                color: 'rgba(255, 255, 255, 0.7)',
                fontStyle: 'italic'
              }}>
                (클릭하여 모델 로드)
              </span>
            )}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            onClick={() => createVehicleLine(null, { brand_id: brand.id })}
            style={{ 
              background: '#10b981',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseOver={(e) => e.target.style.background = '#059669'}
            onMouseOut={(e) => e.target.style.background = '#10b981'}
          >
            차량라인 추가
          </button>
          <button 
            onClick={() => editBrand(brand)}
            style={{ 
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseOver={(e) => e.target.style.background = '#4b5563'}
            onMouseOut={(e) => e.target.style.background = '#6b7280'}
          >
            수정
          </button>
          <button 
            onClick={() => deleteBrand(brand)}
            style={{ 
              background: '#ef4444',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseOver={(e) => e.target.style.background = '#dc2626'}
            onMouseOut={(e) => e.target.style.background = '#ef4444'}
          >
            삭제
          </button>
        </div>
      </div>
      
      {/* 브랜드 상세 정보 */}
      <div className="brand-details" style={{
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '1rem',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div className="detail-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          <div className="detail-item" style={{
            background: '#f8fafc',
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>생성자</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              {brand.created_by_username || brand.created_by} ({brand.created_by_email || brand.created_by})
            </div>
          </div>
          <div className="detail-item" style={{
            background: '#f8fafc',
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>생성일</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              {brand.created_at ? new Date(brand.created_at).toLocaleString() : 'N/A'}
            </div>
          </div>
          {(brand.updated_by_username || brand.updated_by_email) && (
            <>
              <div className="detail-item" style={{
                background: '#f8fafc',
                padding: '0.75rem',
                borderRadius: '6px',
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>수정자</div>
                <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  {brand.updated_by_username || 'N/A'} ({brand.updated_by_email || 'N/A'})
                </div>
              </div>
              <div className="detail-item" style={{
                background: '#f8fafc',
                padding: '0.75rem',
                borderRadius: '6px',
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>수정일</div>
                <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  {brand.updated_at ? new Date(brand.updated_at).toLocaleString() : 'N/A'}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* 모델 목록 */}
      <div className="models-container" style={{
        background: 'rgba(255, 255, 255, 0.98)',
        borderRadius: '0 0 12px 12px',
        padding: '1rem'
      }}>
        {brand.vehicle_lines && brand.vehicle_lines.some(vl => vl.models && vl.models.length > 0) ? (
          <div>
            {brand.vehicle_lines.map(vehicleLine => (
              vehicleLine.models && vehicleLine.models.length > 0 && (
                <div key={vehicleLine.id} style={{ marginBottom: '1rem' }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '0.5rem',
                    paddingBottom: '0.25rem',
                    borderBottom: '1px solid #e5e7eb'
                  }}>
                    <h4 style={{ 
                      color: '#374151', 
                      fontSize: '0.875rem', 
                      fontWeight: '600',
                      margin: 0
                    }}>
                      {vehicleLine.name}
                    </h4>
                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                      <button 
                        onClick={() => createModel(null, { vehicle_line_id: vehicleLine.id })}
                        style={{ 
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.625rem',
                          cursor: 'pointer',
                          minWidth: '70px',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        모델 추가
                      </button>
                      <button 
                        onClick={() => editVehicleLine(vehicleLine)}
                        style={{ 
                          background: '#6b7280',
                          color: 'white',
                          border: 'none',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.625rem',
                          cursor: 'pointer',
                          minWidth: '50px',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        수정
                      </button>
                      <button 
                        onClick={() => deleteVehicleLine(vehicleLine)}
                        style={{ 
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.625rem',
                          cursor: 'pointer',
                          minWidth: '50px',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    {vehicleLine.models.map(model => (
                      <div key={model.id} data-model-id={model.id} style={{
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        padding: '0.75rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginBottom: '0.25rem'
                          }}>
                            <div style={{ fontWeight: '500', color: '#111827' }}>
                              {model.name}
                            </div>
                            <div style={{ display: 'flex', gap: '0.25rem' }}>
                              <button 
                                onClick={() => createTrim(null, { model_id: model.id })}
                                style={{ 
                                  background: '#10b981',
                                  color: 'white',
                                  border: 'none',
                                  padding: '0.25rem 0.5rem',
                                  borderRadius: '4px',
                                  fontSize: '0.625rem',
                                  cursor: 'pointer',
                                  minWidth: '70px',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                트림 추가
                              </button>
                              <button 
                                onClick={() => editModel(model)}
                                style={{ 
                                  background: '#6b7280',
                                  color: 'white',
                                  border: 'none',
                                  padding: '0.25rem 0.5rem',
                                  borderRadius: '4px',
                                  fontSize: '0.625rem',
                                  cursor: 'pointer',
                                  minWidth: '50px',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                수정
                              </button>
                              <button 
                                onClick={() => deleteModel(model)}
                                style={{ 
                                  background: '#ef4444',
                                  color: 'white',
                                  border: 'none',
                                  padding: '0.25rem 0.5rem',
                                  borderRadius: '4px',
                                  fontSize: '0.625rem',
                                  cursor: 'pointer',
                                  minWidth: '50px',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                삭제
                              </button>
                            </div>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                            코드: {model.code}
                          </div>
                          
                          {/* 트림 목록 표시 */}
                          {model.trims && model.trims.length > 0 && (
                            <div style={{ marginTop: '0.5rem' }}>
                              <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginBottom: '0.25rem' }}>
                                트림 ({model.trims.length}개):
                              </div>
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                                {model.trims.map(trim => {
                                  return (
                                <div key={trim.id} data-trim-id={trim.id} style={{
                                  background: '#f1f5f9',
                                  border: '1px solid #e2e8f0',
                                  borderRadius: '4px',
                                  padding: '0.5rem',
                                  marginBottom: '0.25rem',
                                  fontSize: '0.75rem'
                                }}>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    alignItems: 'center',
                                    marginBottom: '0.25rem'
                                  }}>
                                    <div style={{ fontWeight: '500', color: '#475569' }}>
                                      {trim.name}
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.125rem' }}>
                                      <button 
                                        onClick={() => createOption(null, { trim_id: trim.id })}
                                        style={{ 
                                          background: '#10b981',
                                          color: 'white',
                                          border: 'none',
                                          padding: '0.25rem 0.5rem',
                                          borderRadius: '4px',
                                          fontSize: '0.6rem',
                                          cursor: 'pointer',
                                          minWidth: '60px',
                                          whiteSpace: 'nowrap'
                                        }}
                                      >
                                        옵션 추가
                                      </button>
                                      <button 
                                        onClick={() => editTrim(trim)}
                                        style={{ 
                                          background: '#6b7280',
                                          color: 'white',
                                          border: 'none',
                                          padding: '0.25rem 0.5rem',
                                          borderRadius: '4px',
                                          fontSize: '0.6rem',
                                          cursor: 'pointer',
                                          minWidth: '50px',
                                          whiteSpace: 'nowrap'
                                        }}
                                      >
                                        수정
                                      </button>
                                      <button 
                                        onClick={() => deleteTrim(trim)}
                                        style={{ 
                                          background: '#ef4444',
                                          color: 'white',
                                          border: 'none',
                                          padding: '0.25rem 0.5rem',
                                          borderRadius: '4px',
                                          fontSize: '0.6rem',
                                          cursor: 'pointer',
                                          minWidth: '50px',
                                          whiteSpace: 'nowrap'
                                        }}
                                      >
                                        삭제
                                      </button>
                                    </div>
                                  </div>
                                  <div style={{ color: '#64748b', fontSize: '0.7rem' }}>
                                    {trim.car_type} | {trim.fuel_name} | {trim.cc}cc | 기본가격: {trim.base_price ? `${trim.base_price.toLocaleString()}원` : 'N/A'}
                                  </div>
                                  
                                  {/* 통합된 옵션 표시 */}
                                  {trim.options && trim.options.length > 0 && (
                                    <div style={{ marginTop: '0.25rem' }}>
                                      <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.125rem' }}>
                                        옵션 ({trim.options.length}개):
                                      </div>
                                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.25rem' }}>
                                        {trim.options.map(option => (
                                        <div key={option.id} style={{
                                          background: '#f8fafc',
                                          border: '1px solid #e2e8f0',
                                          borderRadius: '3px',
                                          padding: '0.25rem 0.375rem',
                                          marginBottom: '0.125rem',
                                          fontSize: '0.7rem'
                                        }}>
                                          <div style={{ 
                                            display: 'flex', 
                                            justifyContent: 'space-between', 
                                            alignItems: 'center',
                                            marginBottom: '0.125rem'
                                          }}>
                                            <div style={{ color: '#475569', fontWeight: '500' }}>
                                              {option.name}
                                            </div>
                                            <div style={{ display: 'flex', gap: '0.125rem' }}>
                                              <button 
                                                onClick={() => editOption(option)}
                                                style={{ 
                                                  background: '#6b7280',
                                                  color: 'white',
                                                  border: 'none',
                                                  padding: '0.125rem 0.25rem',
                                                  borderRadius: '3px',
                                                  fontSize: '0.55rem',
                                                  cursor: 'pointer',
                                                  minWidth: '40px',
                                                  whiteSpace: 'nowrap'
                                                }}
                                              >
                                                수정
                                              </button>
                                              <button 
                                                onClick={() => deleteOption(option)}
                                                style={{ 
                                                  background: '#ef4444',
                                                  color: 'white',
                                                  border: 'none',
                                                  padding: '0.125rem 0.25rem',
                                                  borderRadius: '3px',
                                                  fontSize: '0.55rem',
                                                  cursor: 'pointer',
                                                  minWidth: '40px',
                                                  whiteSpace: 'nowrap'
                                                }}
                                              >
                                                삭제
                                              </button>
                                            </div>
                                          </div>
                                          <div style={{ color: '#64748b', fontSize: '0.65rem' }}>
                                            {option.code && `코드: ${option.code} | `}
                                            가격: {option.price ? `${option.price.toLocaleString()}원` : 'N/A'}
                                            {option.discounted_price && ` (할인: ${option.discounted_price.toLocaleString()}원)`}
                                          </div>
                                          {option.description && (
                                            <div style={{ color: '#94a3b8', fontSize: '0.65rem', fontStyle: 'italic' }}>
                                              {option.description}
                                            </div>
                                          )}
                                        </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                                );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                       
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#6b7280', padding: '1rem' }}>
            <div style={{ marginBottom: '0.5rem' }}>
              이 브랜드에는 모델이 없습니다.
            </div>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              모델 추가 버튼을 클릭하여 새 모델을 추가하세요.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BrandCard;
