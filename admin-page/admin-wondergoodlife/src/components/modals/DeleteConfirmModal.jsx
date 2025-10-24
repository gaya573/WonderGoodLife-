import './DeleteConfirmModal.css';

function DeleteConfirmModal({ title, onConfirm, onCancel }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-container delete-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>정책 삭제 확인</h2>
        </div>
        <div className="modal-body">
          <div className="delete-icon">⚠️</div>
          <p>정말로 이 정책을 삭제하시겠습니까?</p>
          <p className="delete-target"><strong>{title}</strong></p>
          <p className="delete-warning">이 작업은 되돌릴 수 없습니다.</p>
        </div>
        <div className="modal-footer">
          <button className="cancel-button" onClick={onCancel}>
            취소
          </button>
          <button className="confirm-button delete" onClick={onConfirm}>
            삭제
          </button>
        </div>
      </div>
    </div>
  );
}

export default DeleteConfirmModal;

