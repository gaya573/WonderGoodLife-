export const cardBrandCards = {
  '신한': [
    { id: 101, brand: '신한', name: '신한카드', desc: '전월실적별 추가 청구할인', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=21' },
  ],
  'KB국민': [
    { id: 102, brand: 'KB국민', name: 'KB국민카드', desc: '신규/전환 고객 캐시백 최대 7만', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=22' },
  ],
  '현대': [
    { id: 103, brand: '현대', name: '현대카드', desc: '무이자 24개월 + 부분 캐시백', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=23' },
  ],
  '롯데': [
    { id: 104, brand: '롯데', name: '롯데카드', desc: '특별 제휴 프로모션 진행중', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=24' },
  ],
  '하나': [
    { id: 105, brand: '하나', name: '하나카드', desc: '무이자/캐시백 혜택', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=25' },
  ],
  '삼성': [
    { id: 106, brand: '삼성', name: '삼성카드', desc: '특별 청구할인', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=26' },
  ],
  'BC': [
    { id: 107, brand: 'BC', name: 'BC카드', desc: '여름 한정 이벤트', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=27' },
  ],
  'NH농협': [
    { id: 108, brand: 'NH농협', name: '농협카드', desc: '첫 결제 고객 리워드', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=28' },
  ],
  '우리': [
    { id: 109, brand: '우리', name: '우리카드', desc: '청구할인 + 포인트 적립', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=29' },
  ],
  '카카오뱅크': [
    { id: 110, brand: '카카오뱅크', name: '카카오뱅크', desc: '특별 캐시백', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&h=560&fit=crop&sig=30' },
  ],
};

export const allCardBrandCards = Object.values(cardBrandCards).flat();

export const findCardBrandById = (id) => allCardBrandCards.find(c => String(c.id) === String(id));


