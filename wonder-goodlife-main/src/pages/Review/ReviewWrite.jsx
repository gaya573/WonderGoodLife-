import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import Breadcrumb from '../../components/Breadcrumb';
import QuickConsult from '../../components/layout/QuickConsult';
import styles from './ReviewWrite.module.css';

/**
 * ReviewWrite 페이지 컴포넌트
 * 새 리뷰 작성 페이지
 */
const ReviewWrite = () => {
  const navigate = useNavigate();
  
  // 폼 데이터 상태 관리
  const [formData, setFormData] = useState({
    author: '',
    sido: '',
    gugun: '',
    carBrand: '',
    carModel: '',
    rating: 0,
    content: '',
    images: []
  });

  // 브레드크럼 아이템
  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '후기·리뷰', link: '/review' },
    { label: '작성하기' }
  ];

  /**
   * 입력 필드 변경 처리
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 시·도 / 구·군 데이터 (필요 시 확장 가능)
  const SIDO_LIST = [
    '서울특별시',
    '경기도',
    '인천광역시',
    '부산광역시',
  ];
  const GUGUN_MAP = {
    '서울특별시': ['강남구', '서초구', '송파구', '마포구', '영등포구'],
    '경기도': ['수원시', '성남시', '용인시', '고양시', '안양시'],
    '인천광역시': ['남동구', '연수구', '부평구', '계양구'],
    '부산광역시': ['해운대구', '수영구', '남구', '북구'],
  };

  const handleSidoChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, sido: value, gugun: '' }));
  };

  const handleGugunChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, gugun: value }));
  };

  // 차량 브랜드/모델 데이터
  const CAR_BRANDS = [
    '현대',
    '기아',
    '제네시스',
    '쉐보레',
    '르노코리아',
    'BMW',
    '벤츠',
    '아우디',
    '폭스바겐',
    '볼보',
    '렉서스',
    '인피니티',
    '혼다',
    '도요타',
    '닛산',
    '마쓰다',
    '미쓰비시',
    '스즈키',
    '기타'
  ];

  const CAR_MODELS = {
    '현대': ['아반떼', '소나타', '그랜저', '캐스퍼', '코나', '투싼', '싼타페', '팰리세이드', '넥쏘', '아이오닉'],
    '기아': ['K3', 'K5', 'K7', 'K8', 'K9', '모닝', '레이', '쏘울', '스포티지', '쏘렌토', '모하비', '카니발'],
    '제네시스': ['G70', 'G80', 'G90', 'GV70', 'GV80'],
    '쉐보레': ['스파크', '아베오', '크루즈', '말리부', '카마로', '콜벳', '트래버스', '타호'],
    'BMW': ['1시리즈', '2시리즈', '3시리즈', '5시리즈', '7시리즈', 'X1', 'X3', 'X5', 'X7'],
    '벤츠': ['A클래스', 'C클래스', 'E클래스', 'S클래스', 'GLA', 'GLC', 'GLE', 'GLS'],
    '아우디': ['A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8'],
    '폭스바겐': ['골프', '제타', '파사트', '티구안', '투렉', '아테온'],
    '볼보': ['S60', 'S90', 'XC40', 'XC60', 'XC90'],
    '렉서스': ['IS', 'ES', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX'],
    '인피니티': ['Q50', 'Q60', 'QX50', 'QX60', 'QX80'],
    '혼다': ['시빅', '어코드', 'CR-V', '파일럿', '리지드'],
    '도요타': ['캠리', '프리우스', 'RAV4', '하이랜더', '시에나'],
    '닛산': ['센트라', '알티마', '로그', '무라노', '패스파인더'],
    '마쓰다': ['마즈다3', '마즈다6', 'CX-5', 'CX-9'],
    '미쓰비시': ['아웃랜더', '이클립스 크로스'],
    '스즈키': ['스위프트', '스위프트 스포츠'],
    '기타': ['기타']
  };

  const handleCarBrandChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, carBrand: value, carModel: '' }));
  };

  const handleCarModelChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, carModel: value }));
  };

  /**
   * 별점 클릭 처리
   */
  const handleRatingClick = (rating) => {
    setFormData(prev => ({
      ...prev,
      rating: rating
    }));
  };

  /**
   * 별점 렌더링 함수
   */
  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span 
          key={i} 
          className={`${styles.star} ${i <= formData.rating ? styles.filledStar : styles.emptyStar}`}
          onClick={() => handleRatingClick(i)}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  /**
   * 이미지 업로드 변경 처리 (다중 파일)
   */
  const handleImageChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const nextImages = files.map((file) => ({
      file,
      url: URL.createObjectURL(file)
    }));

    setFormData((prev) => ({
      ...prev,
      images: [...prev.images, ...nextImages]
    }));
  };

  /**
   * 개별 업로드 이미지 제거
   */
  const handleRemoveImage = (idx) => {
    setFormData((prev) => {
      const next = [...prev.images];
      const removed = next.splice(idx, 1)[0];
      if (removed?.url) URL.revokeObjectURL(removed.url);
      return { ...prev, images: next };
    });
  };

  /**
   * 폼 제출 처리
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('리뷰 작성:', formData);
    alert('리뷰가 성공적으로 작성되었습니다!');
    navigate('/review');
  };

  /**
   * 취소 처리
   */
  const handleCancel = () => {
    navigate('/review');
  };

  return (
    <div className={styles.reviewWritePage}>

      {/* 메인 컨텐츠 */}
      <div className={styles.mainContent}>
        {/* 브레드크럼 */}
        <Breadcrumb items={breadcrumbItems} />
        
        {/* 페이지 헤더 */}
        <div className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>작성하기</h1>
        </div>

        {/* 리뷰 작성 레이아웃 */}
        <div className={styles.writeLayout}>
          {/* 작성 폼 섹션 */}
          <div className={styles.writeSection}>
            <h2 className={styles.formTitle}>작성하기</h2>
            <form onSubmit={handleSubmit} className={styles.reviewForm}>
              {/* 작성자 */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>작성자</label>
                <input
                  type="text"
                  name="author"
                  value={formData.author}
                  onChange={handleInputChange}
                  className={styles.formInput}
                  placeholder="예시) 임미희"
                  required
                />
              </div>

              {/* 지역 (시·도 / 구·군) */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>지역</label>
                <div className={styles.selectRow}>
                  <select
                    name="sido"
                    value={formData.sido}
                    onChange={handleSidoChange}
                    className={styles.formSelect}
                    required
                  >
                    <option value="" disabled>시·도</option>
                    {SIDO_LIST.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <select
                    name="gugun"
                    value={formData.gugun}
                    onChange={handleGugunChange}
                    className={styles.formSelect}
                    required
                    disabled={!formData.sido}
                  >
                    <option value="" disabled>구·군</option>
                    {(GUGUN_MAP[formData.sido] || []).map((g) => (
                      <option key={g} value={g}>{g}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 차종 */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>차종</label>
                <input
                  type="text"
                  name="carModel"
                  value={formData.carModel}
                  onChange={handleInputChange}
                  className={styles.formInput}
                  placeholder="예시) 기아 카니발"
                  required
                />
              </div>

              {/* 별점 */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>별점</label>
                <div className={styles.ratingContainer}>
                  <div className={styles.stars}>
                    {renderStars()}
                  </div>
                  <span className={styles.ratingNumber}>
                    {formData.rating > 0 ? `${formData.rating}.0` : ''}
                  </span>
                </div>
              </div>

              {/* 사진 업로드 */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>사진</label>
                <div className={styles.imageUploadArea}>
                  {/* 파일 입력 (시각적으로 숨김) */}
                  <input
                    id="review-image-input"
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                  <button
                    type="button"
                    className={styles.uploadPlaceholder}
                    onClick={() => document.getElementById('review-image-input')?.click()}
                  >
                    <span className={styles.uploadIcon}>↑</span>
                  </button>

                  {/* 미리보기 그리드 */}
                  {formData.images?.length > 0 && (
                    <div className={styles.previewGrid}>
                      {formData.images.map((img, idx) => (
                        <div key={idx} className={styles.previewItem}>
                          <img src={img.url} alt={`첨부 ${idx + 1}`} />
                          <button
                            type="button"
                            className={styles.previewRemove}
                            onClick={() => handleRemoveImage(idx)}
                            aria-label="이미지 삭제"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* 내용 */}
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>내용</label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  className={styles.formTextarea}
                  placeholder="리뷰 내용을 작성해주세요..."
                  rows={8}
                  required
                />
              </div>

              {/* 폼 액션 버튼 */}
              <div className={styles.formActions}>
                <button type="button" className={styles.cancelButton} onClick={handleCancel}>
                  취소
                </button>
                <button type="submit" className={styles.submitButton}>
                  작성하기
                </button>
              </div>
            </form>
          </div>

          {/* 가이드라인 섹션 */}
          <div className={styles.guideSection}>
            <div className={styles.writeGuide}>
              <h4>계약후기(리뷰) 작성 시 유의사항 - WONDERGOODLIFE 안내</h4>
              <ul>
                <li>차량 사진은 필수로 첨부 부탁드립니다.</li>
                <li>원더굿라이프의 후기 작성은 고객님의 개인정보 보호와 편의를 위해 회원가입 후 비인증 상태에서도 자유롭게 작성 하실 수 있습니다.</li>
                <li>게시판 성격에 맞지 않는 광고성 게시물, 비방, 상업적 글 등은 운영정책에 따라 사전 통보 없이 검수 후 삭제 및 등록 제한이 될 수 있습니다.</li>
                <li>작성 시에도 내부 검수 및 이미지 확인 절차를 거쳐 등록되며, 허위 후기 방지를 위해 실제 계약 고객 우선 검증 후 게시됩니다.</li>
                <li>원더굿라이프는 고객님께서 남겨주신 모든 리뷰와 의견을 소중히 다루며, 서비스 품질 향상 및 신뢰도 개선에 적극 반영하고 있습니다.</li>
                <li>후기 작성은 100자 이상 1,000자 이하로 작성해 주세요.</li>
                <li>구체적인 계약 경험이나 만족도를 함께 남겨주시면 다른 고객분들께 도움이 됩니다.</li>
              </ul>
            </div>
          </div>

          {/* 우측 고정 사이드바 */}
          <div className={styles.rightSidebar}>
            <div className={styles.bulletinBoard}>
              <div className={styles.boardHeader}>
                <h3>게시판</h3>
                <a href="#" className={styles.moreLink}>더보기</a>
              </div>
              <div className={styles.boardList}>
                <ul>
                  <li>
                    <a href="#" className={styles.boardItem}>
                      <span className={styles.boardTitle}>신규 차량 출시 안내</span>
                      <span className={styles.boardDate}>2024.01.15</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className={styles.boardItem}>
                      <span className={styles.boardTitle}>겨울철 차량 관리 팁</span>
                      <span className={styles.boardDate}>2024.01.14</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className={styles.boardItem}>
                      <span className={styles.boardTitle}>이벤트 진행 안내</span>
                      <span className={styles.boardDate}>2024.01.13</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className={styles.boardItem}>
                      <span className={styles.boardTitle}>고객 서비스 개선</span>
                      <span className={styles.boardDate}>2024.01.12</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className={styles.boardItem}>
                      <span className={styles.boardTitle}>리뷰 작성 가이드</span>
                      <span className={styles.boardDate}>2024.01.11</span>
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* 푸터 */}
      <Footer />
    </div>
  );
};

export default ReviewWrite;
