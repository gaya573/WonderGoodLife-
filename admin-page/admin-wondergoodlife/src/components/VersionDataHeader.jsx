import { useNavigate } from 'react-router-dom';

/**
 * 버전 데이터 관리 페이지 헤더 컴포넌트
 * 뒤로가기 버튼, 제목, 버전 선택 드롭다운을 포함
 */
function VersionDataHeader({ 
  versions, 
  selectedVersion, 
  onVersionChange, 
  showVersionSelector = true 
}) {
  const navigate = useNavigate();

  return (
    <div className="version-header">
      <div className="header-with-back">
        <button 
          className="back-btn"
          onClick={() => navigate('/versions')}
          style={{
            background: 'transparent',
            border: '1px solid #e5e7eb',
            color: '#6b7280',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
            marginBottom: '1rem',
            fontSize: '0.875rem',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.target.style.background = '#f9fafb';
            e.target.style.borderColor = '#d1d5db';
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'transparent';
            e.target.style.borderColor = '#e5e7eb';
          }}
        >
          ← 버전 관리로 돌아가기
        </button>
        <h1 style={{ 
          color: '#111827', 
          fontSize: '1.875rem', 
          fontWeight: '600', 
          margin: '0 0 0.5rem 0' 
        }}>
          데이터 관리
        </h1>
      </div>
      <p style={{ 
        color: '#6b7280', 
        fontSize: '1rem', 
        margin: '0 0 2rem 0' 
      }}>
        버전별로 입력된 브랜드, 모델, 트림 데이터를 관리하세요
      </p>
      
      {/* 버전 선택 드롭다운 */}
      {showVersionSelector && (
        <div style={{ marginBottom: '2rem' }}>
          <label htmlFor="version-select" style={{ 
            color: '#374151', 
            fontSize: '0.875rem', 
            fontWeight: '500', 
            marginBottom: '0.5rem', 
            display: 'block' 
          }}>
            버전 선택
          </label>
          <select 
            id="version-select"
            value={selectedVersion?.id || ''} 
            onChange={(e) => {
              const versionId = parseInt(e.target.value);
              if (versionId && !isNaN(versionId)) {
                const version = versions.find(v => v.id === versionId);
                if (version) {
                  onVersionChange(version);
                }
              }
            }}
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              background: 'white',
              color: '#374151',
              fontSize: '0.875rem',
              width: '100%',
              maxWidth: '400px',
              outline: 'none',
              transition: 'border-color 0.2s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
          >
            <option value="">버전을 선택하세요</option>
            {versions.map(version => (
              <option key={version.id} value={version.id}>
                {version.version_name} - {version.total_brands}개 브랜드, {version.total_models}개 모델, {version.total_trims}개 트림
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}

export default VersionDataHeader;
