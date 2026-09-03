import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { listTransactions } from '../services/transactionService';
import { EmptyState, ErrorState, TableSkeleton } from '../components';

const RISK_LEVELS = ['LOW', 'MEDIUM', 'HIGH'];
const DECISIONS = ['ALLOW', 'REVIEW', 'BLOCK'];

const levelBadge = (level) => level ? `badge badge-${level.toLowerCase()}` : 'badge badge-pending';
const levelLabel = (level) => level || 'Pending Analysis';
const decisionBadge = (decision) => decision ? `badge badge-${decision.toLowerCase()}` : 'badge badge-pending';
const decisionLabel = (decision) => decision || 'Pending Analysis';

export default function TransactionsView() {
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);

  const [search, setSearch] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [decision, setDecision] = useState('');
  const [sortBy, setSortBy] = useState('transaction_timestamp');
  const [sortOrder, setSortOrder] = useState('desc');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listTransactions({
        page,
        page_size: pageSize,
        search: search || undefined,
        risk_level: riskLevel || undefined,
        decision: decision || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      const d = res.data;
      setItems(d.items || []);
      setTotal(d.total || 0);
      setPageSize(d.page_size || pageSize);
      setPage(d.page || 1);
      setTotalPages(d.total_pages || 1);
    } catch (err) {
      const msg = err?.response?.status === 401
        ? 'Your session expired. Please sign in again.'
        : 'Unable to load transactions. Please try again.';
      setError(msg);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, riskLevel, decision, sortBy, sortOrder]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const applyFilters = (fn) => (e) => {
    const v = e.target.value;
    fn(v);
    setPage(1);
  };

  const toggleSort = (field) => {
    setSortBy(field);
    setSortOrder((prev) => (sortBy === field && prev === 'desc' ? 'asc' : 'desc'));
    setPage(1);
  };

  const renderSkeleton = () => <TableSkeleton rows={6} cols={9} />;

  return (
    <div className="transactions-view">
      <div className="page-title-section">
        <h2 className="page-title">Transaction Ledger</h2>
        <p className="page-subtitle">Historical records of evaluated payments and threat signals.</p>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="toolbar">
          <div className="form-group" style={{ flex: 1, minWidth: '220px' }}>
            <label className="form-label" htmlFor="search-tx">Search</label>
            <input
              id="search-tx"
              className="form-input"
              type="text"
              placeholder="Search transaction ID, user, or merchant..."
              value={search}
              onChange={applyFilters(setSearch)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="risk-level">Risk Level</label>
            <select
              id="risk-level"
              className="form-input"
              value={riskLevel}
              onChange={applyFilters(setRiskLevel)}
            >
              <option value="">All levels</option>
              {RISK_LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="decision">Decision</label>
            <select
              id="decision"
              className="form-input"
              value={decision}
              onChange={applyFilters(setDecision)}
            >
              <option value="">All decisions</option>
              {DECISIONS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="page-size">Per page</label>
            <select
              id="page-size"
              className="form-input"
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
            >
              {[10, 20, 50, 100].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading && renderSkeleton()}

      {!loading && error && (
        <ErrorState message={error} onRetry={fetchTransactions} />
      )}

      {!loading && !error && items.length === 0 && (
        <EmptyState
          title="No transactions found"
          description="Try changing your filters or search query."
        />
      )}

      {!loading && !error && items.length > 0 && (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction</th>
                <th>User</th>
                <th>Merchant</th>
                <th>Amount</th>
                <th>Risk Score</th>
                <th>
                  <button type="button" className="sort-link" onClick={() => toggleSort('risk_level')}>
                    Risk Level {sortBy === 'risk_level' && (sortOrder === 'desc' ? '▾' : '▴')}
                  </button>
                </th>
                <th>Decision</th>
                <th>Time</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {items.map((tx) => (
                <tr key={tx.id}>
                  <td className="font-mono" style={{ color: 'var(--accent)' }}>{tx.transaction_reference}</td>
                  <td>{tx.user?.name || '—'}</td>
                  <td>{tx.merchant?.name || '—'}</td>
                  <td className="font-mono">
                    {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(tx.amount)}
                  </td>
                  <td className="font-mono">{tx.risk_score != null ? tx.risk_score : '—'}</td>
                  <td><span className={levelBadge(tx.risk_level)}>{levelLabel(tx.risk_level)}</span></td>
                  <td><span className={decisionBadge(tx.decision)}>{decisionLabel(tx.decision)}</span></td>
                  <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                    {new Date(tx.transaction_timestamp).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-outline"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                      onClick={() => navigate(`/app/transactions/${tx.id}`)}
                    >
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && total > 0 && (
        <div className="pagination">
          <span>Showing {items.length} of {total} transactions</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-outline page-btn"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >‹</button>
            <span style={{ display: 'inline-flex', alignItems: 'center', padding: '0 8px', fontSize: '13px' }}>
              Page {page} of {totalPages}
            </span>
            <button
              type="button"
              className="btn btn-outline page-btn"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >›</button>
          </div>
        </div>
      )}
    </div>
  );
}