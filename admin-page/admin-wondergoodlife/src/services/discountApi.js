import { batchApi } from './api';

/**
 * 할인 정책 API 서비스
 */

// ===== 할인 정책 기본 CRUD =====
export const getDiscountPolicies = async (params = {}) => {
  const response = await batchApi.get('/discount/policies/', { params });
  return response.data;
};

export const getDiscountPolicy = async (policyId) => {
  const response = await batchApi.get(`/discount/policies/${policyId}`);
  return response.data;
};

export const createDiscountPolicy = async (policyData) => {
  const response = await batchApi.post('/discount/policies/', policyData);
  return response.data;
};

export const updateDiscountPolicy = async (policyId, policyData) => {
  const response = await batchApi.put(`/discount/policies/${policyId}`, policyData);
  return response.data;
};

export const deleteDiscountPolicy = async (policyId) => {
  const response = await batchApi.delete(`/discount/policies/${policyId}`);
  return response.data;
};

export const getDiscountPolicyDetails = async (policyId) => {
  const response = await batchApi.get(`/discount/policies/${policyId}/details`);
  return response.data;
};

export const getVersionDiscountSummary = async (versionId) => {
  const response = await batchApi.get(`/discount/versions/${versionId}/summary`);
  return response.data;
};

// ===== 카드사 제휴 CRUD =====
export const getCardBenefits = async (params = {}) => {
  const response = await batchApi.get('/discount/card-benefits/', { params });
  return response.data;
};

export const getCardBenefit = async (benefitId) => {
  const response = await batchApi.get(`/discount/card-benefits/${benefitId}`);
  return response.data;
};

export const createCardBenefit = async (benefitData) => {
  const response = await batchApi.post('/discount/card-benefits/', benefitData);
  return response.data;
};

export const updateCardBenefit = async (benefitId, benefitData) => {
  const response = await batchApi.put(`/discount/card-benefits/${benefitId}`, benefitData);
  return response.data;
};

export const deleteCardBenefit = async (benefitId) => {
  const response = await batchApi.delete(`/discount/card-benefits/${benefitId}`);
  return response.data;
};

export const createCardBenefitsBulk = async (benefitsData) => {
  const response = await batchApi.post('/discount/card-benefits/bulk', benefitsData);
  return response.data;
};

// ===== 브랜드 프로모션 CRUD =====
export const getPromos = async (params = {}) => {
  const response = await batchApi.get('/discount/promos/', { params });
  return response.data;
};

export const getPromo = async (promoId) => {
  const response = await batchApi.get(`/discount/promos/${promoId}`);
  return response.data;
};

export const createPromo = async (promoData) => {
  const response = await batchApi.post('/discount/promos/', promoData);
  return response.data;
};

export const updatePromo = async (promoId, promoData) => {
  const response = await batchApi.put(`/discount/promos/${promoId}`, promoData);
  return response.data;
};

export const deletePromo = async (promoId) => {
  const response = await batchApi.delete(`/discount/promos/${promoId}`);
  return response.data;
};

export const createPromosBulk = async (promosData) => {
  const response = await batchApi.post('/discount/promos/bulk', promosData);
  return response.data;
};

// ===== 재고 할인 CRUD =====
export const getInventoryDiscounts = async (params = {}) => {
  const response = await batchApi.get('/discount/inventory-discounts/', { params });
  return response.data;
};

export const getInventoryDiscount = async (discountId) => {
  const response = await batchApi.get(`/discount/inventory-discounts/${discountId}`);
  return response.data;
};

export const createInventoryDiscount = async (discountData) => {
  const response = await batchApi.post('/discount/inventory-discounts/', discountData);
  return response.data;
};

export const updateInventoryDiscount = async (discountId, discountData) => {
  const response = await batchApi.put(`/discount/inventory-discounts/${discountId}`, discountData);
  return response.data;
};

export const deleteInventoryDiscount = async (discountId) => {
  const response = await batchApi.delete(`/discount/inventory-discounts/${discountId}`);
  return response.data;
};

export const createInventoryDiscountsBulk = async (discountsData) => {
  const response = await batchApi.post('/discount/inventory-discounts/bulk', discountsData);
  return response.data;
};

// ===== 선구매 할인 CRUD =====
export const getPrePurchases = async (params = {}) => {
  const response = await batchApi.get('/discount/pre-purchases/', { params });
  return response.data;
};

export const getPrePurchase = async (prePurchaseId) => {
  const response = await batchApi.get(`/discount/pre-purchases/${prePurchaseId}`);
  return response.data;
};

export const createPrePurchase = async (prePurchaseData) => {
  const response = await batchApi.post('/discount/pre-purchases/', prePurchaseData);
  return response.data;
};

export const updatePrePurchase = async (prePurchaseId, prePurchaseData) => {
  const response = await batchApi.put(`/discount/pre-purchases/${prePurchaseId}`, prePurchaseData);
  return response.data;
};

export const deletePrePurchase = async (prePurchaseId) => {
  const response = await batchApi.delete(`/discount/pre-purchases/${prePurchaseId}`);
  return response.data;
};

export const createPrePurchasesBulk = async (prePurchasesData) => {
  const response = await batchApi.post('/discount/pre-purchases/bulk', prePurchasesData);
  return response.data;
};

// ===== 통합 수정/삭제 API =====
export const updateDiscountPolicyWithDetails = async (policyId, policyData) => {
  const response = await batchApi.put(`/discount/policies/${policyId}/with-details`, policyData);
  return response.data;
};

export const deleteDiscountPolicyWithDetails = async (policyId) => {
  const response = await batchApi.delete(`/discount/policies/${policyId}/with-details`);
  return response.data;
};
