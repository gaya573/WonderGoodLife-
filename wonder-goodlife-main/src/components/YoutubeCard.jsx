import React from 'react';
import './YoutubeCard.css';
import channelImage from '../assets/img/youtube/image.png';

const YoutubeCard = () => {
  // 3개의 영상 데이터
  const videos = [
    {
      id: 'dQw4w9WgXcQ',
      title: '벤츠 마지막 재고 할인!!',
      subtitle: '10월 역대급 딜의 할인 대방출'
    },
    {
      id: 'jNQXAC9IVRw',
      title: '10월 최신 현대 기아 출고기',
      subtitle: '결국 눈물의 재고 떨이..'
    },
    {
      id: 'M7lc1UVf-VE',
      title: '결국 완판! 신차 나온다고?',
      subtitle: '폭스바겐 대신 10월엔 아우디?'
    }
  ];

  const handleVideoClick = (videoId) => {
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
          <div className="youtube-title-section-left">
          <div className="youtube-logo-icon">📺</div>
           <h2 className="youtube-main-title">원더굿라이프 유튜브</h2>
        
          </div>
          <p className="youtube-subtitle">차량 리뷰와 딜을 유튜브에서 생생하게 확인하세요</p>
        </div>

   
      </div>

      {/* 콘텐츠 영역: 3개 영상 + 설명 */}
      <div className="youtube-content">
        {/* 왼쪽: 3개 영상 썸네일 */}
        <div className="videos-grid">
          {videos.map((video, index) => (
            <div 
              key={video.id} 
              className="video-thumbnail-wrapper" 
              onClick={() => handleVideoClick(video.id)}
            >
              <div className="video-thumbnail-placeholder">
                <div className="placeholder-content">
                  <div className="placeholder-icon">🎬</div>
                  <div className="placeholder-text">영상 {index + 1}</div>
                </div>
              </div>
              <div className="video-overlay">
                <div className="play-button-circle">
                  <div className="play-icon">▶</div>
                </div>
                <div className="video-text-banner">
                  <div className="video-title-main">{video.title}</div>
                  <div className="video-title-highlight">{video.subtitle}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
      {/* 하단 버튼 */}
      <div className="youtube-bottom-button">
        <button className="more-videos-btn" onClick={handleChannelClick}>
          더많은 차량 할인·팁 영상 보러가기 →
        </button>
      </div>
    </div>
  );
};

export default YoutubeCard;

