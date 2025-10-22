/**
 * 무한 스크롤 로딩 인디케이터 컴포넌트
 * 로딩 상태와 완료 상태를 표시
 */
const InfiniteScrollIndicator = ({ loadingMore, hasMore, currentPage, totalPages }) => {
  // 로딩 중일 때
  if (loadingMore && hasMore) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '2rem',
        background: 'white',
        borderRadius: '12px',
        border: '1px solid #e5e7eb',
        marginTop: '1rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          color: '#6b7280'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid #e5e7eb',
            borderTop: '2px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
            추가 데이터를 불러오는 중... ({currentPage}/{totalPages}) - 20% 지점에서 미리 로딩
          </span>
        </div>
      </div>
    );
  }

  // 더 이상 데이터가 없을 때
  if (!hasMore && currentPage > 1) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '2rem',
        background: 'white',
        borderRadius: '12px',
        border: '1px solid #e5e7eb',
        marginTop: '1rem'
      }}>
        <div style={{
          color: '#6b7280',
          fontSize: '0.875rem',
          fontWeight: '500'
        }}>
          📄 모든 데이터를 불러왔습니다 ({totalPages}페이지)
        </div>
      </div>
    );
  }

  // 기본 상태 (아무것도 표시하지 않음)
  return null;
};

export default InfiniteScrollIndicator;
