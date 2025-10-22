import BrandCard from './BrandCard';
import InfiniteScrollIndicator from './InfiniteScrollIndicator';

/**
 * 버전 데이터 관리 페이지 브랜드 리스트 컴포넌트
 * 브랜드 카드들과 무한 스크롤 기능을 관리
 */
function VersionDataBrandList({
  versionData,
  selectedVersion,
  useSplitAPI,
  loadingMore,
  hasMore,
  currentPage,
  totalPages,
  lastBrandElementRef,
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
  deleteOption,
  createBrand,
  // 검색 관련 props
  searchStats,
  isSearching,
  searchQuery
}) {
  // 검색어가 있고 결과가 없을 때
  const hasSearchQuery = searchQuery && searchQuery.trim().length > 0;
  if (hasSearchQuery && searchStats && searchStats.totalItems === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🔍</div>
        <h3 className="empty-title">검색 결과가 없습니다</h3>
        <p className="empty-description">검색 조건에 맞는 데이터를 찾을 수 없습니다.</p>
      </div>
    );
  }

  // 검색어가 있을 때는 브랜드 리스트를 숨김 (검색 결과는 SearchBox에서 처리)
  let displayBrands = versionData.brands || [];
  if (hasSearchQuery) {
    displayBrands = [];
  }

  // 빈 상태 렌더링
  if (!displayBrands || displayBrands.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🏢</div>
        <h3 className="empty-title">브랜드 데이터가 없습니다</h3>
        <p className="empty-description">이 버전에 등록된 브랜드가 없습니다.</p>
        <button 
          className="action-btn btn-edit"
          onClick={() => createBrand(null, { version_id: selectedVersion.id })}
        >
          📝 브랜드 추가하기
        </button>
      </div>
    );
  }

  return (
    <div className="brand-hierarchy-view">
      {displayBrands.map((brand, brandIndex) => {
        const isLastBrand = brandIndex === displayBrands.length - 1;
        
        // 고유한 키 생성 (브랜드 ID + 인덱스 조합)
        const uniqueKey = `brand-${brand.id}-${brandIndex}-${Date.now()}`;
        
        return (
          <div key={uniqueKey} data-brand-id={brand.id}>
            <BrandCard
              brand={brand}
              brandIndex={brandIndex}
              isLastBrand={isLastBrand}
              lastBrandElementRef={lastBrandElementRef}
              useSplitAPI={useSplitAPI}
              loadBrandModels={loadBrandModels}
              onAddModel={(brand) => onAddModel(brand, 'models')}
              onEdit={onEdit}
              onDelete={onDelete}
              // CRUD 함수들
              createVehicleLine={createVehicleLine}
              editBrand={editBrand}
              deleteBrand={deleteBrand}
              createModel={createModel}
              editVehicleLine={editVehicleLine}
              deleteVehicleLine={deleteVehicleLine}
              editModel={editModel}
              deleteModel={deleteModel}
              createTrim={createTrim}
              editTrim={editTrim}
              deleteTrim={deleteTrim}
              createOption={createOption}
              editOption={editOption}
              deleteOption={deleteOption}
            />
          </div>
        );
      })}
      
      {/* 무한 스크롤 로딩 인디케이터 */}
      <InfiniteScrollIndicator
        loadingMore={loadingMore}
        hasMore={hasMore}
        currentPage={currentPage}
        totalPages={totalPages}
      />
    </div>
  );
}

export default VersionDataBrandList;
