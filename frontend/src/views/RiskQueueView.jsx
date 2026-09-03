import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReviewQueue, getQueueStats } from '../services/riskOpsService';
import { EmptyState, ErrorState, TableSkeleton } from '../components';

const badgeClass = (level) => {
  if (level === 'HIGH') return 'badge badge-high';
  if (level === 'MEDIUM') return 'badge badge-medium';
  if (level === 'LOW') return 'badge badge-low';
  return 'badge';
};

export default function RiskQueueView() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    Promise.all([
      getReviewQueue({ page: 1, page_size: 100 }),
      getQueueStats(),
    ])
      .then(([queueRes, statsRes]) => {
        if (!active) return;
        setItems(queueRes.data?.items || []);
        setStats(statsRes.data || {});
      })
      .catch((err) => {
        if (!active) return;
        setError(err?.response?.status === 401
          ? 'Session expired. Please sign in again.'
          : 'Unable to load review queue.');
      })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false };
  }, []);

  if (loading) return <TableSkeleton rows={6} cols={7} />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const totalOpen = (stats.open || 0) + (stats.in_progress || 0);

  return (
    <div className="risk-queue-view">
      <div className="page-title-section">
        <h2 className="page-title">Review Queue</h2>
        <p className="page-subtitle">
          {totalOpen} case(s) requiring analyst attention
          {stats.critical ? ` · ${stats.critical} critical` : ''}
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState title="Review queue empty" description="No cases currently require analyst review." />
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Transaction</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Decision</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id}>
                  <td className="font-mono" style={{ color: 'var(--accent)' }}>#{c.id}</td>
                  <td className="font-mono">TX-{String(c.transaction_id).padStart(4, '0')}</td>
                  <td className="font-mono" style={{ fontWeight: 'bold' }}>{c.risk_score}</td>
                  <td><span className={badgeClass(c.risk_level)}>{c.risk_level}</span></td>
                  <td><span className={`badge ${c.decision === 'BLOCK' ? 'badge-high' : 'badge-medium'}`}>{c.decision}</span></td>
                  <td>
                    <span className={`badge ${c.status === 'OPEN' ? 'badge-medium' : c.status === 'IN_PROGRESS' ? 'badge-low' : 'badge'}`}>
                      {c.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <button type="button" className="btn" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => navigate(`/app/transactions/${c.transaction_id}`)}>
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
