import { useNavigate } from 'react-router-dom';

/**
 * 빈 상태를 표시하는 재사용 가능한 컴포넌트
 */
function EmptyState({ 
  icon = "📋", 
  title = "데이터가 없습니다", 
  description = "표시할 데이터가 없습니다.", 
  buttonText = "새로 만들기",
  onButtonClick,
  buttonNavigateTo
}) {
  const navigate = useNavigate();

  const handleButtonClick = () => {
    if (onButtonClick) {
      onButtonClick();
    } else if (buttonNavigateTo) {
      navigate(buttonNavigateTo);
    }
  };

  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3 className="empty-title">{title}</h3>
      <p className="empty-description">{description}</p>
      {(onButtonClick || buttonNavigateTo) && (
        <button 
          className="action-btn btn-edit"
          onClick={handleButtonClick}
        >
          📝 {buttonText}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
