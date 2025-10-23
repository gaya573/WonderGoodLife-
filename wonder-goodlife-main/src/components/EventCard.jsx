import React from 'react';
import styles from './EventCard.module.css';

const EventCard = ({
  title,
  subtitle = "EVENT",
  image,
  description,
  theme = "default",
  ended = false,
  onClick
}) => {
  return (
    <div className={styles['event-card-wrapper']}>
      <div 
        className={`${styles['event-card']} ${styles[`theme-${theme}`]} ${ended ? styles['ended'] : ''}`}
        onClick={onClick}
      >
     
        {/* 중앙 이미지 영역 */}
        <div className={styles['event-image-area']}>
          <img 
            src={image} 
            alt={title}
            className={styles['event-car-image']}
          />
        </div>
      </div>
      
      {/* 카드 외부 설명 텍스트 */}
      {description && (
        <p className={styles['event-description']}>{description}</p>
      )}
    </div>
  );
};

export default EventCard;
