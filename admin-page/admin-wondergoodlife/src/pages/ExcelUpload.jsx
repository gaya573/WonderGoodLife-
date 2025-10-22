import { useState, useRef, useEffect } from 'react';
import { uploadExcelAsync, getJobStatus } from '../services/api';
import versionAPI from '../services/versionApi';
// monitoring 관련 import 제거됨
import { useNavigate, useSearchParams } from 'react-router-dom';
import './ExcelUpload.css';

function ExcelUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [loadingVersions, setLoadingVersions] = useState(true);
  const [targetVersion, setTargetVersion] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState('KR');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // URL 파라미터에서 버전 ID 확인
  useEffect(() => {
    const versionId = searchParams.get('version_id');
    if (versionId) {
      loadTargetVersion(versionId);
    }
    loadVersions();
  }, [searchParams]);

  // 작업 상태 폴링
  useEffect(() => {
    if (!jobId) return;

    const versionToUse = targetVersion || selectedVersion;
    if (!versionToUse?.id) return;

    const pollInterval = setInterval(async () => {
      try {
        // 버전별 작업 상태 조회 API 사용
        const response = await fetch(`http://localhost:8000/api/versions/${versionToUse.id}/job-status/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('작업 상태 조회 실패');
        }
        
        const status = await response.json();
        setJobStatus(status);

        // 완료 또는 실패 시 폴링 중지
        if (status.status === 'COMPLETED') {
          clearInterval(pollInterval);
          setTimeout(() => {
            navigate(`/version-data-management?version_id=${status.version_id}`);
          }, 2000);
        } else if (status.status === 'FAILED') {
          clearInterval(pollInterval);
          setError(status.error_message || '처리 중 오류가 발생했습니다.');
        }
      } catch (err) {
        console.error('작업 상태 조회 실패:', err);
      }
    }, 2000); // 2초마다 폴링

    return () => clearInterval(pollInterval);
  }, [jobId, navigate, targetVersion, selectedVersion]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileName = selectedFile.name;
      if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        setFile(selectedFile);
        setError(null);
        setJobId(null);
        setJobStatus(null);
      } else {
        setError('엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.');
        setFile(null);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const fileName = droppedFile.name;
      if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        setFile(droppedFile);
        setError(null);
        setJobId(null);
        setJobStatus(null);
      } else {
        setError('엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.');
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const loadTargetVersion = async (versionId) => {
    try {
      console.log(`[DEBUG] 버전 ${versionId} 로드 시도`);
      const response = await versionAPI.getById(versionId);
      console.log('[DEBUG] 버전 응답:', response.data);
      
      if (response.data) {
        setTargetVersion(response.data);
        setSelectedVersion(response.data);
        console.log('[DEBUG] 버전 정보 설정 완료');
      } else {
        console.error('[ERROR] 응답 데이터가 비어있음');
        setError('버전 정보가 비어있습니다.');
      }
    } catch (err) {
      console.error('Failed to load target version:', err);
      setError('버전 정보를 불러오는 데 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const loadVersions = async () => {
    try {
      setLoadingVersions(true);
      
      // URL 파라미터가 있을 때는 버전 목록을 로드하지 않음
      const versionId = searchParams.get('version_id');
      if (versionId) {
        return; // loadTargetVersion에서 targetVersion을 설정하므로 여기서는 return
      }
      
      // URL 파라미터가 없을 때만 PENDING 상태의 버전들을 로드
      const response = await versionAPI.getAll({ approval_status: 'PENDING', limit: 100 });
      setVersions(response.data?.items || []);
    } catch (err) {
      console.error('Failed to load versions:', err);
      setError('버전 목록을 불러오는 데 실패했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('파일을 선택해주세요.');
      return;
    }

    const versionToUse = targetVersion || selectedVersion;
    if (!versionToUse) {
      setError('버전을 선택해주세요.');
      return;
    }
    
    if (!versionToUse.id) {
      setError('선택된 버전의 ID가 유효하지 않습니다.');
      return;
    }
    
    if (versionToUse.approval_status !== 'PENDING') {
      setError('PENDING 상태의 버전만 엑셀 업로드가 가능합니다.');
      return;
    }


    setUploading(true);
    setError(null);
    setJobId(null);
    setJobStatus(null);

    try {
      // 버전별 엑셀 업로드 API 호출
      const formData = new FormData();
      formData.append('file', file);
      formData.append('country', selectedCountry);
      
      // JWT 토큰 가져오기
      const token = localStorage.getItem('access_token');
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`http://localhost:8000/api/versions/${versionToUse.id}/upload-excel`, {
        method: 'POST',
        headers: headers,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '업로드 중 오류가 발생했습니다.');
      }

      const result = await response.json();
      setJobId(result.job_id);  // 정수 ID 사용
      setJobStatus({
        id: result.job_id,
        status: 'PENDING',
        message: result.message,
        version_id: result.version_id,
        version_name: result.version_name || versionToUse.version_name
      });
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.message || '업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setJobId(null);
    setJobStatus(null);
    setError(null);
    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (loadingVersions) {
    return <div className="loading">버전 목록을 불러오는 중...</div>;
  }

  return (
    <div style={{ padding: '2rem', background: '#f9fafb', minHeight: '100vh' }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <h1 style={{
            margin: 0,
            fontSize: '1.875rem',
            fontWeight: '600',
            color: '#111827'
          }}>
            버전별 엑셀 파일 업로드
          </h1>
     
        </div>
        {targetVersion ? (
          <div style={{
            background: '#f0f9ff',
            border: '1px solid #bae6fd',
            borderRadius: '8px',
            padding: '1.5rem',
            marginTop: '1rem'
          }}>
            <h2 style={{
              margin: '0 0 0.5rem 0',
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#0c4a6e'
            }}>
              업로드 대상 버전: {targetVersion.version_name}
            </h2>
            {targetVersion.description && (
              <p style={{
                margin: '0 0 1rem 0',
                color: '#0369a1',
                fontSize: '0.875rem'
              }}>
                {targetVersion.description}
              </p>
            )}
            <div style={{
              display: 'flex',
              gap: '2rem',
              fontSize: '0.875rem',
              color: '#0369a1'
            }}>
              <span>생성자: {targetVersion.created_by}</span>
              <span>생성일: {targetVersion.created_at ? new Date(targetVersion.created_at).toLocaleString() : 'N/A'}</span>
            </div>
          </div>
        ) : (
          <p style={{
            margin: 0,
            color: '#6b7280',
            fontSize: '1rem'
          }}>
            버전을 선택하고 차량 데이터를 엑셀 파일로 업로드하세요
          </p>
        )}
      </div>

      {/* 버전 선택 (URL 파라미터가 없을 때만 표시) */}
      {!targetVersion && (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            margin: '0 0 1rem 0',
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#111827'
          }}>
            업로드할 버전 선택
          </h3>
          <div style={{
            background: '#fef3c7',
            border: '1px solid #f59e0b',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <p style={{
              margin: '0',
              fontSize: '0.875rem',
              color: '#92400e'
            }}>
              💡 <strong>안내:</strong> PENDING 상태의 버전만 엑셀 파일 업로드가 가능합니다. 
              승인됨(APPROVED) 또는 거부됨(REJECTED) 상태의 버전은 선택할 수 없습니다.
            </p>
          </div>
          {versions.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '3rem',
              color: '#6b7280'
            }}>
              <p style={{ margin: '0', fontSize: '1.125rem' }}>
                업로드 가능한 PENDING 상태 버전이 없습니다. 위의 "새 버전 생성하기" 버튼을 클릭하여 새 버전을 만들어주세요.
              </p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
            {versions.map((version, index) => (
              <div 
                key={version.id || `version-${index}`} 
                style={{
                  background: selectedVersion?.id === version.id ? '#f0f9ff' : 
                             version.approval_status !== 'PENDING' ? '#f9fafb' : 'white',
                  border: selectedVersion?.id === version.id ? '2px solid #3b82f6' : 
                         version.approval_status !== 'PENDING' ? '1px solid #d1d5db' : '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '1.5rem',
                  cursor: version.approval_status === 'PENDING' ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease',
                  opacity: version.approval_status !== 'PENDING' ? 0.6 : 1
                }}
                onClick={() => {
                  if (version.approval_status === 'PENDING') {
                    setSelectedVersion(version);
                  }
                }}
                onMouseOver={(e) => {
                  if (selectedVersion?.id !== version.id && version.approval_status === 'PENDING') {
                    e.currentTarget.style.borderColor = '#d1d5db';
                    e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                  }
                }}
                onMouseOut={(e) => {
                  if (selectedVersion?.id !== version.id) {
                    e.currentTarget.style.borderColor = version.approval_status !== 'PENDING' ? '#d1d5db' : '#e5e7eb';
                    e.currentTarget.style.boxShadow = 'none';
                  }
                }}
              >
                  <div style={{ marginBottom: '1rem' }}>
                    <h4 style={{
                      margin: '0 0 0.5rem 0',
                      fontSize: '1rem',
                      fontWeight: '600',
                      color: '#111827'
                    }}>
                      {version.version_name}
                    </h4>
                    {version.description && (
                      <p style={{
                        margin: '0 0 1rem 0',
                        color: '#6b7280',
                        fontSize: '0.875rem'
                      }}>
                        {version.description}
                      </p>
                    )}
                    <div style={{
                      display: 'flex',
                      gap: '1rem',
                      fontSize: '0.75rem',
                      color: '#6b7280'
                    }}>
                      <span>브랜드: {version.total_brands || 0}</span>
                      <span>모델: {version.total_models || 0}</span>
                      <span>트림: {version.total_trims || 0}</span>
                    </div>
                  </div>
                  
                  {/* 상태 표시 */}
                  <div style={{
                    background: version.approval_status === 'PENDING' ? '#f59e0b' : 
                               version.approval_status === 'APPROVED' ? '#10b981' : '#ef4444',
                    color: 'white',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    display: 'inline-block'
                  }}>
                    {version.approval_status === 'PENDING' ? '대기중' : 
                     version.approval_status === 'APPROVED' ? '승인됨' : '거부됨'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 선택된 버전 표시 (URL 파라미터가 없을 때만) */}
      {selectedVersion && !targetVersion && (
        <div className="selected-version">
          <h3>선택된 버전: {selectedVersion.version_name}</h3>
          {selectedVersion.description && <p>{selectedVersion.description}</p>}
        </div>
      )}

      {/* 브랜드 국가 선택 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{
          margin: '0 0 1.5rem 0',
          fontSize: '1.125rem',
          fontWeight: '600',
          color: '#111827'
        }}>
          브랜드 국가 선택
        </h3>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <label htmlFor="country-select" style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#374151'
          }}>
            엑셀 파일의 브랜드들이 속한 국가를 선택하세요 *
          </label>
          <select 
            id="country-select"
            value={selectedCountry} 
            onChange={(e) => setSelectedCountry(e.target.value)}
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              background: 'white',
              color: '#374151',
              fontSize: '0.875rem',
              outline: 'none',
              transition: 'border-color 0.2s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
          >
            <option value="KR">🇰🇷 대한민국 (Korea)</option>
            <option value="US">🇺🇸 미국 (United States)</option>
            <option value="JP">🇯🇵 일본 (Japan)</option>
            <option value="DE">🇩🇪 독일 (Germany)</option>
            <option value="FR">🇫🇷 프랑스 (France)</option>
            <option value="IT">🇮🇹 이탈리아 (Italy)</option>
            <option value="GB">🇬🇧 영국 (United Kingdom)</option>
            <option value="CN">🇨🇳 중국 (China)</option>
            <option value="ES">🇪🇸 스페인 (Spain)</option>
            <option value="CA">🇨🇦 캐나다 (Canada)</option>
            <option value="AU">🇦🇺 호주 (Australia)</option>
            <option value="BR">🇧🇷 브라질 (Brazil)</option>
            <option value="IN">🇮🇳 인도 (India)</option>
            <option value="RU">🇷🇺 러시아 (Russia)</option>
            <option value="MX">🇲🇽 멕시코 (Mexico)</option>
            <option value="SE">🇸🇪 스웨덴 (Sweden)</option>
            <option value="CH">🇨🇭 스위스 (Switzerland)</option>
            <option value="NL">🇳🇱 네덜란드 (Netherlands)</option>
            <option value="BE">🇧🇪 벨기에 (Belgium)</option>
            <option value="AT">🇦🇹 오스트리아 (Austria)</option>
            <option value="CZ">🇨🇿 체코 (Czech Republic)</option>
            <option value="PL">🇵🇱 폴란드 (Poland)</option>
            <option value="HU">🇭🇺 헝가리 (Hungary)</option>
            <option value="RO">🇷🇴 루마니아 (Romania)</option>
            <option value="BG">🇧🇬 불가리아 (Bulgaria)</option>
            <option value="GR">🇬🇷 그리스 (Greece)</option>
            <option value="PT">🇵🇹 포르투갈 (Portugal)</option>
            <option value="TR">🇹🇷 터키 (Turkey)</option>
            <option value="ZA">🇿🇦 남아프리카공화국 (South Africa)</option>
            <option value="EG">🇪🇬 이집트 (Egypt)</option>
            <option value="MA">🇲🇦 모로코 (Morocco)</option>
            <option value="TH">🇹🇭 태국 (Thailand)</option>
            <option value="VN">🇻🇳 베트남 (Vietnam)</option>
            <option value="MY">🇲🇾 말레이시아 (Malaysia)</option>
            <option value="SG">🇸🇬 싱가포르 (Singapore)</option>
            <option value="ID">🇮🇩 인도네시아 (Indonesia)</option>
            <option value="PH">🇵🇭 필리핀 (Philippines)</option>
            <option value="AR">🇦🇷 아르헨티나 (Argentina)</option>
            <option value="CL">🇨🇱 칠레 (Chile)</option>
            <option value="CO">🇨🇴 콜롬비아 (Colombia)</option>
            <option value="PE">🇵🇪 페루 (Peru)</option>
            <option value="UY">🇺🇾 우루과이 (Uruguay)</option>
            <option value="VE">🇻🇪 베네수엘라 (Venezuela)</option>
            <option value="EC">🇪🇨 에콰도르 (Ecuador)</option>
            <option value="BO">🇧🇴 볼리비아 (Bolivia)</option>
            <option value="PY">🇵🇾 파라과이 (Paraguay)</option>
            <option value="OTHER">🌍 기타 (Other)</option>
          </select>
          <p style={{
            fontSize: '0.75rem',
            color: '#6b7280',
            margin: 0
          }}>
            💡 엑셀 파일의 모든 브랜드가 선택한 국가로 설정됩니다.
          </p>
        </div>
      </div>

      <div className="upload-card">
        <div 
          className="drop-zone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          <div className="drop-zone-icon">📁</div>
          <h3>파일을 드래그하거나 클릭하여 선택하세요</h3>
          <p>지원 형식: .xlsx, .xls (최대 10MB)</p>
          {(selectedVersion || targetVersion) && (
            <p className="upload-target-info">
              📋 업로드 대상: {targetVersion?.version_name || selectedVersion?.version_name}
            </p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="file-input"
          />
          <button 
            className="select-file-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            파일 선택
          </button>
        </div>

        {file && !jobId && (
          <div className="selected-file">
            <div className="file-info">
              <span className="file-icon">📄</span>
              <div className="file-details">
                <p className="file-name">{file.name}</p>
                <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
              <button className="remove-file-btn" onClick={handleReset}>
                ✕
              </button>
            </div>
            <button 
              className="upload-btn"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? '업로드 중...' : '업로드 시작'}
            </button>
          </div>
        )}

        {jobStatus && (
          <div className="message info-message">
            <span className="message-icon">
              {jobStatus.status === 'COMPLETED' ? '완료' : 
               jobStatus.status === 'FAILED' ? '실패' : '진행중'}
            </span>
            <div className="result-content">
              <h3>
                {jobStatus.status === 'PENDING' && '작업 대기 중...'}
                {jobStatus.status === 'PROCESSING' && '처리 중...'}
                {jobStatus.status === 'COMPLETED' && '처리 완료! Staging 데이터를 확인하세요.'}
                {jobStatus.status === 'FAILED' && '처리 실패'}
              </h3>
              
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${jobStatus.progress_percentage || 0}%` }}
                  />
                </div>
                <p className="progress-text">{jobStatus.progress_percentage || 0}% 완료</p>
              </div>

              <div className="result-stats">
                <div className="stat-item">
                  <span className="stat-label">전체 행:</span>
                  <span className="stat-value">{jobStatus.total_rows || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">처리된 행:</span>
                  <span className="stat-value">{jobStatus.processed_rows || 0}</span>
                </div>
              </div>

              {jobStatus.status === 'COMPLETED' && jobStatus.result_data && (
                <div className="result-detail">
                  <p>트림: {jobStatus.result_data.trim_count || 0}개</p>
                  <p>옵션: {jobStatus.result_data.option_count || 0}개</p>
                  <p>색상: {jobStatus.result_data.color_count || 0}개</p>
                  
                  <button 
                    className="view-version-btn"
                    onClick={() => navigate(`/versions/${jobStatus.version_id}`)}
                  >
                    버전 상세 보기 →
                  </button>
                </div>
              )}

              {jobStatus.result_data?.errors && jobStatus.result_data.errors.length > 0 && (
                <div className="error-list">
                  <h4>오류 목록:</h4>
                  <ul>
                    {jobStatus.result_data.errors.map((err, idx) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="message error-message">
            <span className="message-icon">오류</span>
            <p>{error}</p>
          </div>
        )}
      </div>

      <div className="excel-guide">
        <h2>엑셀 파일 형식 가이드</h2>
        <div className="guide-content">
          <div className="guide-section">
            <h3>📁 시트별 브랜드 구조</h3>
            <p>엑셀 파일은 <strong>시트별로 브랜드가 분리</strong>되어 있습니다:</p>
            <div className="brand-sheets">
              <span className="sheet-tab">현대</span>
              <span className="sheet-tab active">기아</span>
              <span className="sheet-tab">제네시스</span>
              <span className="sheet-tab">르노코리아</span>
              <span className="sheet-tab">한국지엠(쉐보레)</span>
              <span className="sheet-tab">KGM(쌍용)</span>
            </div>
          </div>
          
          <div className="guide-section">
            <h3>시트 내부 컬럼 구조</h3>
            <table className="example-table">
              <thead>
                <tr>
                  <th>RowType</th>
                  <th>Model</th>
                  <th>Trim</th>
                  <th>BasePrice</th>
                  <th>OptionGroup</th>
                  <th>OptionName</th>
                  <th>Price</th>
                </tr>
              </thead>
              <tbody>
                <tr className="trim-row">
                  <td>TRIM</td>
                  <td>모닝 가솔린 1.0</td>
                  <td>트렌디</td>
                  <td>13,250,000</td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
                <tr className="trim-row">
                  <td>TRIM</td>
                  <td>모닝 가솔린 1.0</td>
                  <td>프레스티지</td>
                  <td>15,000,000</td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
                <tr className="option-row">
                  <td>OPTION</td>
                  <td>모닝 가솔린 1.0</td>
                  <td></td>
                  <td></td>
                  <td>트렌디</td>
                  <td>버튼시동 PACK</td>
                  <td>400,000</td>
                </tr>
                <tr className="option-row">
                  <td>OPTION</td>
                  <td>모닝 가솔린 1.0</td>
                  <td></td>
                  <td></td>
                  <td>트렌디</td>
                  <td>스타일</td>
                  <td>900,000</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div className="guide-tips">
            <h3>🔄 처리 과정</h3>
            <ol>
              <li><strong>시트별 브랜드 인식</strong>: 시트명으로 브랜드 구분 (현대, 기아 등)</li>
              <li><strong>Staging DB 저장</strong>: 임시 테이블에 저장 (승인 대기 상태)</li>
              <li><strong>관리자 검토</strong>: "승인 대기" 페이지에서 데이터 확인</li>
              <li><strong>승인/거부</strong>: 개별 또는 일괄 승인 처리</li>
              <li><strong>Main DB 전송</strong>: 승인된 데이터만 최종 테이블로 이동</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExcelUpload;
