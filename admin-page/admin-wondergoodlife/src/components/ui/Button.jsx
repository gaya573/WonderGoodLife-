/**
 * 재사용 가능한 Button 컴포넌트
 * 일관된 디자인 시스템 적용
 */

import React from 'react';
import './Button.css';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const getButtonClasses = () => {
    const classes = ['btn', `btn-${size}`, `btn-${variant}`];
    
    if (loading || disabled) {
      classes.push('btn-loading');
    }
    
    if (className) {
      classes.push(className);
    }
    
    return classes.join(' ');
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={getButtonClasses()}
      {...props}
    >
      {loading ? (
        <>
          <span className="btn-loading-icon">⏳</span>
          처리중...
        </>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
