import React, { useState } from 'react';
import styles from './QuickConsult.module.css';
import kakoIcon from '../../assets/icon/kako.png';
import talkIcon from '../../assets/icon/talk.png';
import naverIcon from '../../assets/icon/naver.png';

const QuickConsult = () => {
  const [isOpen, setIsOpen] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('상담 신청이 접수되었습니다.');
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`${styles['quick-consult-sidebar']} ${isOpen ? styles.open : styles.closed}`}>
      {/* <button className="sidebar-toggle-btn" onClick={toggleSidebar} aria-label={isOpen ? '닫기' : '열기'}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button> */}
      
      <div className={styles['quick-consult-card']}>
        <div className={styles['consult-header']}>
          <svg className={styles['phone-icon']} width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M3 5C3 3.89543 3.89543 3 5 3H8.27924C8.70967 3 9.09181 3.27543 9.22792 3.68377L10.7257 8.17721C10.8831 8.64932 10.6694 9.16531 10.2243 9.38787L7.96701 10.5165C9.06925 12.9612 11.0388 14.9308 13.4835 16.033L14.6121 13.7757C14.8347 13.3306 15.3507 13.1169 15.8228 13.2743L20.3162 14.7721C20.7246 14.9082 21 15.2903 21 15.7208V19C21 20.1046 20.1046 21 19 21H18C9.71573 21 3 14.2843 3 6V5Z" stroke="#0062FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>빠른 견적문의</h3>
        </div>
        <div className={styles['consult-phone']}>1577-8319</div>
        
        <form className={styles['consult-form']} onSubmit={handleSubmit}>
          <input className={styles['consult-input']} type="text" placeholder="성함" required />
          <input className={styles['consult-input']} type="tel" placeholder="연락처" required />
          <input className={styles['consult-input']} type="text" placeholder="차종" required />
          
          <div className={styles['privacy-checkbox']}>
            <input type="checkbox" id="privacy-consent" defaultChecked required />
            <label htmlFor="privacy-consent">
              [필수] 개인정보 수집·이용 동의 <span className={styles['view-link']}>[보기]</span>
            </label>
          </div>
          
          <button type="submit" className={styles['consult-submit-btn']}>비대면 상담 신청</button>
        </form>
        
        <div className={styles['other-methods']}>
          <p>다른 방법으로 문의</p>
          <div className={styles['method-icons']}>
            <div className={styles['method-icon']}>
              <img src={kakoIcon} alt="카카오톡" />
            </div>
            <div className={styles['method-icon']}>
              <img src={talkIcon} alt="카카오 채널" />
            </div>
            <div className={styles['method-icon']}>
              <img src={naverIcon} alt="네이버 톡톡" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickConsult;

