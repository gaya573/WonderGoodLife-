import SearchBox from './SearchBox';

/**
 * 버전 데이터 관리 페이지 검색 섹션 컴포넌트
 * 검색 기능과 필터링 상태를 관리
 */
function VersionDataSearchSection({
  // 검색 관련 props
  searchQuery,
  searchResults,
  isSearching,
  showPreview,
  searchStats,
  hasResults,
  onSearchChange,
  onSelectResult,
  onClearSearch,
  onSearchSubmit,
  highlightText,
  
  // 필터링 상태
  versionData,
  onClearSearchFilter
}) {
  return (
    <div style={{
      background: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '1.5rem',
      marginBottom: '2rem',
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h2 style={{ 
            color: '#111827', 
            margin: 0, 
            fontSize: '1.25rem', 
            fontWeight: '600' 
          }}>
            🔍 빠른 검색
          </h2>
          {versionData?.filtered_by_search && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: '#eff6ff',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '1px solid #bfdbfe'
            }}>
              <span style={{ fontSize: '0.875rem', color: '#1e40af' }}>
                필터링됨: "{versionData.search_query}"
              </span>
              <button
                onClick={onClearSearchFilter}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#1e40af',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  padding: '0.25rem',
                  borderRadius: '50%',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = '#dbeafe'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
                title="검색 필터 초기화"
              >
                ×
              </button>
            </div>
          )}
        </div>
        <div style={{
          fontSize: '0.875rem',
          color: '#6b7280',
          background: '#f8fafc',
          padding: '0.5rem 1rem',
          borderRadius: '6px',
          border: '1px solid #e2e8f0'
        }}>
          {versionData?.filtered_by_search ? 
            `필터링된 결과: ${versionData.total_count}개 브랜드` : 
            `총 ${searchStats.totalItems}개 항목`
          }
        </div>
      </div>
      
      {/* 검색창 */}
      <SearchBox
        searchQuery={searchQuery}
        searchResults={searchResults}
        isSearching={isSearching}
        showPreview={showPreview}
        searchStats={searchStats}
        hasResults={hasResults}
        onSearchChange={onSearchChange}
        onSelectResult={onSelectResult}
        onClearSearch={onClearSearch}
        onSearchSubmit={onSearchSubmit}
        highlightText={highlightText}
      />
    </div>
  );
}

export default VersionDataSearchSection;
