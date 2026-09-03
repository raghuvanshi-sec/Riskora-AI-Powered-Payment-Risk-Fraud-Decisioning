import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllRiskEvents } from '../services/riskService';
import { getReviewQueue } from '../services/riskOpsService';
import { EmptyState, ErrorState, TableSkeleton } from '../components';

const severityClass = (sev) => {
  if (sev === 'CRITICAL') return 'badge badge-high';
  if (sev === 'WARNING') return 'badge badge-medium';
  return 'badge badge-low';
};

const fmtDateTime = (v) => v ? new Date(v).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : '—';

export default function AlertsView() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    Promise.all([
      getAllRiskEvents({ limit: 50 }),
      getReviewQueue({ page: 1, page_size: 20 }),
    ])
      .then(([evRes, caseRes]) => {
        if (!active) return;
        setEvents(evRes.data || []);
        setCases(caseRes.data?.items || []);
      })
      .catch((err) => {
        if (!active) return;
        setError(err?.response?.status === 401
          ? 'Session expired. Please sign in again.'
          : 'Unable to load alerts.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false };
  }, []);

  if (loading) return <TableSkeleton rows={6} cols={4} />;

  if (error) {
    return (
      <div className="alerts-view">
        <div className="page-title-section">
          <h2 className="page-title">Audit Log &amp; System Alerts</h2>
          <p className="page-subtitle">Critical updates, rules modifications, and high-frequency threat alerts.</p>
        </div>
        <ErrorState message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  return (
    <div className="alerts-view">
      <div className="page-title-section">
        <h2 className="page-title">Audit Log &amp; System Alerts</h2>
        <p className="page-subtitle">Critical updates, rules modifications, and high-frequency threat alerts.</p>
      </div>

      {events.length === 0 && cases.length === 0 ? (
        <EmptyState
          title="No alerts recorded"
          description="Risk events will appear here when transactions trigger risk rules."
        />
      ) : (
        <>
          {cases.length > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Cases Requiring Attention
              </h3>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Case</th>
                      <th>Transaction</th>
                      <th>Risk Score</th>
                      <th>Decision</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cases.map((c) => (
                      <tr key={`case-${c.id}`} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/transactions/${c.transaction_id}`)}>
                        <td className="font-mono" style={{ color: 'var(--accent)' }}>#{c.id}</td>
                        <td className="font-mono">TX-{String(c.transaction_id).padStart(4, '0')}</td>
                        <td className="font-mono" style={{ fontWeight: 'bold' }}>{c.risk_score}</td>
                        <td><span className={`badge ${c.decision === 'BLOCK' ? 'badge-high' : 'badge-medium'}`}>{c.decision}</span></td>
                        <td>
                          <span className={`badge ${c.priority === 'CRITICAL' ? 'badge-high' : c.priority === 'HIGH' ? 'badge-medium' : 'badge-low'}`}>
                            {c.priority}
                          </span>
                        </td>
                        <td><span className="badge badge-medium">{c.status.replace('_', ' ')}</span></td>
                        <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{fmtDateTime(c.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {events.length > 0 && (
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Risk Events
              </h3>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Event</th>
                      <th>Transaction</th>
                      <th>Description</th>
                      <th>Severity</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.map((ev) => (
                      <tr key={ev.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/transactions/${ev.transaction_id}`)}>
                        <td className="font-mono" style={{ color: 'var(--accent)' }}>{ev.event_type}</td>
                        <td className="font-mono">TX-{String(ev.transaction_id).padStart(4, '0')}</td>
                        <td style={{ color: 'var(--text-secondary)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {ev.description || '—'}
                        </td>
                        <td><span className={severityClass(ev.severity)}>{ev.severity}</span></td>
                        <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{fmtDateTime(ev.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
