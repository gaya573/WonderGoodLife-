/**
 * 리팩토링된 VersionCard 컴포넌트
 * 관심사 분리와 재사용성 향상
 */

import React from 'react';
import Card from './ui/Card';
import Button from './ui/Button';
import { useApi } from '../hooks/useApi';
import versionAPI from '../services/versionApi';
import './VersionCard.css';

const VersionCard = ({ version, onEdit, onDelete, onDataManagement }) => {
  const deleteApi = useApi();

  const handleDelete = async () => {
    if (!window.confirm('정말로 이 버전을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await deleteApi.execute(
        () => versionAPI.delete(version.id),
        { 
          context: 'VersionCard.delete',
          onSuccess: () => {
            alert('버전이 성공적으로 삭제되었습니다.');
            window.location.reload(); // TODO: 상태 업데이트로 변경
          }
        }
      );
    } catch (error) {
      // 에러는 useApi에서 자동 처리됨
    }
  };

  const getStatusClasses = () => {
    const statusMap = {
      'PENDING': 'status-pending',
      'APPROVED': 'status-approved',
      'REJECTED': 'status-rejected',
      'MIGRATED': 'status-migrated',
    };
    
    const status = version.approval_status || version.status;
    return `status-badge ${statusMap[status] || 'status-pending'}`;
  };

  const getStatusText = (status) => {
    const statusTexts = {
      'PENDING': '대기중',
      'APPROVED': '승인됨',
      'REJECTED': '거부됨',
      'MIGRATED': '마이그레이션 완료',
    };
    return statusTexts[status] || status;
  };

  const getActionButtons = () => {
    const buttons = [];

    // 데이터 관리 버튼 (항상 표시)
    buttons.push(
      <Button
        key="data-management"
        variant="warning"
        size="sm"
        onClick={() => onDataManagement(version)}
      >
        데이터 관리
      </Button>
    );

    // 상태별 버튼
    const status = version.approval_status || version.status;
    switch (status) {
      case 'PENDING':
        buttons.push(
          <Button
            key="edit"
            variant="secondary"
            size="sm"
            onClick={() => onEdit(version)}
          >
            수정
          </Button>
        );
        buttons.push(
          <Button
            key="delete"
            variant="error"
            size="sm"
            onClick={handleDelete}
            loading={deleteApi.loading}
          >
            삭제
          </Button>
        );
        break;
        
      case 'APPROVED':
        buttons.push(
          <Button
            key="migrate"
            variant="success"
            size="sm"
            onClick={() => {
              if (window.confirm('이 버전을 마이그레이션하시겠습니까?')) {
                // TODO: 마이그레이션 로직
                alert('마이그레이션 기능은 구현 중입니다.');
              }
            }}
          >
            마이그레이션
          </Button>
        );
        break;
    }

    return buttons;
  };

  return (
    <Card interactive>
      {/* 헤더 */}
      <div className="version-card-header">
        <h3 className="version-card-title">
          {version.version_name || version.name}
        </h3>
        <span className={getStatusClasses()}>
          {getStatusText(version.approval_status || version.status)}
        </span>
      </div>

      {/* 설명 */}
      {version.description && (
        <p className="version-card-description">
          {version.description}
        </p>
      )}

      {/* 메타 정보 */}
      <div className="version-card-meta">
        <div>생성자: {version.created_by}</div>
        <div>생성일: {version.created_at ? new Date(version.created_at).toLocaleString() : 'N/A'}</div>
        {version.approved_by && <div>승인자: {version.approved_by}</div>}
        {version.migration_date && (
          <div>마이그레이션: {new Date(version.migration_date).toLocaleString()}</div>
        )}
      </div>

      {/* 액션 버튼들 */}
      <div className="version-card-actions">
        {getActionButtons()}
      </div>
    </Card>
  );
};

export default VersionCard;
