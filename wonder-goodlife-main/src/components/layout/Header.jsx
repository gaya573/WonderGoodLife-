import React, { useState, useRef, useEffect } from 'react';
import { Link, NavLink } from 'react-router-dom';
import SearchBar from '../SearchBar';
import './Header.css';

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isMegaOpen, setIsMegaOpen] = useState(false);
  const megaRef = useRef(null);
  const toggleBtnRef = useRef(null);

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
    // 검색 로직 구현 (필요시)
  };

  // 바깥 클릭 시 닫힘
  useEffect(() => {
    const onDocClick = (e) => {
      if (!isMegaOpen) return;
      const clickedInsideMenu = megaRef.current && megaRef.current.contains(e.target);
      const clickedOnToggleBtn = toggleBtnRef.current && toggleBtnRef.current.contains(e.target);
      if (!clickedInsideMenu && !clickedOnToggleBtn) {
        setIsMegaOpen(false);
      }
    };
    const onEsc = (e) => {
      if (e.key === 'Escape') setIsMegaOpen(false);
    };
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onEsc);
    };
  }, [isMegaOpen]);

  return (
    <header className="header">
      {/* 상단 링크 */}
      <div className="top-bar">
        <div className="top-links">
          <a href="#">로그인</a>
          <a href="#">회원가입</a>
          <a href="#">회사소개</a>
        </div>
      </div>

      {/* 중간 바: 왼쪽 로고 / 오른쪽 메뉴+검색 */}
      <div className="middle-bar">
        <Link to="/" className="logo-section">
          <div className="logo-icon"></div>
          <span className="logo-text">원더굿라이프</span>
        </Link>

        <div className="right-area">
          
          <SearchBar 
            value={searchQuery}
            onChange={handleSearch}
            placeholder="검색어를 입력해 주세요"
            className="header-search"
          />
          
          <div className="right-links">
            <a href="#">장기렌트/리스</a>
            <a href="#">커뮤니티</a>
          </div>

        </div>
      </div>

      {/* 하단 메뉴 */}
      <div className="bottom-bar">
        <button
          type="button"
          className={`hamburger-menu${isMegaOpen ? ' active' : ''}`}
          aria-expanded={isMegaOpen}
          aria-controls="mega-menu"
          aria-haspopup="true"
          aria-pressed={isMegaOpen}
          ref={toggleBtnRef}
          onClick={() => setIsMegaOpen((v) => !v)}
        >
          <span className="hamburger-icon"/>
        </button>
        <nav className="nav-links">
          <NavLink 
            to="/carlist/domestic"
            className={({ isActive }) => isActive ? 'active' : ''}
          >
            견적내기
          </NavLink>
          <NavLink to="/express-deals" className={({ isActive }) => isActive ? 'active' : ''}>
            특가 즉시출고
          </NavLink>
          <NavLink to="/promotion" className={({ isActive }) => isActive ? 'active' : ''}>브랜드별 혜택</NavLink>
          <NavLink to="/review" className={({ isActive }) => isActive ? 'active' : ''}>후기·리뷰</NavLink>
          <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>상담·문의</NavLink>
          <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>비교·계산</NavLink>
        </nav>
      </div>

      {/* 메가메뉴 */}
      <div
        id="mega-menu"
        ref={megaRef}
        className={`mega-menu${isMegaOpen ? ' open' : ''}`}
        role="menu"
        aria-hidden={!isMegaOpen}
        style={{ zIndex: 1025 }}
      >
        <div className="mega-inner">
          <div className="mega-col mega-spacer" />
          <div className="mega-col">
            <ul>
              <li><NavLink to="/carlist/domestic">국산차</NavLink></li>
              <li><NavLink to="/carlist/imported">수입차</NavLink></li>
            </ul>
          </div>
          <div className="mega-col">
            <ul>
              <li><NavLink to="/express-deals">재고보유</NavLink></li>
              <li><NavLink to="/prepurchase-deals">선구매 핫딜 특가</NavLink></li>
            </ul>
          </div>
          <div className="mega-col">
            <ul>
              <li><NavLink to="/promotion">브랜드별 혜택</NavLink></li>
              <li><NavLink to="/card-promotion">카드사 / 캐시백</NavLink></li>
            </ul>
          </div>
          <div className="mega-col">
            <ul>
              <li><NavLink to="/review">실출고 후기</NavLink></li>
            </ul>
          </div>
          <div className="mega-col">
            <ul>
              <li><span className="disabled-link">빠른견적요청</span></li>
              <li><span className="disabled-link">카톡상담·전화</span></li>
              <li><span className="disabled-link">방문예약</span></li>
              <li><span className="disabled-link">간편심사 해보기</span></li>
            </ul>
          </div>
          <div className="mega-col">
            <ul>
              <li><span className="disabled-link">월납입비교</span></li>
              <li><span className="disabled-link">장기렌트 vs 리스 vs 할부</span></li>
              <li><span className="disabled-link">세금/부가세/정비처리</span></li>
              <li><span className="disabled-link">보험료추정</span></li>
            </ul>
          </div>
  
         
        </div>
      </div>
    </header>
  );
};

export default Header;
