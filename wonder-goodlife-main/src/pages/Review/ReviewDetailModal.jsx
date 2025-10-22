import React, { useState } from 'react';
import styles from './ReviewDetailModal.module.css';

/**
 * ReviewDetailModal 컴포넌트
 * 리뷰 상세 보기 및 새 리뷰 작성 모달
 * 
 * @param {Object} props - 컴포넌트 props
 * @param {boolean} props.isOpen - 모달 열림 상태
 * @param {Function} props.onClose - 모달 닫기 함수
 * @param {Object} props.reviewData - 리뷰 데이터 (상세 보기 모드일 때)
 * @param {boolean} props.isWritingMode - 작성 모드 여부
 */
const ReviewDetailModal = ({ isOpen, onClose, reviewData, isWritingMode }) => {
  // 작성 모드 상태 관리
  const [formData, setFormData] = useState({
    productName: '',
    reviewText: '',
    rating: 0,
    author: ''
  });

  // 모달이 닫힐 때 폼 데이터 초기화
  React.useEffect(() => {
    if (!isOpen) {
      setFormData({
        productName: '',
        reviewText: '',
        rating: 0,
        author: ''
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  /**
   * 별점 렌더링 함수
   * @param {number} rating - 별점 (1-5)
   * @param {boolean} interactive - 클릭 가능한 별점인지 여부
   * @returns {Array} 별점 요소 배열
   */
  const renderStars = (rating, interactive = false) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span 
          key={i} 
          className={`${styles.star} ${i < rating ? styles.filledStar : styles.emptyStar} ${interactive ? styles.interactiveStar : ''}`}
          onClick={interactive ? () => setFormData(prev => ({ ...prev, rating: i + 1 })) : undefined}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  /**
   * 폼 제출 처리
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (isWritingMode) {
      // 새 리뷰 작성 로직
      console.log('새 리뷰 작성:', formData);
      alert('리뷰가 성공적으로 작성되었습니다!');
    }
    onClose();
  };

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

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        {/* 모달 헤더 */}
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>
            {isWritingMode ? '새 리뷰 작성' : '고객 후기'}
          </h2>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>

        {/* 모달 본문 */}
        <div className={styles.modalBody}>
          {/* 이미지 영역 */}
          <div className={styles.imageContainer}>
            {isWritingMode ? (
              <div className={styles.imagePlaceholder}>
                <span className={styles.placeholderText}>이미지 업로드</span>
              </div>
            ) : (
              <div className={styles.imagePlaceholder}>
                <span className={styles.placeholderText}>이미지</span>
              </div>
            )}
          </div>

          {isWritingMode ? (
            /* 작성 모드 폼 */
            <form onSubmit={handleSubmit} className={styles.reviewForm}>
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>제품명 *</label>
                <input
                  type="text"
                  name="productName"
                  value={formData.productName}
                  onChange={handleInputChange}
                  className={styles.formInput}
                  placeholder="제품명을 입력해주세요"
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>작성자 *</label>
                <input
                  type="text"
                  name="author"
                  value={formData.author}
                  onChange={handleInputChange}
                  className={styles.formInput}
                  placeholder="작성자명을 입력해주세요"
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>별점 *</label>
                <div className={styles.ratingInput}>
                  {renderStars(formData.rating, true)}
                  <span className={styles.ratingText}>
                    {formData.rating > 0 ? `${formData.rating}점` : '별점을 선택해주세요'}
                  </span>
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>리뷰 내용 *</label>
                <textarea
                  name="reviewText"
                  value={formData.reviewText}
                  onChange={handleInputChange}
                  className={styles.formTextarea}
                  placeholder="리뷰를 작성해주세요..."
                  rows={6}
                  required
                />
              </div>

              <div className={styles.formActions}>
                <button type="button" className={styles.cancelButton} onClick={onClose}>
                  취소
                </button>
                <button type="submit" className={styles.submitButton}>
                  리뷰 작성하기
                </button>
              </div>
            </form>
          ) : (
            /* 상세 보기 모드 */
            <div className={styles.reviewDetail}>
              <h3 className={styles.productName}>{reviewData?.productName}</h3>
              <p className={styles.reviewText}>{reviewData?.reviewTextFull}</p>
              <div className={styles.rating}>
                {renderStars(reviewData?.rating || 0)}
              </div>
              <div className={styles.metaInfo}>
                <span className={styles.author}>{reviewData?.author}</span>
                <span className={styles.date}>{reviewData?.date}</span>
              </div>
              <div className={styles.detailActions}>
                <button className={styles.submitButton} onClick={() => {
                  // 상세 보기에서도 작성 모드로 전환 가능
                  console.log('리뷰 작성 모드로 전환');
                }}>
                  내 후기 작성하기
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewDetailModal;
