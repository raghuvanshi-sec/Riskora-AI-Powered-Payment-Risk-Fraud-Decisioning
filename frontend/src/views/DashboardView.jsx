import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSummary, listTransactions } from '../services/transactionService';
import { getRiskHealth, getRiskSummary } from '../services/riskService';
import { TableSkeleton } from '../components';

const fmtINR = (v) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v) || 0);

const levelBadge = (level) => level ? `badge badge-${level.toLowerCase()}` : 'badge badge-pending';

export default function DashboardView() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [engineHealth, setEngineHealth] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      getSummary().then((r) => r.data).catch(() => null),
      getRiskSummary().then((r) => r.data).catch(() => null),
      getRiskHealth().then((r) => r.data).catch(() => null),
      listTransactions({ page: 1, page_size: 5, sort_by: 'transaction_timestamp', sort_order: 'desc' })
        .then((r) => r.data.items || [])
        .catch(() => []),
    ]).then(([s, rs, eh, items]) => {
      if (!active) return;
      setSummary(s);
      setRiskSummary(rs);
      setEngineHealth(eh);
      setRecent(items);
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false };
  }, []);

  const total = summary?.total_transactions ?? 0;
  const totalAmount = summary?.total_amount ?? 0;
  const today = summary?.today_transactions ?? 0;
  const totalAssessed = riskSummary?.total_assessed ?? 0;
  const blocked = riskSummary?.blocked ?? 0;
  const review = riskSummary?.review ?? 0;
  const allowed = riskSummary?.allowed ?? 0;
  const engineActive = engineHealth?.model_loaded ?? false;

  return (
    <div className="dashboard-view">
      <div className="page-title-section">
        <h2 className="page-title">Risk Signals &amp; Metrics</h2>
        <p className="page-subtitle">Real-time risk scoring and payment fraud evaluation pipeline.</p>
      </div>

      <div className="metrics-grid">
        <div className="card metric-card">
          <span className="metric-label">Total Transactions</span>
          <span className="metric-val">{loading ? '—' : total.toLocaleString()}</span>
          <span className="metric-trend trend-down">{today > 0 ? `↓ ${today} today` : '↓ —'}</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Total Amount</span>
          <span className="metric-val">{loading ? '—' : fmtINR(totalAmount)}</span>
          <span className="metric-trend">cumulative volume</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Assessed</span>
          <span className="metric-val" style={{ color: 'var(--brand)' }}>{loading ? '—' : totalAssessed.toLocaleString()}</span>
          <span className="metric-trend">risk evaluated</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Risk Engine</span>
          <span className="metric-val" style={{ color: engineActive ? 'var(--color-success)' : 'var(--text-muted)', fontSize: '22px' }}>
            {loading ? '—' : (engineActive ? 'Active' : 'Inactive')}
          </span>
          <span className="metric-trend">XGBoost v1 scoring</span>
        </div>
      </div>

      {totalAssessed > 0 && (
        <div className="metrics-grid" style={{ marginTop: '16px' }}>
          <div className="card metric-card">
            <span className="metric-label">Allowed</span>
            <span className="metric-val" style={{ color: 'var(--color-success)' }}>{allowed.toLocaleString()}</span>
            <span className="metric-trend trend-up">auto-approved</span>
          </div>
          <div className="card metric-card">
            <span className="metric-label">Review Queue</span>
            <span className="metric-val" style={{ color: 'var(--color-warning)' }}>{review.toLocaleString()}</span>
            <span className="metric-trend">pending analysis</span>
          </div>
          <div className="card metric-card">
            <span className="metric-label">Blocked</span>
            <span className="metric-val" style={{ color: 'var(--color-danger)' }}>{blocked.toLocaleString()}</span>
            <span className="metric-trend trend-down">high risk</span>
          </div>
          <div className="card metric-card">
            <span className="metric-label">High Risk Rate</span>
            <span className="metric-val" style={{ color: 'var(--color-danger)' }}>
              {loading ? '—' : totalAssessed > 0 ? `${((blocked / totalAssessed) * 100).toFixed(1)}%` : '0%'}
            </span>
            <span className="metric-trend">blocked transactions</span>
          </div>
        </div>
      )}

      <div className="page-title-section" style={{ marginTop: '40px' }}>
        <h2 className="page-title" style={{ fontSize: '20px' }}>Recent Transactions</h2>
      </div>

      {loading ? (
        <TableSkeleton rows={5} cols={8} />
      ) : recent.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No transactions yet.
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>User</th>
                <th>Merchant</th>
                <th>Amount</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Decision</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((tx) => (
                <tr key={tx.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/transactions/${tx.id}`)}>
                  <td className="font-mono" style={{ color: 'var(--accent)' }}>{tx.transaction_reference}</td>
                  <td>{tx.user?.name || '—'}</td>
                  <td>{tx.merchant?.name || '—'}</td>
                  <td className="font-mono">{fmtINR(tx.amount)}</td>
                  <td className="font-mono">{tx.risk_score != null ? tx.risk_score : '—'}</td>
                  <td>
                    <span className={levelBadge(tx.risk_level)}>
                      {tx.risk_level || 'Pending Analysis'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${(tx.decision || 'pending').toLowerCase()}`}>
                      {tx.decision || 'Pending Analysis'}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                    {new Date(tx.transaction_timestamp).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
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
