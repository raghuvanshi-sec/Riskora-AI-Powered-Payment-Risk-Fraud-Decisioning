import api from "./api";

export const getReviewQueue = (params = {}) =>
  api.get("/cases/queue", { params });

export const getQueueStats = () =>
  api.get("/cases/stats");

export const listCases = (params = {}) =>
  api.get("/cases", { params });

export const getCase = (caseId) =>
  api.get(`/cases/${caseId}`);

export const createCase = (data) =>
  api.post("/cases", data);

export const updateCase = (caseId, data) =>
  api.patch(`/cases/${caseId}`, data);

export const assignCase = (caseId, analystId) =>
  api.post(`/cases/${caseId}/assign`, { assigned_analyst_id: analystId });

export const takeCaseAction = (caseId, data) =>
  api.post(`/cases/${caseId}/actions`, data);

export const getCaseActions = (caseId, params = {}) =>
  api.get(`/cases/${caseId}/actions`, { params });
