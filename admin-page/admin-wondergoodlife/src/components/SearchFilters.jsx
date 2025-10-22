/**
 * 검색 필터 컴포넌트
 * 브랜드, 모델, 트림 타입별로 검색 결과를 필터링
 */
const SearchFilters = ({ 
  selectedFilters, 
  onFilterChange, 
  searchStats 
}) => {
  const filterOptions = [
    { key: 'brand', label: '브랜드', icon: '🏢', count: searchStats.totalBrands },
    { key: 'model', label: '모델', icon: '🚗', count: searchStats.totalModels },
    { key: 'trim', label: '트림', icon: '⚙️', count: searchStats.totalTrims }
  ];

  const handleFilterToggle = (filterKey) => {
    const newFilters = selectedFilters.includes(filterKey)
      ? selectedFilters.filter(f => f !== filterKey)
      : [...selectedFilters, filterKey];
    
    onFilterChange(newFilters);
  };

  const handleSelectAll = () => {
    onFilterChange(['brand', 'model', 'trim']);
  };

  const handleClearAll = () => {
    onFilterChange([]);
  };

  const allSelected = selectedFilters.length === 3;
  const noneSelected = selectedFilters.length === 0;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem',
      background: '#f8fafc',
      borderRadius: '8px',
      border: '1px solid #e5e7eb'
    }}>
      <div style={{
        fontSize: '0.875rem',
        fontWeight: '600',
        color: '#374151'
      }}>
        필터:
      </div>
      
      <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
        {filterOptions.map(option => (
          <button
            key={option.key}
            onClick={() => handleFilterToggle(option.key)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 0.75rem',
              border: selectedFilters.includes(option.key) 
                ? '1px solid #3b82f6' 
                : '1px solid #d1d5db',
              borderRadius: '6px',
              background: selectedFilters.includes(option.key) 
                ? '#dbeafe' 
                : 'white',
              color: selectedFilters.includes(option.key) 
                ? '#1d4ed8' 
                : '#6b7280',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              if (!selectedFilters.includes(option.key)) {
                e.target.style.background = '#f9fafb';
                e.target.style.borderColor = '#9ca3af';
              }
            }}
            onMouseOut={(e) => {
              if (!selectedFilters.includes(option.key)) {
                e.target.style.background = 'white';
                e.target.style.borderColor = '#d1d5db';
              }
            }}
          >
            <span>{option.icon}</span>
            <span>{option.label}</span>
            <span style={{
              background: selectedFilters.includes(option.key) 
                ? '#3b82f6' 
                : '#e5e7eb',
              color: selectedFilters.includes(option.key) 
                ? 'white' 
                : '#6b7280',
              padding: '0.125rem 0.375rem',
              borderRadius: '10px',
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>
              {option.count}
            </span>
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button
          onClick={handleSelectAll}
          disabled={allSelected}
          style={{
            padding: '0.5rem 0.75rem',
            border: '1px solid #10b981',
            borderRadius: '6px',
            background: allSelected ? '#d1fae5' : 'white',
            color: allSelected ? '#059669' : '#10b981',
            fontSize: '0.875rem',
            fontWeight: '500',
            cursor: allSelected ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            opacity: allSelected ? 0.5 : 1
          }}
        >
          전체 선택
        </button>
        
        <button
          onClick={handleClearAll}
          disabled={noneSelected}
          style={{
            padding: '0.5rem 0.75rem',
            border: '1px solid #ef4444',
            borderRadius: '6px',
            background: noneSelected ? '#fee2e2' : 'white',
            color: noneSelected ? '#dc2626' : '#ef4444',
            fontSize: '0.875rem',
            fontWeight: '500',
            cursor: noneSelected ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            opacity: noneSelected ? 0.5 : 1
          }}
        >
          전체 해제
        </button>
      </div>
    </div>
  );
};

export default SearchFilters;
