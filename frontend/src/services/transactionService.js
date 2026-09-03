/** Thin wrapper around the shared Axios client (`services/api.js`).
 *
 * No Axios config is duplicated here — timeouts, base URL, and the
 * Authorization interceptor all live in api.js.
 */

import api from "./api";

/** GET /transactions with pagination, filtering, and sorting. */
export const listTransactions = (params = {}) =>
  api.get("/transactions", { params });

/** GET /transactions/recent */
export const getRecentTransactions = (limit = 5) =>
  api.get("/transactions/recent", { params: { limit } });

/** GET /transactions/summary */
export const getSummary = () => api.get("/transactions/summary");

/** GET /transactions/{transaction_id} */
export const getTransaction = (transactionId) =>
  api.get(`/transactions/${transactionId}`);

/** POST /transactions */
export const createTransaction = (payload) =>
  api.post("/transactions", payload);

/** PATCH /transactions/{transaction_id} */
export const updateTransaction = (transactionId, payload) =>
  api.patch(`/transactions/${transactionId}`, payload);