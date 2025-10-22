import { useState, useRef, useEffect } from 'react';

/**
 * 검색창 컴포넌트
 * 실시간 검색과 미리보기 기능을 제공
 */
const SearchBox = ({
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
  highlightText
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchInputRef = useRef(null);
  const resultsRef = useRef(null);
  const searchContainerRef = useRef(null);

  // 외부 클릭 감지 - 미리보기 숨김
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        // 검색창 외부 클릭 시 미리보기 숨김
        setIsFocused(false);
        setSelectedIndex(-1);
      }
    };

    if (showPreview) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showPreview]);

  // 키보드 네비게이션 핸들러
  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (showPreview && hasResults) {
          setSelectedIndex(prev => 
            prev < searchResults.length - 1 ? prev + 1 : 0
          );
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (showPreview && hasResults) {
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : searchResults.length - 1
          );
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (showPreview && hasResults && selectedIndex >= 0 && selectedIndex < searchResults.length) {
          onSelectResult(searchResults[selectedIndex]);
        } else if (searchQuery.trim()) {
          onSearchSubmit(searchQuery);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsFocused(false);
        setSelectedIndex(-1);
        searchInputRef.current?.blur();
        break;
    }
  };

  // 선택된 항목 스크롤
  useEffect(() => {
    if (selectedIndex >= 0 && resultsRef.current) {
      const selectedElement = resultsRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }
    }
  }, [selectedIndex]);

  // 포커스 이벤트
  const handleFocus = () => {
    setIsFocused(true);
    if (searchQuery && hasResults) {
      setSelectedIndex(0);
    }
  };

  const handleBlur = () => {
    // 외부 클릭 감지로 처리되므로 즉시 처리
    setIsFocused(false);
    setSelectedIndex(-1);
  };

  // 검색어 변경
  const handleInputChange = (e) => {
    onSearchChange(e.target.value);
    setSelectedIndex(-1);
  };

  // 결과 선택
  const handleResultClick = (result) => {
    console.log('🔍 SearchBox - handleResultClick 호출됨:', result);
    console.log('🔍 SearchBox - onSelectResult 함수:', onSelectResult);
    console.log('🔍 SearchBox - result.displayText:', result.displayText);
    console.log('🔍 SearchBox - result.name:', result.name);
    
    // 직접 URL 변경 테스트
    const searchText = result.displayText || result.name;
    console.log('🔍 SearchBox - 직접 URL 변경 테스트:', searchText);
    
    if (searchText) {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('search', searchText);
      console.log('🔍 SearchBox - 새 URL:', currentUrl.toString());
      
      // 직접 URL 변경
      window.history.replaceState({}, '', currentUrl.toString());
      console.log('🔍 SearchBox - 직접 URL 변경 완료');
    }
    
    if (typeof onSelectResult === 'function') {
      onSelectResult(result);
      console.log('🔍 SearchBox - onSelectResult 호출 완료');
    } else {
      console.error('❌ SearchBox - onSelectResult가 함수가 아닙니다:', typeof onSelectResult);
    }
  };

  // 타입별 아이콘
  const getTypeIcon = (type) => {
    switch (type) {
      case 'brand': return '🏢';
      case 'model': return '🚗';
      case 'trim': return '⚙️';
      default: return '📋';
    }
  };

  // 타입별 색상
  const getTypeColor = (type) => {
    switch (type) {
      case 'brand': return '#3b82f6';
      case 'model': return '#10b981';
      case 'trim': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <div ref={searchContainerRef} style={{ position: 'relative', width: '100%' }}>
      {/* 검색 입력창 */}
      <div style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center'
      }}>
        <div style={{
          position: 'relative',
          flex: 1
        }}>
          <div style={{
            position: 'absolute',
            left: '1rem',
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 1,
            color: isSearching ? '#f59e0b' : '#6b7280',
            fontSize: '1.25rem'
          }}>
            {isSearching ? '⏳' : '🔍'}
          </div>
          
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            placeholder="브랜드, 모델, 트림을 검색하세요... (예: 현대, BMW, 아반떼)"
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 3rem',
              border: `2px solid ${isFocused ? '#3b82f6' : '#e5e7eb'}`,
              borderRadius: '12px',
              fontSize: '1rem',
              outline: 'none',
              background: 'white',
              transition: 'all 0.2s ease',
              boxShadow: isFocused ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none'
            }}
          />
          
          {searchQuery && (
            <button
              onClick={onClearSearch}
              style={{
                position: 'absolute',
                right: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#6b7280',
                fontSize: '1.25rem',
                padding: '0.25rem',
                borderRadius: '50%',
                transition: 'color 0.2s ease'
              }}
              onMouseOver={(e) => e.target.style.color = '#ef4444'}
              onMouseOut={(e) => e.target.style.color = '#6b7280'}
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* 검색 결과 미리보기 */}
      {showPreview && isFocused && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          marginTop: '0.5rem',
          maxHeight: '400px',
          overflow: 'auto'
        }}>
          {/* 검색 통계 */}
          {searchQuery && (
            <div style={{
              padding: '0.75rem 1rem',
              borderBottom: '1px solid #f3f4f6',
              background: '#f8fafc',
              borderTopLeftRadius: '12px',
              borderTopRightRadius: '12px',
              fontSize: '0.875rem',
              color: '#6b7280'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>
                  <strong>"{searchQuery}"</strong> 검색 결과
                </span>
                <span>
                  총 {searchStats.totalItems}개 중 {searchResults.length}개 표시
                </span>
              </div>
            </div>
          )}

          {/* 검색 결과 목록 */}
          {hasResults ? (
            <div ref={resultsRef} style={{ padding: '0.5rem' }}>
              {searchResults.map((result, index) => (
                <div
                  key={`${result.type}-${result.id}`}
                  onClick={(e) => {
                    console.log('🔍 검색 결과 div 클릭됨!', result);
                    e.preventDefault();
                    e.stopPropagation();
                    handleResultClick(result);
                  }}
                  onMouseDown={(e) => {
                    console.log('🔍 검색 결과 mouseDown:', result);
                    // mouseDown에서도 URL 변경 시도
                    setTimeout(() => {
                      console.log('🔍 mouseDown에서 URL 변경 시도');
                      const searchText = result.displayText || result.name;
                      const currentUrl = new URL(window.location.href);
                      currentUrl.searchParams.set('search', searchText);
                      console.log('🔍 mouseDown - 새 URL:', currentUrl.toString());
                      window.history.replaceState({}, '', currentUrl.toString());
                      console.log('🔍 mouseDown - URL 변경 완료');
                    }, 100);
                  }}
                  onMouseUp={(e) => {
                    console.log('🔍 검색 결과 mouseUp:', result);
                    // mouseUp에서도 URL 변경 시도
                    const searchText = result.displayText || result.name;
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('search', searchText);
                    console.log('🔍 mouseUp - 새 URL:', currentUrl.toString());
                    window.history.replaceState({}, '', currentUrl.toString());
                    console.log('🔍 mouseUp - URL 변경 완료');
                  }}
                  onTouchStart={(e) => {
                    console.log('🔍 검색 결과 touchStart:', result);
                    // 터치 이벤트에서도 URL 변경
                    const searchText = result.displayText || result.name;
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('search', searchText);
                    console.log('🔍 touchStart - 새 URL:', currentUrl.toString());
                    window.history.replaceState({}, '', currentUrl.toString());
                    console.log('🔍 touchStart - URL 변경 완료');
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.75rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    background: selectedIndex === index ? '#f0f9ff' : 'transparent',
                    border: selectedIndex === index ? '1px solid #3b82f6' : '1px solid transparent',
                    userSelect: 'none',
                    pointerEvents: 'auto'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedIndex !== index) {
                      e.target.style.background = '#f9fafb';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedIndex !== index) {
                      e.target.style.background = 'transparent';
                    }
                  }}
                >
                  {/* 타입 아이콘 */}
                  <div style={{
                    fontSize: '1.5rem',
                    marginRight: '0.75rem',
                    opacity: 0.8
                  }}>
                    {getTypeIcon(result.type)}
                  </div>

                  {/* 결과 정보 */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {/* 제목 */}
                    <div style={{
                      fontSize: '1rem',
                      fontWeight: '600',
                      color: '#111827',
                      marginBottom: '0.25rem',
                      lineHeight: '1.25'
                    }}
                    dangerouslySetInnerHTML={{
                      __html: highlightText(result.displayText, result.matches)
                    }}
                    />
                    
                    {/* 부제목 */}
                    {result.subtitle && (
                      <div style={{
                        fontSize: '0.875rem',
                        color: '#6b7280'
                      }}>
                        {result.subtitle}
                      </div>
                    )}
                  </div>

                  {/* 타입 배지 */}
                  <div style={{
                    background: getTypeColor(result.type),
                    color: 'white',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    {result.type === 'brand' ? '브랜드' : 
                     result.type === 'model' ? '모델' : '트림'}
                  </div>

                  {/* URL 변경 버튼 */}
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('🔍 URL 변경 버튼 클릭됨!', result);
                      
                      const searchText = result.displayText || result.name;
                      console.log('🔍 URL에 추가할 검색어:', searchText);
                      
                      const currentUrl = new URL(window.location.href);
                      currentUrl.searchParams.set('search', searchText);
                      console.log('🔍 새 URL:', currentUrl.toString());
                      
                      window.history.replaceState({}, '', currentUrl.toString());
                      console.log('✅ URL 변경 완료!');
                      console.log('🔍 변경 후 URL:', window.location.href);
                    }}
                    style={{
                      marginLeft: '0.5rem',
                      padding: '0.25rem 0.5rem',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    선택
                  </button>

                  {/* 점수 (개발 모드에서만 표시) */}
                  {process.env.NODE_ENV === 'development' && (
                    <div style={{
                      marginLeft: '0.5rem',
                      fontSize: '0.75rem',
                      color: '#9ca3af',
                      background: '#f3f4f6',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '4px'
                    }}>
                      {result.score}
                    </div>
                  )}

                </div>
              ))}
            </div>
          ) : (
            <div style={{
              padding: '2rem 1rem',
              textAlign: 'center',
              color: '#6b7280'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
              <div style={{ fontSize: '1rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                검색 결과가 없습니다
              </div>
              <div style={{ fontSize: '0.875rem' }}>
                다른 키워드로 검색해보세요
              </div>
            </div>
          )}

          {/* 검색 힌트 */}
          {!searchQuery && (
            <div style={{
              padding: '1rem',
              borderTop: '1px solid #f3f4f6',
              background: '#f8fafc',
              borderBottomLeftRadius: '12px',
              borderBottomRightRadius: '12px'
            }}>
              <div style={{
                fontSize: '0.875rem',
                color: '#6b7280',
                textAlign: 'center'
              }}>
                <div style={{ marginBottom: '0.5rem', fontWeight: '500' }}>
                  💡 검색 팁
                </div>
                <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
                  브랜드명, 모델명, 트림명을 입력하세요<br/>
                  예: <strong>현대</strong>, <strong>BMW</strong>, <strong>아반떼</strong>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBox;
