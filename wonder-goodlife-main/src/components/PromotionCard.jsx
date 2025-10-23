import React from 'react';
import styles from './PromotionCard.module.css';

const PromotionCard = ({ 
  id, 
  name, 
  desc, 
  img, 
  brand, 
  onClick,
  buttonText = "혜택 상담 받기",
  ended = false,
  variant = "normal" // "small" 또는 "normal" 또는 "big"
}) => {
  return (
    <article 
      className={`${styles['promo-card']} ${ended ? styles['ended'] : ''} ${variant === 'small' ? styles['small-card'] : ''} ${variant === 'big' ? styles['big-card'] : ''}`}
      onClick={() => onClick && onClick(id)}
    >
      <div className={styles['promo-card-top']}>
        <img src={img} alt={name} loading="lazy" />
      </div>
      <div className={styles['promo-card-body']}>
        <h3>{name}</h3>
        <p>{desc}</p>
      </div>
      <button
        className={styles['promo-card-btn']}
        onClick={(e) => {
          e.stopPropagation();
          onClick && onClick(id);
        }}
      >
        {buttonText}
      </button>
    </article>
  );
};

export default PromotionCard;
