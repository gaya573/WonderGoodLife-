import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import Breadcrumb from '../../components/Breadcrumb';
import QuickConsult from '../../components/layout/QuickConsult';
import ReviewCard from './ReviewCard';
import ReviewDetailModal from './ReviewDetailModal';
import { reviews } from './reviewData';
import styles from './Review.module.css';

/**
 * Review 페이지 컴포넌트
 * 리뷰 목록을 표시하고 리뷰 상세 보기/작성 기능을 제공
 */
const Review = () => {
  const navigate = useNavigate();
  
  // 모달 상태 관리 (상세 보기용)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);

  // 브레드크럼 아이템
  const breadcrumbItems = [
    { label: '홈', link: '/' },
    { label: '후기·리뷰' }
  ];

  /**
   * 리뷰 카드 클릭 처리
   * @param {Object} review - 선택된 리뷰 데이터
   */
  const handleReviewClick = (review) => {
    setSelectedReview(review);
    setIsModalOpen(true);
  };

  /**
   * 새 리뷰 작성 버튼 클릭 처리
   */
  const handleWriteReviewClick = () => {
    navigate('/review/write');
  };

  /**
   * 모달 닫기 처리
   */
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedReview(null);
  };

  return (
    <div className={styles.reviewPage}>

      
      {/* 메인 컨텐츠 */}
      <div className={styles.mainContent}>
        {/* 브레드크럼 */}
        <Breadcrumb items={breadcrumbItems} />
        
        {/* 페이지 헤더 */}
        <div className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>리뷰 - 후기</h1>
        </div>

        {/* 리뷰 레이아웃 */}
        <div className={styles.reviewLayout}>
          {/* 리뷰 섹션 */}
          <div className={styles.reviewSection}>
            {/* 리뷰 그리드 */}
            <div className={styles.reviewGrid}>
              {reviews.map((review) => (
                <ReviewCard
                  key={review.id}
                  review={review}
                  onClick={() => handleReviewClick(review)}
                />
              ))}
            </div>

            {/* 후기 작성하기 버튼 */}
            <div className={styles.writeReviewSection}>
              <button 
                className={styles.writeReviewButton} 
                onClick={handleWriteReviewClick}
              >
                후기 작성하기
              </button>
            </div>
          </div>

    
        </div>
      </div>

   
      {/* 리뷰 상세 모달 */}
      {isModalOpen && (
        <ReviewDetailModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          reviewData={selectedReview}
          isWritingMode={false}
        />
      )}
    </div>
  );
};

export default Review;
