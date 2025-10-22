import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import './EstimateModal.css';
import RegionSelect from '../RegionSelect';

const EstimateModal = ({ open, onClose, carName = '', trimName = '' }) => {
  const [customerType, setCustomerType] = useState('개인');
  const [name, setName] = useState('');
  const [birth, setBirth] = useState('');
  const [phone, setPhone] = useState('');
  const [sido, setSido] = useState('');
  const [gungu, setGungu] = useState('');
  const [message, setMessage] = useState('');

  // 공용 RegionSelect 사용

  const CustomSelect = ({ value, onChange, options, placeholder = '', disabled = false }) => {
    const [openMenu, setOpenMenu] = useState(false);
    const ref = useRef(null);

    useEffect(() => {
      const handler = (e) => {
        if (ref.current && !ref.current.contains(e.target)) setOpenMenu(false);
      };
      const esc = (e) => { if (e.key === 'Escape') setOpenMenu(false); };
      document.addEventListener('mousedown', handler);
      document.addEventListener('keydown', esc);
      return () => { document.removeEventListener('mousedown', handler); document.removeEventListener('keydown', esc); };
    }, []);

    const currentLabel = value || '';
    return (
      <div className={`custom-select ${disabled ? 'disabled' : ''}`} ref={ref}>
        <button type="button" className="custom-select-trigger" onClick={() => !disabled && setOpenMenu((v) => !v)}>
          <span>{currentLabel || placeholder}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        {openMenu && !disabled && (
          <div className="custom-select-menu">
            {options.map((opt) => (
              <div key={opt} className={`custom-select-item ${opt === value ? 'selected' : ''}`} onClick={() => { onChange(opt); setOpenMenu(false); }}>
                {opt}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const handleClose = useCallback(() => {
    if (onClose) onClose();
  }, [onClose]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = originalOverflow;
    };
  }, [open, handleClose]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // 실제 전송 로직 연결 지점
    alert('비대면 견적 신청이 접수되었습니다.');
    handleClose();
  };

  if (!open) return null;

  return (
    <div className="estimate-modal" role="dialog" aria-modal="true" onClick={handleClose}>
      <div className="estimate-modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="estimate-modal-header">
          <span className="estimate-modal-title">간편상담</span>
          <button className="estimate-modal-close" aria-label="닫기" onClick={handleClose}>×</button>
        </div>

        <div className="estimate-modal-hero">
          <div className="estimate-car-thumb" />
          <div className="estimate-car-meta">
            <div className="estimate-car-name">{carName}</div>
            {trimName && <div className="estimate-car-trim">{trimName}</div>}
          </div>
        </div>

        <div className="estimate-modal-tabs" role="tablist" aria-label="고객 유형">
          <button
            className={`estimate-tab ${customerType === '개인' ? 'active' : ''}`}
            role="tab"
            aria-selected={customerType === '개인'}
            onClick={() => setCustomerType('개인')}
          >
            개인
          </button>
          <button
            className={`estimate-tab ${customerType === '사업자' ? 'active' : ''}`}
            role="tab"
            aria-selected={customerType === '사업자'}
            onClick={() => setCustomerType('사업자')}
          >
            사업자
          </button>
        </div>

        <form className="estimate-modal-body" onSubmit={handleSubmit}>
          <div className="form-row">
            <input
              type="text"
              placeholder="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-row">
            <input
              type="text"
              placeholder="생년월일 (선택) ex)19910101"
              value={birth}
              onChange={(e) => setBirth(e.target.value)}
              inputMode="numeric"
              pattern="[0-9]*"
            />
          </div>
          <div className="form-row">
            <input
              type="tel"
              placeholder="연락처"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
          </div>
          <RegionSelect valueSido={sido} valueGungu={gungu} onChangeSido={setSido} onChangeGungu={setGungu} />
          <div className="form-row">
            <textarea
              placeholder="문의사항"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
            />
          </div>
          <label className="privacy-row">
            <input type="checkbox" name="privacy" value="true" checked onChange={() => {}} className="locked-checkbox" />
            <span>개인정보 수집 · 이용 동의</span>
          </label>

          <button type="submit" className="submit-btn">비대면 견적 신청</button>
        </form>
      </div>
    </div>
  );
};

export default EstimateModal;


