import React from 'react';
import './YoutubeCard.css';
import channelImage from '../assets/img/youtube/image.png';

const YoutubeCard = () => {
  // 원더굿라이프 채널의 실제 영상 ID (예시)
  const videoId = 'dQw4w9WgXcQ'; // 실제 영상 ID로 교체 가능
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;

  const handleVideoClick = () => {
    window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
  };

  const handleChannelClick = () => {
    window.open('https://www.youtube.com/@WonderGoodLife', '_blank');
  };

  return (
    <div className="youtube-card">
      {/* 최상단: 제목 + 채널 정보 */}
      <div className="youtube-header">
        {/* 왼쪽: 제목과 부제 */}
        <div className="youtube-title-section">
          <h2 className="youtube-main-title">원더굿라이프 유튜브</h2>
          <p className="youtube-subtitle">차량 리뷰와 딜을 유튜브에서 생생하게 확인하세요</p>
        </div>

 
      </div>

      {/* 콘텐츠 영역: 영상 + 설명 */}
      <div className="youtube-content">
        {/* 왼쪽: 영상 썸네일 */}
        <div className="video-thumbnail-wrapper" onClick={handleVideoClick}>
          <img 
            src={thumbnailUrl} 
            alt="유튜브 영상 썸네일" 
            className="video-thumbnail-image"
          />
          <div className="video-overlay">
            <div className="play-button-circle">
              <div className="play-icon">▶</div>
            </div>
            <div className="video-text-banner">
              <div className="video-title-main">벤츠 마지막 재고 할인!!</div>
              <div className="video-title-highlight">10월 역대급 딜의 할인 대방출</div>
            </div>
          </div>
        </div>

        {/* 오른쪽: 설명 텍스트 */}
        <div className="channel-description">
          <div className="channel-info-card">
            <img 
              src={channelImage} 
              alt="원더굿라이프 채널"
              className="channel-info-image"
              onClick={handleChannelClick}
            />
          </div>

<div className='gray'>
          <div className="description-intro">유튜브 채널에서는 👇</div>
          <div className="description-list">
            <div className="description-item description-spacer"></div>
            <div className="description-item description-spacer"></div>
            <div className="description-item">
              #실시간 특가 차량 정보부터 리얼 출고 후기까지!
            </div>
            <div className="description-item">
              #장기렌트·리스·할부 비교 노하우와 금융 혜택 AtoZ
            </div>
            <div className="description-item">
              #전문가 꿀팁과 고객님의 리얼 인터뷰, 모두 이곳에!
            </div>
          </div>

          </div>

        </div>
      </div>
    </div>
  );
};

export default YoutubeCard;

