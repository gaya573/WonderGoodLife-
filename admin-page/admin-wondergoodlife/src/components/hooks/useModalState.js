import { useState } from 'react';

/**
 * 모달 상태 관리 커스텀 훅
 * 편집/추가 모달의 상태와 핸들러를 관리
 */
export const useModalState = () => {
  const [editingItem, setEditingItem] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [addingItem, setAddingItem] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // 편집 모달 열기
  const openEditModal = (item, type) => {
    setEditingItem({ ...item, type });
    setIsModalOpen(true);
  };

  // 편집 모달 닫기
  const closeEditModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
  };

  // 추가 모달 열기
  const openAddModal = (parentItem, type) => {
    setAddingItem({ parentItem, type });
    setIsAddModalOpen(true);
  };

  // 추가 모달 닫기
  const closeAddModal = () => {
    setIsAddModalOpen(false);
    setAddingItem(null);
  };

  return {
    // 상태
    editingItem,
    isModalOpen,
    addingItem,
    isAddModalOpen,
    
    // 편집 모달 핸들러
    openEditModal,
    closeEditModal,
    
    // 추가 모달 핸들러
    openAddModal,
    closeAddModal
  };
};
