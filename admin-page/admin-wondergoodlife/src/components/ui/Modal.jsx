/**
 * 재사용 가능한 Modal 컴포넌트
 */

import React, { useEffect } from 'react';
import Button from './Button';
import './Modal.css';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  className = '',
}) => {
  // ESC 키로 모달 닫기
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // 배경 스크롤 방지
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const getModalClasses = () => {
    const classes = ['modal-content', `modal-${size}`];
    if (className) {
      classes.push(className);
    }
    return classes.join(' ');
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className={getModalClasses()}>
        {/* 헤더 */}
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && <h3 className="modal-title">{title}</h3>}
            {showCloseButton && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="modal-close-btn"
              >
                ✕
              </Button>
            )}
          </div>
        )}

        {/* 컨텐츠 */}
        <div className={title ? 'modal-body-with-header' : 'modal-body'}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
