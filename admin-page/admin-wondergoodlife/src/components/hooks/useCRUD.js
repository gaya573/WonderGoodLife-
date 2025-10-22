import { useState, useCallback } from 'react';
import { stagingAPI } from '../../services/versionApi';

/**
 * CRUD 작업을 관리하는 훅
 */
export const useCRUD = () => {
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: null, // 'create', 'edit', 'delete'
    entityType: null, // 'brand', 'vehicleLine', 'model', 'trim', 'option'
    entityData: null,
    parentData: null
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 모달 열기
  const openModal = useCallback((mode, entityType, entityData = null, parentData = null) => {
    setModalState({
      isOpen: true,
      mode,
      entityType,
      entityData,
      parentData
    });
    setError(null);
  }, []);

  // 모달 닫기
  const closeModal = useCallback(() => {
    setModalState({
      isOpen: false,
      mode: null,
      entityType: null,
      entityData: null,
      parentData: null
    });
    setError(null);
  }, []);

  // CRUD 작업 실행
  const executeCRUD = useCallback(async (data, mode) => {
    const { entityType, entityData } = modalState;
    
    if (!entityType) {
      throw new Error('Entity type is required');
    }

    setLoading(true);
    setError(null);

    try {
      let result;
      const api = stagingAPI[entityType === 'vehicleLine' ? 'vehicleLines' : `${entityType}s`];

      switch (mode) {
        case 'create':
          result = await api.create(data);
          break;
        case 'edit':
          result = await api.update(entityData.id, data);
          break;
        case 'delete':
          result = await api.delete(entityData.id);
          break;
        default:
          throw new Error(`Unknown mode: ${mode}`);
      }

      return result;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || '작업 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [modalState]);

  // 편의 함수들
  const createBrand = useCallback((data, parentData) => {
    openModal('create', 'brand', null, parentData);
  }, [openModal]);

  const editBrand = useCallback((brandData) => {
    openModal('edit', 'brand', brandData);
  }, [openModal]);

  const deleteBrand = useCallback((brandData) => {
    openModal('delete', 'brand', brandData);
  }, [openModal]);

  const createVehicleLine = useCallback((data, parentData) => {
    openModal('create', 'vehicleLine', null, parentData);
  }, [openModal]);

  const editVehicleLine = useCallback((vehicleLineData) => {
    openModal('edit', 'vehicleLine', vehicleLineData);
  }, [openModal]);

  const deleteVehicleLine = useCallback((vehicleLineData) => {
    openModal('delete', 'vehicleLine', vehicleLineData);
  }, [openModal]);

  const createModel = useCallback((data, parentData) => {
    openModal('create', 'model', null, parentData);
  }, [openModal]);

  const editModel = useCallback((modelData) => {
    openModal('edit', 'model', modelData);
  }, [openModal]);

  const deleteModel = useCallback((modelData) => {
    openModal('delete', 'model', modelData);
  }, [openModal]);

  const createTrim = useCallback((data, parentData) => {
    openModal('create', 'trim', null, parentData);
  }, [openModal]);

  const editTrim = useCallback((trimData) => {
    openModal('edit', 'trim', trimData);
  }, [openModal]);

  const deleteTrim = useCallback((trimData) => {
    openModal('delete', 'trim', trimData);
  }, [openModal]);

  const createOption = useCallback((data, parentData) => {
    openModal('create', 'option', null, parentData);
  }, [openModal]);

  const editOption = useCallback((optionData) => {
    openModal('edit', 'option', optionData);
  }, [openModal]);

  const deleteOption = useCallback((optionData) => {
    openModal('delete', 'option', optionData);
  }, [openModal]);

  return {
    // 상태
    modalState,
    loading,
    error,
    
    // 모달 제어
    openModal,
    closeModal,
    
    // CRUD 실행
    executeCRUD,
    
    // 편의 함수들
    createBrand,
    editBrand,
    deleteBrand,
    createVehicleLine,
    editVehicleLine,
    deleteVehicleLine,
    createModel,
    editModel,
    deleteModel,
    createTrim,
    editTrim,
    deleteTrim,
    createOption,
    editOption,
    deleteOption
  };
};
