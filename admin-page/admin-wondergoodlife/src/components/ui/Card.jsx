/**
 * 재사용 가능한 Card 컴포넌트
 */

import React from 'react';
import './Card.css';

const Card = ({
  children,
  padding = 'md',
  interactive = false,
  className = '',
  onClick,
  ...props
}) => {
  const getCardClasses = () => {
    const classes = ['card', `card-padding-${padding}`];
    
    if (interactive) {
      classes.push('card-interactive');
    }
    
    if (className) {
      classes.push(className);
    }
    
    return classes.join(' ');
  };

  return (
    <div
      className={getCardClasses()}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
