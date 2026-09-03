import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getTransaction } from '../services/transactionService';
import { getTransactionRisk, getRiskHistory, getRiskEvents } from '../services/riskService';
import { getCase, takeCaseAction } from '../services/riskOpsService';
import { EmptyState, ErrorState, DetailSkeleton } from '../components';
import ModelIntelligence from '../components/ModelIntelligence';

const fmtINR = (v) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const fmtDateTime = (v) => v ? new Date(v).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : '—';

const Field = ({ label, value }) => (
  <div className="detail-field">
    <span className="detail-label">{label}</span>
    <span className="detail-value">{value ?? '—'}</span>
  </div>
);

const ACTION_TYPES = ['ALLOW', 'BLOCK', 'ESCALATE', 'FLAG', 'DISMISS', 'ADD_NOTE'];

const severityColor = (sev) => {
  if (sev === 'CRITICAL') return 'var(--color-danger)';
  if (sev === 'WARNING') return 'var(--color-warning)';
  return 'var(--text-muted)';
};

export default function TransactionDetail() {
  const { transactionId } = useParams();
  const navigate = useNavigate();

  const [tx, setTx] = useState(null);
  const [riskCase, setRiskCase] = useState(null);
  const [risk, setRisk] = useState(null);
  const [riskHistory, setRiskHistory] = useState([]);
  const [riskEvents, setRiskEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionType, setActionType] = useState('ADD_NOTE');
  const [actionReason, setActionReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);

  const handleRiskResult = (mlResult) => {
    if (!mlResult) return;
    const unifiedRisk = {
      risk_score: mlResult.final_score,
      risk_level: mlResult.final_level,
      decision: mlResult.final_decision,
      ml_score: mlResult.ml_score,
      rule_score: mlResult.rules_score,
      ml_probability: mlResult.ml_probability,
      explanation: mlResult.explanation,
      shap_factors: mlResult.shap_factors,
      rules_factors: mlResult.rules_factors,
      triggered_rules: mlResult.rules_factors,
      top_positive_features: mlResult.shap_factors?.filter(f => f.contribution > 0) || [],
      top_negative_features: mlResult.shap_factors?.filter(f => f.contribution < 0) || [],
      inference_time_ms: mlResult.inference_time_ms,
      model_version: mlResult.ml_model_version,
      shap_available: mlResult.shap_available,
    };
    setRisk(unifiedRisk);

    if (process.env.NODE_ENV === 'development') {
      const assessmentScore = unifiedRisk.risk_score;
      const miScore = mlResult.final_score;
      if (assessmentScore !== miScore) {
        console.warn('[Riskora Consistency] Risk Assessment score !== Model Intelligence hybrid score:', assessmentScore, 'vs', miScore);
      }
      if (unifiedRisk.decision !== mlResult.final_decision) {
        console.warn('[Riskora Consistency] Risk Assessment decision !== Model Intelligence decision:', unifiedRisk.decision, 'vs', mlResult.final_decision);
      }
      if (unifiedRisk.risk_level !== mlResult.final_level) {
        console.warn('[Riskora Consistency] Risk Assessment level !== Model Intelligence level:', unifiedRisk.risk_level, 'vs', mlResult.final_level);
      }
    }
  };

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    getTransaction(transactionId)
      .then((res) => { if (active) setTx(res.data); })
      .catch((err) => {
        if (!active) return;
        const msg = err?.response?.status === 404 ? 'Transaction not found.' : 'Unable to load transaction.';
        setError(msg);
      })
      .finally(() => { if (active) setLoading(false); });

    getCase(transactionId)
      .then((res) => { if (active) setRiskCase(res.data); })
      .catch(() => {});

    getTransactionRisk(transactionId)
      .then((res) => { if (active) setRisk(res.data); })
      .catch(() => {});

    getRiskHistory(transactionId, 5)
      .then((res) => { if (active) setRiskHistory(res.data.assessments || []); })
      .catch(() => {});

    getRiskEvents(transactionId, { limit: 20 })
      .then((res) => { if (active) setRiskEvents(res.data.events || []); })
      .catch(() => {});

    return () => { active = false };
  }, [transactionId]);

  const handleAction = (e) => {
    e.preventDefault();
    if (!riskCase) return;
    setActionLoading(true);
    setActionMsg(null);

    takeCaseAction(riskCase.id, {
      action_type: actionType,
      reason: actionReason,
    })
      .then(() => {
        setActionMsg({ type: 'success', text: `Action "${actionType}" recorded successfully.` });
        setActionReason('');
        return getCase(transactionId);
      })
      .then((res) => setRiskCase(res.data))
      .catch((err) => {
        setActionMsg({ type: 'error', text: err?.response?.data?.detail || 'Failed to record action.' });
      })
      .finally(() => setActionLoading(false));
  };

  if (loading) return <DetailSkeleton />;

  if (error || !tx) {
    return (
      <div className="transactions-view">
        <div className="page-title-section">
          <h2 className="page-title">Transaction Detail</h2>
        </div>
        <ErrorState
          message={error || 'Transaction not found.'}
          onRetry={() => navigate('/app/transactions')}
        />
      </div>
    );
  }

  const hasRisk = risk != null || tx.risk_score != null || tx.risk_level != null || tx.decision != null;
  const riskScore = risk?.risk_score ?? tx.risk_score ?? 0;
  const riskLevel = risk?.risk_level ?? tx.risk_level ?? null;
  const decision = risk?.decision ?? tx.decision ?? null;
  const riskLevelBadge = riskLevel ? `badge badge-${riskLevel.toLowerCase()}` : 'badge badge-pending';
  const decisionBadge = decision ? `badge badge-${decision.toLowerCase()}` : 'badge badge-pending';

  const scoreColor = riskScore >= 70 ? 'var(--color-danger)' : riskScore >= 40 ? 'var(--color-warning)' : 'var(--color-success)';

  return (
    <div className="transactions-view">
      <div className="page-title-section">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <h2 className="page-title" style={{ margin: 0 }}>Transaction Detail</h2>
          <span className="font-mono" style={{ color: 'var(--accent)' }}>{tx.transaction_reference}</span>
        </div>
        <p className="page-subtitle">Investigation signals and risk assessment for this transaction.</p>
      </div>

      <div className="detail-layout">
        <section className="card detail-block">
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Transaction</h3>
          <div className="detail-grid">
            <Field label="Transaction ID" value={tx.transaction_reference} />
            <Field label="Amount" value={fmtINR(tx.amount)} />
            <Field label="Currency" value={tx.currency} />
            <Field label="Timestamp" value={fmtDateTime(tx.transaction_timestamp)} />
          </div>
        </section>

        <section className="card detail-block">
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Parties</h3>
          <div className="detail-grid">
            <Field label="User" value={tx.user?.name} />
            <Field label="User ID" value={tx.user?.id} />
            <Field label="Merchant" value={tx.merchant?.name} />
            <Field label="Merchant Category" value={tx.merchant?.category} />
          </div>
        </section>

        <section className="card detail-block">
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Transaction Signals</h3>
          <div className="signals-grid">
            <div className="signal-tile">
              <div className="signal-label">Device</div>
              <div className="signal-value">{tx.device_id || 'Unknown'}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Location</div>
              <div className="signal-value">{tx.location || 'Unknown'}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Velocity</div>
              <div className="signal-value">{tx.velocity ?? '—'}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Failed Attempts</div>
              <div className="signal-value">{tx.failed_attempts ?? '—'}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Account Age</div>
              <div className="signal-value">{tx.account_age_days != null ? `${tx.account_age_days} days` : '—'}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Device Change</div>
              <div className="signal-value">{tx.device_change == null ? 'Unknown' : (tx.device_change ? 'Yes' : 'No')}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Location Change</div>
              <div className="signal-value">{tx.location_change == null ? 'Unknown' : (tx.location_change ? 'Yes' : 'No')}</div>
            </div>
            <div className="signal-tile">
              <div className="signal-label">Merchant Risk</div>
              <div className="signal-value">{tx.merchant_risk != null ? tx.merchant_risk.toFixed(1) : '—'}</div>
            </div>
          </div>
        </section>

        <section className="card detail-block">
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Risk Assessment</h3>

          {!hasRisk ? (
            <EmptyState
              title="Risk assessment pending"
              description="This transaction has not been scored yet."
            />
          ) : (
            <div>
              <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Risk Score</div>
                  <div className="risk-gauge">
                    <span className="score" style={{ color: scoreColor }}>{riskScore}</span>
                    <span className="of">/ 100</span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Risk Level</div>
                  <span className={riskLevelBadge}>{riskLevel}</span>
                </div>
                <div>
                  <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Decision</div>
                  <span className={decisionBadge}>{decision}</span>
                </div>
              </div>

              <div className="risk-bar">
                <span
                  style={{
                    width: `${Math.min(100, Math.max(0, Number(riskScore) || 0))}%`,
                    background: scoreColor,
                  }}
                />
              </div>

              {risk && (
                <div style={{ marginTop: '16px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>ML Score</div>
                    <span className="font-mono" style={{ color: 'var(--accent)', fontSize: '15px' }}>
                      {risk.ml_score?.toFixed(1) ?? '—'}
                    </span>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>Rule Score</div>
                    <span className="font-mono" style={{ color: 'var(--accent)', fontSize: '15px' }}>
                      {risk.rule_score?.toFixed(1) ?? '—'}
                    </span>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>ML Probability</div>
                    <span className="font-mono" style={{ color: 'var(--accent)', fontSize: '15px' }}>
                      {risk.ml_probability != null ? `${(risk.ml_probability * 100).toFixed(1)}%` : '—'}
                    </span>
                  </div>
                </div>
              )}

              {risk && risk.explanation && (
                <p style={{ marginTop: '12px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {risk.explanation}
                </p>
              )}
            </div>
            )}
          </section>

        <ModelIntelligence transactionId={transactionId} onRiskResult={handleRiskResult} riskResult={risk} />

        {risk && (risk.triggered_rules?.length > 0 || risk.top_positive_features?.length > 0 || risk.top_negative_features?.length > 0) && (
          <section className="card detail-block">
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Risk Explanation</h3>

            {risk.triggered_rules?.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '10px', color: 'var(--text-secondary)' }}>
                  Triggered Rules ({risk.triggered_rules.length})
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {risk.triggered_rules.map((rule, i) => (
                    <div key={i} style={{
                      padding: '10px 12px',
                      borderRadius: '6px',
                      background: 'var(--bg-secondary)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                      fontSize: '13px',
                    }}>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: severityColor(rule.severity),
                        color: '#fff',
                        textTransform: 'uppercase',
                        flexShrink: 0,
                      }}>
                        {rule.severity}
                      </span>
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{rule.name}</span>
                        {rule.reason && (
                          <span style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '2px', fontSize: '12px' }}>
                            {rule.reason}
                          </span>
                        )}
                      </div>
                      <span className="font-mono" style={{ color: 'var(--text-muted)', fontSize: '12px', flexShrink: 0 }}>
                        +{rule.score_contribution}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {risk.top_positive_features?.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '10px', color: 'var(--color-danger)' }}>
                  Risk Increasing Factors
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {risk.top_positive_features.map((feat, i) => (
                    <span key={i} style={{
                      padding: '4px 10px',
                      borderRadius: '20px',
                      background: 'rgba(239, 68, 68, 0.1)',
                      color: 'var(--color-danger)',
                      fontSize: '12px',
                      fontFamily: 'monospace',
                    }}>
                      {feat.feature_name}: +{feat.shap_value?.toFixed(3)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {risk.top_negative_features?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '10px', color: 'var(--color-success)' }}>
                  Risk Decreasing Factors
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {risk.top_negative_features.map((feat, i) => (
                    <span key={i} style={{
                      padding: '4px 10px',
                      borderRadius: '20px',
                      background: 'rgba(16, 185, 129, 0.1)',
                      color: 'var(--color-success)',
                      fontSize: '12px',
                      fontFamily: 'monospace',
                    }}>
                      {feat.feature_name}: {feat.shap_value?.toFixed(3)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {riskHistory.length > 0 && (
          <section className="card detail-block">
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Risk History</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {riskHistory.map((h) => {
                const hc = h.risk_score >= 70 ? 'var(--color-danger)' : h.risk_score >= 40 ? 'var(--color-warning)' : 'var(--color-success)';
                return (
                  <div key={h.id} style={{
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: 'var(--bg-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    fontSize: '13px',
                  }}>
                    <span className="font-mono" style={{ color: hc, fontWeight: 600, minWidth: '36px' }}>
                      {h.risk_score}
                    </span>
                    <span className={`badge badge-${(h.risk_level || 'pending').toLowerCase()}`}>
                      {h.risk_level || '—'}
                    </span>
                    <span className={`badge badge-${(h.decision || 'pending').toLowerCase()}`}>
                      {h.decision || '—'}
                    </span>
                    {h.ml_probability != null && (
                      <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                        ML: {(h.ml_probability * 100).toFixed(1)}%
                      </span>
                    )}
                    <span style={{ color: 'var(--text-muted)', marginLeft: 'auto', fontSize: '12px' }}>
                      {fmtDateTime(h.created_at)}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {(riskEvents.length > 0 || (tx.risk_events && tx.risk_events.length > 0)) && (
          <section className="card detail-block">
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Risk Events</h3>
            {riskEvents.length === 0 && tx.risk_events?.length === 0 ? (
              <EmptyState title="No events" description="No risk events recorded yet." />
            ) : (
              <ul className="audit-list">
                {[...riskEvents, ...(tx.risk_events || [])].map((ev, idx) => (
                  <li key={`${ev.id}-${idx}`}>
                    <div>
                      <span className="audit-action" style={{ color: severityColor(ev.severity) }}>
                        {ev.event_type}
                      </span>
                      {ev.description && <span className="audit-meta" style={{ display: 'block' }}>{ev.description}</span>}
                    </div>
                    <span className="audit-meta">{fmtDateTime(ev.created_at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {riskCase && (
          <section className="card detail-block">
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text-primary)' }}>Case Management</h3>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '20px' }}>
              <div>
                <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Case ID</div>
                <span className="font-mono" style={{ color: 'var(--accent)' }}>#{riskCase.id}</span>
              </div>
              <div>
                <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Status</div>
                <span className={`badge ${riskCase.status === 'OPEN' ? 'badge-medium' : riskCase.status === 'IN_PROGRESS' ? 'badge-low' : 'badge'}`}>
                  {riskCase.status.replace('_', ' ')}
                </span>
              </div>
              <div>
                <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>Priority</div>
                <span className={`badge ${riskCase.priority === 'CRITICAL' ? 'badge-high' : riskCase.priority === 'HIGH' ? 'badge-medium' : 'badge-low'}`}>
                  {riskCase.priority}
                </span>
              </div>
            </div>

            <form onSubmit={handleAction} style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '480px' }}>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <select
                  value={actionType}
                  onChange={(e) => setActionType(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  {ACTION_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={actionLoading}
                  style={{ minWidth: '100px' }}
                >
                  {actionLoading ? 'Recording...' : 'Record Action'}
                </button>
              </div>
              <textarea
                value={actionReason}
                onChange={(e) => setActionReason(e.target.value)}
                placeholder="Reason or notes for this action..."
                rows={3}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  resize: 'vertical',
                  fontFamily: 'inherit',
                }}
              />
              {actionMsg && (
                <div style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  fontSize: '13px',
                  background: actionMsg.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  color: actionMsg.type === 'success' ? 'var(--color-success)' : 'var(--color-danger)',
                }}>
                  {actionMsg.text}
                </div>
              )}
            </form>

            {riskCase.analyst_actions && riskCase.analyst_actions.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-secondary)' }}>
                  Action History ({riskCase.analyst_actions.length})
                </h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {riskCase.analyst_actions.map((a) => (
                    <li key={a.id} style={{
                      padding: '10px 12px',
                      borderRadius: '6px',
                      background: 'var(--bg-secondary)',
                      fontSize: '13px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      gap: '12px',
                    }}>
                      <div>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{a.action_type}</span>
                        {a.reason && <span style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '2px' }}>{a.reason}</span>}
                        {a.new_status && <span style={{ display: 'block', color: 'var(--text-muted)', fontSize: '12px', marginTop: '2px' }}>Status → {a.new_status}</span>}
                      </div>
                      <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap', fontSize: '12px' }}>{fmtDateTime(a.created_at)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
