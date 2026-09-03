import api from "./api";

export const getTransactionRisk = (transactionId) =>
  api.get(`/risk/transactions/${transactionId}`);

export const getRiskHistory = (transactionId, limit = 10) =>
  api.get(`/risk/transactions/${transactionId}/history`, { params: { limit } });

export const getRiskEvents = (transactionId, params = {}) =>
  api.get(`/risk/transactions/${transactionId}/events`, { params });

export const getAllRiskEvents = (params = {}) =>
  api.get(`/risk/events`, { params });

export const getRiskSummary = () => api.get("/risk/summary");

export const getRiskHealth = () => api.get("/risk/health");
