/**
 * Version 관리 페이지 - 버전 CRUD 및 페이지네이션
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import versionAPI from '../services/versionApi';
// monitoring 관련 import 제거됨
import { useNavigate } from 'react-router-dom';
import './DataList.css';
import './VersionList.css';

function VersionList() {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingVersion, setEditingVersion] = useState(null);
  const [showCrawlingModal, setShowCrawlingModal] = useState(false);
  const [selectedVersionForCrawling, setSelectedVersionForCrawling] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  
  // 무한 스크롤 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;
  
  // 필터 및 검색 상태
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchTimeout, setSearchTimeout] = useState(null);
  
  // 무한 스크롤을 위한 ref
  const observerRef = useRef();
  const lastVersionRef = useCallback(node => {
    if (loading || loadingMore) return;
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMoreVersions();
      }
    });
    if (node) observerRef.current.observe(node);
  }, [loading, loadingMore, hasMore]);
  
  // 폼 데이터
  const [formData, setFormData] = useState({
    version_name: '',
    description: '',
    created_by: 'admin'
  });
  
  const navigate = useNavigate();
  const searchInputRef = useRef(null); // 검색 입력 필드 참조

  // 초기 로드 및 검색/필터 변경시 리셋
  useEffect(() => {
    // 사용자 정보 로드
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      try {
        setCurrentUser(JSON.parse(userInfo));
      } catch (e) {
        console.error('사용자 정보 파싱 오류:', e);
      }
    }
    
    resetAndLoadVersions();
  }, [statusFilter, searchQuery]);

  // 페이지 포커스 시 자동 리패치 (다른 페이지에서 돌아왔을 때)
  useEffect(() => {
    const handleFocus = () => {
      // 페이지가 다시 포커스될 때 데이터 새로고침
      resetAndLoadVersions();
    };

    window.addEventListener('focus', handleFocus);
    
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  // 검색 디바운스
  useEffect(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    const timeout = setTimeout(() => {
      // 검색어가 있으면 검색 실행, 없으면 전체 데이터 로드
      resetAndLoadVersions();
    }, 500);
    
    setSearchTimeout(timeout);
    
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  const resetAndLoadVersions = async () => {
    setVersions([]);
    setCurrentPage(1);
    setHasMore(true);
    setTotalCount(0);
    await loadVersions(1, true);
  };

  const loadVersions = async (page = 1, isReset = false) => {
    try {
      if (isReset) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      
      const params = {
        skip: (page - 1) * pageSize,
        limit: pageSize
      };
      
      if (statusFilter) {
        params.approval_status = statusFilter;
      }
      
      if (searchQuery) {
        params.search = searchQuery;
      }
      
      const response = await versionAPI.getAll(params);
      console.log('API Response:', response.data);
      
      if (response.data && response.data.items) {
        const newVersions = response.data.items;
        
        if (isReset) {
          setVersions(newVersions);
        } else {
          setVersions(prev => [...prev, ...newVersions]);
        }
        
        setTotalCount(response.data.total_count || 0);
        setHasMore(newVersions.length === pageSize && (page * pageSize) < (response.data.total_count || 0));
        setCurrentPage(page);
      } else {
        console.error('Unexpected API response structure:', response.data);
        if (isReset) {
          setVersions([]);
        }
        setHasMore(false);
      }
      
    } catch (err) {
      console.error('Failed to load versions:', err);
      setError(err.response?.data?.detail || err.message || '버전 목록을 불러오는 데 실패했습니다.');
      if (isReset) {
        setVersions([]);
      }
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
      // 검색 완료 후 포커스 유지
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }
  };

  const loadMoreVersions = async () => {
    if (!hasMore || loadingMore) return;
    await loadVersions(currentPage + 1, false);
  };

  const handleCreate = async () => {
    try {
      await versionAPI.create(formData);
      setShowCreateModal(false);
      setFormData({ version_name: '', description: '', created_by: 'admin' });
      resetAndLoadVersions();
      alert('버전이 성공적으로 생성되었습니다.');
    } catch (err) {
      alert('버전 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleEdit = (version) => {
    setEditingVersion(version);
    setFormData({
      version_name: version.version_name,
      description: version.description || '',
      created_by: version.created_by
    });
    setShowEditModal(true);
  };

  const handleUpdate = async () => {
    try {
      console.log('Updating version:', editingVersion);
      if (!editingVersion || !editingVersion.id) {
        alert('수정할 버전 정보가 없습니다.');
        return;
      }
      
      await versionAPI.update(editingVersion.id, {
        version_name: formData.version_name,
        description: formData.description
      });
      setShowEditModal(false);
      setEditingVersion(null);
      setFormData({ version_name: '', description: '', created_by: 'admin' });
      resetAndLoadVersions();
      alert('버전이 성공적으로 수정되었습니다.');
    } catch (err) {
      console.error('Update error:', err);
      alert('버전 수정에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('정말로 이 버전을 삭제하시겠습니까?')) {
      try {
        await versionAPI.delete(id);
        resetAndLoadVersions();
        alert('버전이 성공적으로 삭제되었습니다.');
      } catch (err) {
        alert('버전 삭제에 실패했습니다: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleMigrate = async (id) => {
    if (window.confirm('이 버전을 마이그레이션하시겠습니까?')) {
      try {
        await versionAPI.migrate(id);
        resetAndLoadVersions();
        alert('버전 마이그레이션이 완료되었습니다.');
      } catch (err) {
        alert('마이그레이션에 실패했습니다: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleExcelUpload = (version) => {
    // 엑셀 업로드 페이지로 이동
    navigate(`/excel-upload?version_id=${version.id}`);
  };

  const handleCrawling = (version) => {
    // 크롤링 모달 또는 페이지로 이동
    setSelectedVersionForCrawling(version);
    setShowCrawlingModal(true);
  };

  const handleApprovalRequest = async (version) => {
    if (!window.confirm(`버전 '${version.version_name}'을 승인신청하시겠습니까?\n\n승인 대기 상태로 변경됩니다.`)) {
      return;
    }
    try {
      // 승인신청은 버전 상태를 PENDING으로 변경하는 API 호출
      const response = await versionAPI.update(version.id, {
        approval_status: 'PENDING'
      });
      alert('승인신청이 완료되었습니다.');
      resetAndLoadVersions();
    } catch (err) {
      alert('승인신청에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleUploadToMain = async (version) => {
    if (!window.confirm(`버전 '${version.version_name}'을 메인 DB에 푸시하시겠습니까?\n\nStaging 데이터가 Main DB로 복사됩니다.`)) {
      return;
    }
    try {
      const response = await versionAPI.uploadToMain(version.id);
      alert(response.data.message);
      resetAndLoadVersions();
    } catch (err) {
      alert('메인 DB 푸시에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDownloadFromMain = async (version) => {
    if (!window.confirm(`메인 DB에서 버전 '${version.version_name}'으로 데이터를 풀하시겠습니까?\n\n기존 Staging 데이터가 삭제되고 Main 데이터로 교체되며, 상태가 승인대기로 변경됩니다.`)) {
      return;
    }
    try {
      const response = await versionAPI.downloadFromMain(version.id);
      alert(response.data.message);
      resetAndLoadVersions();
    } catch (err) {
      alert('메인 DB 풀에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleApproveVersion = async (version) => {
    if (!window.confirm(`버전 '${version.version_name}'을 승인하시겠습니까?\n\n승인 후 메인 DB로 푸시할 수 있습니다.`)) {
      return;
    }
    try {
      const response = await versionAPI.approveVersion(version.id);
      alert(response.data.message);
      resetAndLoadVersions();
    } catch (err) {
      alert('버전 승인에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRejectVersion = async (version) => {
    const reason = prompt(`버전 '${version.version_name}'을 거부하시겠습니까?\n\n거부 사유를 입력해주세요:`, '');
    if (reason === null) return; // 취소
    
    if (!reason.trim()) {
      alert('거부 사유를 입력해주세요.');
      return;
    }
    
    try {
      const response = await versionAPI.rejectVersion(version.id, reason);
      alert(response.data.message);
      resetAndLoadVersions();
    } catch (err) {
      alert('버전 거부에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleMainDBView = () => {
    // 메인 DB 현황 페이지로 이동
    navigate('/main-db-status');
  };

  // 승인 권한 체크 함수
  const canApprove = () => {
    if (!currentUser) return false;
    const userRole = currentUser.role;
    const userPosition = currentUser.position;
    return userRole === 'ADMIN' || userPosition === 'MANAGER' || userPosition === 'CEO';
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchClear = () => {
    setSearchQuery('');
  };

  // 검색어 하이라이트 함수
  const highlightSearchTerm = (text, searchTerm) => {
    if (!searchTerm || !text) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark style="background: #fef3c7; color: #92400e; padding: 0.125rem 0.25rem; border-radius: 0.25rem;">$1</mark>');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PENDING': return '#f59e0b';    // 주황
      case 'APPROVED': return '#10b981';   // 초록
      case 'MIGRATED': return '#3b82f6';   // 파랑
      case 'REJECTED': return '#ef4444';   // 빨강
      default: return '#6b7280';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'PENDING': return '대기중';
      case 'APPROVED': return '승인됨';
      case 'MIGRATED': return '마이그레이션 완료';
      case 'REJECTED': return '거부됨';
      default: return status;
    }
  };

  if (loading) return <div className="loading">로딩 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div style={{ padding: '2rem', background: '#f9fafb', minHeight: '100vh' }}>
      {/* 메인 DB 현황 섹션 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: '1.25rem',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '0.5rem'
            }}>
              📊 메인 DB 현황
            </h2>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '0.875rem'
            }}>
              현재 메인 데이터베이스의 상태를 확인하세요
            </p>
          </div>
          <button 
            onClick={handleMainDBView}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => e.target.style.background = '#2563eb'}
            onMouseOut={(e) => e.target.style.background = '#3b82f6'}
          >
            🔍 메인 DB 보기
          </button>
        </div>
      </div>

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
          alignItems: 'flex-start',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '1.875rem',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '0.5rem'
            }}>
              버전 관리
            </h1>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '1rem'
            }}>
              {searchQuery ? `"${searchQuery}" 검색 결과: ${totalCount}개의 버전` : `총 ${totalCount}개의 버전`}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {/* 검색창 */}
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  left: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6b7280',
                  fontSize: '1rem'
                }}>
                  🔍
                </div>
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="버전명 또는 설명으로 검색..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                  style={{
                    padding: '0.75rem 1rem 0.75rem 2.5rem',
                    border: searchQuery ? '2px solid #3b82f6' : '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '0.875rem',
                    width: '300px',
                    outline: 'none',
                    transition: 'border-color 0.2s ease',
                    background: searchQuery ? '#f8fafc' : 'white'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#3b82f6';
                    e.target.style.background = '#f8fafc';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = searchQuery ? '#3b82f6' : '#d1d5db';
                    e.target.style.background = searchQuery ? '#f8fafc' : 'white';
                  }}
                />
              </div>
              {searchQuery && (
                <button 
                  onClick={handleSearchClear}
                  style={{
                    position: 'absolute',
                    right: '0.75rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#6b7280',
                    fontSize: '1.25rem'
                  }}
                >
                  ✕
                </button>
              )}
            </div>
            
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{
                padding: '0.75rem 1rem',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '0.875rem',
                background: 'white',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            >
              <option value="">전체 상태</option>
              <option value="PENDING">대기중</option>
              <option value="APPROVED">승인됨</option>
              <option value="MIGRATED">마이그레이션 완료</option>
              <option value="REJECTED">거부됨</option>
            </select>
            
            <button 
              onClick={() => navigate('/staging-brands')}
              style={{
                background: '#6b7280',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease'
              }}
              onMouseOver={(e) => e.target.style.background = '#4b5563'}
              onMouseOut={(e) => e.target.style.background = '#6b7280'}
            >
              승인 대기
            </button>
            
            <button 
              onClick={() => setShowCreateModal(true)}
              style={{
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease'
              }}
              onMouseOver={(e) => e.target.style.background = '#2563eb'}
              onMouseOut={(e) => e.target.style.background = '#3b82f6'}
            >
              새 버전 생성
            </button>
          </div>
        </div>
      </div>

      {versions.length === 0 ? (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '3rem',
          textAlign: 'center',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          {searchQuery ? (
            <div>
              <div style={{ 
                fontSize: '3rem', 
                marginBottom: '1rem',
                opacity: 0.5
              }}>
                🔍
              </div>
              <p style={{ 
                color: '#6b7280', 
                fontSize: '1.125rem', 
                margin: '0 0 0.5rem 0'
              }}>
                "{searchQuery}"에 대한 검색 결과가 없습니다.
              </p>
              <p style={{ 
                color: '#9ca3af', 
                fontSize: '0.875rem', 
                margin: 0
              }}>
                다른 검색어로 시도해보세요.
              </p>
            </div>
          ) : (
            <p style={{ 
              color: '#6b7280', 
              fontSize: '1.125rem', 
              margin: 0 
            }}>
              버전 데이터가 없습니다.
            </p>
          )}
        </div>
      ) : (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
            gap: '1.5rem'
          }}>
            {versions.map((version, index) => {
              const isLast = index === versions.length - 1;
              return (
                <div 
                  key={version.id || `version-${index}`} 
                  style={{
                    background: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                    transition: 'box-shadow 0.2s ease'
                  }}
                  ref={isLast ? lastVersionRef : null}
                  onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}
                  onMouseOut={(e) => e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'}
                >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '1rem'
                }}>
                  <h3 style={{
                    margin: 0,
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    color: '#111827'
                  }}
                  dangerouslySetInnerHTML={{
                    __html: highlightSearchTerm(version.version_name, searchQuery)
                  }}
                  />
                  <span 
                    style={{ 
                      backgroundColor: getStatusColor(version.approval_status),
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}
                  >
                    {getStatusText(version.approval_status)}
                  </span>
                </div>
                
                {version.description && (
                  <p style={{
                    color: '#000',
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    margin: '0 0 1rem 0',
                    lineHeight: '1.5'
                  }}
                  dangerouslySetInnerHTML={{
                    __html: highlightSearchTerm(version.description, searchQuery)
                  }}
                  />
                )}
                
                
                <div style={{
                  fontSize: '0.75rem',
                  color: '#6b7280',
                  marginBottom: '1.5rem',
                  lineHeight: '1.5'
                }}>
                  <div>생성자: {version.created_by}</div>
                  <div>생성일: {version.created_at ? new Date(version.created_at).toLocaleString() : 'N/A'}</div>
                  {version.approved_by && (
                    <div>승인자: {version.approved_by}</div>
                  )}
                  {version.migration_date && (
                    <div>마이그레이션: {new Date(version.migration_date).toLocaleString()}</div>
                  )}
                </div>
                
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '0.5rem'
                }}>
                  {/* 엑셀 업로드 버튼 - 모든 상태에서 표시 */}
                  <button 
                    onClick={() => handleExcelUpload(version)}
                    style={{
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.background = '#2563eb'}
                    onMouseOut={(e) => e.target.style.background = '#3b82f6'}
                  >
                    엑셀 업로드
                  </button>
                  
                  {/* 크롤링 버튼 - 모든 상태에서 표시 */}
                  <button 
                    onClick={() => handleCrawling(version)}
                    style={{
                      background: '#8b5cf6',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.background = '#7c3aed'}
                    onMouseOut={(e) => e.target.style.background = '#8b5cf6'}
                  >
                    크롤링
                  </button>
                  
                  {/* 승인신청 버튼 */}
                  <button 
                    onClick={() => handleApprovalRequest(version)}
                    disabled={version.approval_status === 'PENDING'}
                    style={{
                      background: version.approval_status === 'PENDING' ? '#d1d5db' : '#10b981',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: version.approval_status === 'PENDING' ? 'not-allowed' : 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => {
                      if (version.approval_status !== 'PENDING') {
                        e.target.style.background = '#059669';
                      }
                    }}
                    onMouseOut={(e) => {
                      if (version.approval_status !== 'PENDING') {
                        e.target.style.background = '#10b981';
                      }
                    }}
                  >
                    승인신청
                  </button>
                  
                  {/* Main → Staging 풀 버튼 */}
                  <button 
                    onClick={() => handleDownloadFromMain(version)}
                    style={{
                      background: '#06b6d4',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.background = '#0891b2'}
                    onMouseOut={(e) => e.target.style.background = '#06b6d4'}
                  >
                    메인을 Staging으로
                  </button>
                  
                  {/* 승인/거부 버튼 (PENDING 상태일 때만 표시, 관리자/매니저/대표만) */}
                  {version.approval_status === 'PENDING' && canApprove() && (
                    <>
                      <button 
                        onClick={() => handleApproveVersion(version)}
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
                        ✅ 승인
                      </button>
                      <button 
                        onClick={() => handleRejectVersion(version)}
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
                        ❌ 거부
                      </button>
                    </>
                  )}
                  <button 
                    onClick={() => handleEdit(version)}
                    disabled={version.approval_status === 'MIGRATED'}
                    style={{
                      background: version.approval_status === 'MIGRATED' ? '#d1d5db' : '#6b7280',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: version.approval_status === 'MIGRATED' ? 'not-allowed' : 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => {
                      if (version.approval_status !== 'MIGRATED') {
                        e.target.style.background = '#4b5563';
                      }
                    }}
                    onMouseOut={(e) => {
                      if (version.approval_status !== 'MIGRATED') {
                        e.target.style.background = '#6b7280';
                      }
                    }}
                  >
                    수정
                  </button>
                  <button 
                    onClick={() => handleDelete(version.id)}
                    disabled={version.approval_status === 'MIGRATED'}
                    style={{
                      background: version.approval_status === 'MIGRATED' ? '#d1d5db' : '#ef4444',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: version.approval_status === 'MIGRATED' ? 'not-allowed' : 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => {
                      if (version.approval_status !== 'MIGRATED') {
                        e.target.style.background = '#dc2626';
                      }
                    }}
                    onMouseOut={(e) => {
                      if (version.approval_status !== 'MIGRATED') {
                        e.target.style.background = '#ef4444';
                      }
                    }}
                  >
                    삭제
                  </button>
                  <button 
                    onClick={() => navigate(`/version-data?version_id=${version.id}`)}
                    style={{
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.background = '#d97706'}
                    onMouseOut={(e) => e.target.style.background = '#f59e0b'}
                  >
                    데이터 관리
                  </button>
                </div>
              </div>
              );
            })}
          </div>

          {/* 무한 스크롤 로딩 인디케이터 */}
          {loadingMore && (
            <div className="loading-more">
              <div className="loading-spinner"></div>
              <p>더 많은 버전을 불러오는 중...</p>
            </div>
          )}
          
          {!hasMore && versions.length > 0 && (
            <div className="no-more-data">
              <p>모든 버전을 불러왔습니다.</p>
            </div>
          )}
        </>
      )}

      {/* 생성 모달 */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{
              margin: '0 0 1.5rem 0',
              fontSize: '1.25rem',
              fontWeight: '600',
              color: '#111827'
            }}>
              새 버전 생성
            </h3>
            <div className="form-group">
              <label>버전명 *</label>
              <input
                type="text"
                value={formData.version_name}
                onChange={(e) => setFormData({...formData, version_name: e.target.value})}
                placeholder="예: v1.0.0"
              />
            </div>
            <div className="form-group">
              <label>설명</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="버전에 대한 설명을 입력하세요"
                rows="3"
              />
            </div>
            <div className="form-group">
              <label>생성자</label>
              <input
                type="text"
                value={formData.created_by}
                onChange={(e) => setFormData({...formData, created_by: e.target.value})}
              />
            </div>
            <div className="modal-actions">
              <button onClick={handleCreate} className="confirm-btn">생성</button>
              <button onClick={() => setShowCreateModal(false)} className="cancel-btn">취소</button>
            </div>
          </div>
        </div>
      )}

      {/* 수정 모달 */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>버전 수정</h3>
            <div className="form-group">
              <label>버전명 *</label>
              <input
                type="text"
                value={formData.version_name}
                onChange={(e) => setFormData({...formData, version_name: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>설명</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows="3"
              />
            </div>
            <div className="modal-actions">
              <button onClick={handleUpdate} className="confirm-btn">수정</button>
              <button onClick={() => setShowEditModal(false)} className="cancel-btn">취소</button>
            </div>
          </div>
        </div>
      )}


      {/* 크롤링 모달 */}
      {showCrawlingModal && selectedVersionForCrawling && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>🕷️ 웹 크롤링</h3>
            <div className="version-info">
              <h4>버전: {selectedVersionForCrawling.version_name}</h4>
              {selectedVersionForCrawling.description && (
                <p>{selectedVersionForCrawling.description}</p>
              )}
            </div>
            <p>이 버전에 웹 크롤링을 시작하시겠습니까?</p>
            <div className="modal-actions">
              <button 
                className="confirm-btn"
                onClick={async () => {
                  try {
                    // TODO: 크롤링 API 호출
                    alert('크롤링 기능은 향후 구현 예정입니다.');
                    setShowCrawlingModal(false);
                    setSelectedVersionForCrawling(null);
                    // 크롤링 작업 완료 후 데이터 리패치
                    resetAndLoadVersions();
                  } catch (err) {
                    alert('크롤링 작업에 실패했습니다: ' + (err.response?.data?.detail || err.message));
                  }
                }}
              >
                크롤링 시작
              </button>
              <button 
                className="cancel-btn"
                onClick={() => {
                  setShowCrawlingModal(false);
                  setSelectedVersionForCrawling(null);
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VersionList;
