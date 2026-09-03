import { useState } from 'react';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const PRESETS = {
  safe: {
    label: 'Safe Transaction',
    amount: 2500,
    currency: 'INR',
    payment_method: 'card',
    merchant: 'Amazon India',
    transaction_type: 'purchase',
    account_age_days: 730,
    transactions_per_hour: 1,
    failed_attempts: 0,
    device_changed: false,
    location_changed: false,
    merchant_risk: 0.2,
  },
  suspicious: {
    label: 'Suspicious Transaction',
    amount: 15000,
    currency: 'INR',
    payment_method: 'card',
    merchant: 'Tech Deals Inc',
    transaction_type: 'purchase',
    account_age_days: 45,
    transactions_per_hour: 8,
    failed_attempts: 3,
    device_changed: true,
    location_changed: true,
    merchant_risk: 0.6,
  },
  highRisk: {
    label: 'High-Risk Transaction',
    amount: 75000,
    currency: 'INR',
    payment_method: 'card',
    merchant: 'Unknown Merchant',
    transaction_type: 'purchase',
    account_age_days: 7,
    transactions_per_hour: 15,
    failed_attempts: 5,
    device_changed: true,
    location_changed: true,
    merchant_risk: 0.9,
  },
};

const STEPS = [
  { id: 1, label: 'Extracting features', duration: 400 },
  { id: 2, label: 'Running XGBoost', duration: 600 },
  { id: 3, label: 'Generating SHAP explanation', duration: 800 },
  { id: 4, label: 'Calculating hybrid score', duration: 400 },
  { id: 5, label: 'Decision generated', duration: 200 },
];

function InferenceAnimation({ currentStep, success }) {
  if (currentStep === 0 && !success) return null;

  return (
    <div style={{
      padding: '20px',
      background: 'rgba(59, 130, 246, 0.08)',
      borderRadius: '12px',
      marginTop: '20px',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {STEPS.map((step) => {
          const isComplete = currentStep > step.id || success;
          const isActive = currentStep === step.id && !success;
          return (
            <div key={step.id} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              opacity: isComplete || isActive ? 1 : 0.4,
            }}>
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                background: isComplete ? '#22C55E' : isActive ? '#3B82F6' : '#1E293B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                color: '#fff',
                fontWeight: 600,
              }}>
                {isComplete ? '✓' : step.id}
              </div>
              <span style={{
                fontSize: '14px',
                color: isActive ? '#F8FAFC' : isComplete ? '#94A3B8' : '#64748B',
                fontWeight: isActive ? 500 : 400,
              }}>
                {step.label}
                {isActive && <span style={{ animation: 'blink 1s infinite' }}>...</span>}
              </span>
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}

function SHAPVisualization({ shapFactors }) {
  if (!shapFactors || shapFactors.length === 0) return null;

  const maxAbs = Math.max(...shapFactors.map((f) => Math.abs(f.contribution)));

  return (
    <div style={{ marginTop: '20px' }}>
      <h4 style={{
        fontSize: '13px',
        fontWeight: 600,
        marginBottom: '16px',
        color: '#94A3B8',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}>
        Top Risk Factors
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {shapFactors.slice(0, 5).map((factor, idx) => {
          const width = Math.abs(factor.contribution / maxAbs) * 100;
          const isPositive = factor.contribution > 0;
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                fontSize: '12px',
                fontFamily: 'monospace',
                color: '#64748B',
                width: '160px',
                flexShrink: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                {factor.feature_name.replace(/_/g, ' ')}
              </span>
              <div style={{
                flex: 1,
                height: '24px',
                background: '#0B1728',
                borderRadius: '4px',
                overflow: 'hidden',
                position: 'relative',
              }}>
                <div style={{
                  position: 'absolute',
                  [isPositive ? 'left' : 'right']: '50%',
                  width: `${width}%`,
                  height: '100%',
                  background: isPositive ? 'rgba(239, 68, 68, 0.6)' : 'rgba(34, 197, 94, 0.6)',
                  borderRadius: '4px',
                }} />
              </div>
              <span style={{
                fontSize: '11px',
                fontFamily: 'monospace',
                color: isPositive ? '#EF4444' : '#22C55E',
                width: '55px',
                textAlign: 'right',
              }}>
                {isPositive ? '+' : ''}{factor.contribution.toFixed(3)}
              </span>
            </div>
          );
        })}
      </div>
      <p style={{ fontSize: '11px', color: '#64748B', marginTop: '12px' }}>
        Red = increases fraud risk, Green = decreases fraud risk
      </p>
    </div>
  );
}

function ResultPanel({ result, shapFactors }) {
  const getDecisionColor = (decision) => {
    if (decision === 'ALLOW') return '#22C55E';
    if (decision === 'REVIEW') return '#F59E0B';
    if (decision === 'BLOCK') return '#EF4444';
    return '#94A3B8';
  };

  const getRiskColor = (level) => {
    if (level === 'LOW') return '#22C55E';
    if (level === 'MEDIUM') return '#F59E0B';
    if (level === 'HIGH') return '#EF4444';
    return '#94A3B8';
  };

  return (
    <div style={{
      marginTop: '24px',
      padding: '24px',
      background: '#101D2E',
      border: '1px solid rgba(148, 163, 184, 0.12)',
      borderRadius: '16px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
      }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#F8FAFC' }}>
          Risk Decision
        </h3>
        <span style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: '#22C55E',
          fontWeight: 500,
        }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E' }} />
          ML ONLINE
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '16px',
        marginBottom: '24px',
      }}>
        <div style={{
          padding: '16px',
          background: '#0B1728',
          borderRadius: '10px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '6px', textTransform: 'uppercase' }}>
            Risk Score
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#F8FAFC', fontFamily: 'monospace' }}>
            {result.final_score}
            <span style={{ fontSize: '16px', color: '#64748B' }}>/100</span>
          </div>
        </div>

        <div style={{
          padding: '16px',
          background: '#0B1728',
          borderRadius: '10px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '6px', textTransform: 'uppercase' }}>
            Risk Level
          </div>
          <div style={{
            fontSize: '20px',
            fontWeight: 700,
            color: getRiskColor(result.final_level),
          }}>
            {result.final_level}
          </div>
        </div>

        <div style={{
          padding: '16px',
          background: '#0B1728',
          borderRadius: '10px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '6px', textTransform: 'uppercase' }}>
            Decision
          </div>
          <div style={{
            fontSize: '20px',
            fontWeight: 700,
            color: getDecisionColor(result.final_decision),
          }}>
            {result.final_decision}
          </div>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
        gap: '12px',
        padding: '16px',
        background: '#0B1728',
        borderRadius: '10px',
        marginBottom: '20px',
      }}>
        <div>
          <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px', textTransform: 'uppercase' }}>
            Fraud Probability
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#3B82F6', fontFamily: 'monospace' }}>
            {((result.ml_probability || 0) * 100).toFixed(1)}%
          </div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px', textTransform: 'uppercase' }}>
            ML Risk Score
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', fontFamily: 'monospace' }}>
            {result.ml_score || 0}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px', textTransform: 'uppercase' }}>
            Rule Score
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', fontFamily: 'monospace' }}>
            {result.rules_score || 0}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px', textTransform: 'uppercase' }}>
            Inference
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#22D3EE', fontFamily: 'monospace' }}>
            {result.inference_time_ms?.toFixed(2) || '0.00'} ms
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginBottom: '16px',
      }}>
        {[
          { label: 'XGBoost inference completed', done: true },
          { label: 'Feature extraction completed', done: true },
          { label: 'SHAP explanation generated', done: result.shap_available },
          { label: 'Hybrid score calculated', done: true },
        ].map((badge, i) => (
          <span key={i} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            background: badge.done ? 'rgba(34, 197, 94, 0.1)' : 'rgba(148, 163, 184, 0.1)',
            borderRadius: '20px',
            fontSize: '12px',
            color: badge.done ? '#22C55E' : '#64748B',
          }}>
            {badge.done ? '✓' : '○'} {badge.label}
          </span>
        ))}
      </div>

      <SHAPVisualization shapFactors={shapFactors} />

      {result.explanation && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: 'rgba(59, 130, 246, 0.06)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '10px',
          fontSize: '13px',
          color: '#94A3B8',
          lineHeight: 1.6,
        }}>
          <strong style={{ color: '#F8FAFC' }}>Why this decision?</strong><br />
          {result.explanation}
        </div>
      )}
    </div>
  );
}

export default function RiskDecisionSimulator() {
  const [form, setForm] = useState({
    amount: 5000,
    currency: 'INR',
    payment_method: 'card',
    merchant: '',
    transaction_type: 'purchase',
    account_age_days: 180,
    transactions_per_hour: 2,
    failed_attempts: 0,
    device_changed: false,
    location_changed: false,
    merchant_risk: 0.3,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const applyPreset = (presetKey) => {
    const preset = PRESETS[presetKey];
    setForm({ ...form, ...preset });
    setResult(null);
    setError(null);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setCurrentStep(1);

    const stepTimers = [];
    for (let i = 1; i <= STEPS.length; i++) {
      stepTimers.push(setTimeout(() => setCurrentStep(i), STEPS[i - 1].duration));
    }

    try {
      const response = await fetch(`${API_URL}/risk/simulator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      clearTimeout(stepTimers[stepTimers.length - 1]);
      setCurrentStep(STEPS.length);
      setResult(data);
      setTimeout(() => setCurrentStep(0), 500);
    } catch (err) {
      setError('Failed to analyze transaction. Please try again.');
      setCurrentStep(0);
      stepTimers.forEach(clearTimeout);
    } finally {
      setIsLoading(false);
    }
  };

  const updateField = (field, value) => {
    setForm({ ...form, [field]: value });
    setResult(null);
  };

  return (
    <section id="simulator" style={{
      padding: '96px 0',
      background: '#07111F',
    }}>
      <div className="ld-container">
        <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 48px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.12em',
            color: '#22D3EE',
            textTransform: 'uppercase',
            marginBottom: '16px',
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E' }} />
            ML ONLINE
          </div>
          <h2 style={{
            fontSize: 'clamp(32px, 4vw, 44px)',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: '#F8FAFC',
            marginBottom: '16px',
            lineHeight: 1.15,
          }}>
            Risk Decision Simulator
          </h2>
          <p style={{ fontSize: '17px', lineHeight: 1.7, color: '#94A3B8' }}>
            Submit a transaction and see Riskora's risk decision in real time.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          maxWidth: '1100px',
          margin: '0 auto',
        }}>
          <div style={{
            padding: '28px',
            background: '#101D2E',
            border: '1px solid rgba(148, 163, 184, 0.12)',
            borderRadius: '16px',
          }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#F8FAFC', marginBottom: '4px' }}>
                Quick Presets
              </h3>
              <p style={{ fontSize: '12px', color: '#64748B' }}>
                Try these example transactions
              </p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {Object.entries(PRESETS).map(([key, preset]) => (
                <button
                  key={key}
                  onClick={() => applyPreset(key)}
                  style={{
                    padding: '12px 16px',
                    background: key === 'safe' ? 'rgba(34, 197, 94, 0.1)' :
                               key === 'suspicious' ? 'rgba(245, 158, 11, 0.1)' :
                               'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${key === 'safe' ? 'rgba(34, 197, 94, 0.3)' :
                                    key === 'suspicious' ? 'rgba(245, 158, 11, 0.3)' :
                                    'rgba(239, 68, 68, 0.3)'}`,
                    borderRadius: '10px',
                    color: key === 'safe' ? '#22C55E' :
                          key === 'suspicious' ? '#F59E0B' :
                          '#EF4444',
                    fontSize: '13px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                  }}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{
            padding: '28px',
            background: '#101D2E',
            border: '1px solid rgba(148, 163, 184, 0.12)',
            borderRadius: '16px',
          }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#F8FAFC', marginBottom: '20px' }}>
              Transaction Details
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Amount
                </label>
                <input
                  type="number"
                  value={form.amount}
                  onChange={(e) => updateField('amount', parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Currency
                </label>
                <select
                  value={form.currency}
                  onChange={(e) => updateField('currency', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                  }}
                >
                  <option value="INR">INR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Payment Method
                </label>
                <select
                  value={form.payment_method}
                  onChange={(e) => updateField('payment_method', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                  }}
                >
                  <option value="card">Card</option>
                  <option value="upi">UPI</option>
                  <option value="netbanking">Net Banking</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Merchant
                </label>
                <input
                  type="text"
                  value={form.merchant}
                  onChange={(e) => updateField('merchant', e.target.value)}
                  placeholder="Merchant name"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Account Age (days)
                </label>
                <input
                  type="number"
                  value={form.account_age_days}
                  onChange={(e) => updateField('account_age_days', parseInt(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Transactions/Hour
                </label>
                <input
                  type="number"
                  value={form.transactions_per_hour}
                  onChange={(e) => updateField('transactions_per_hour', parseInt(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Failed Attempts
                </label>
                <input
                  type="number"
                  value={form.failed_attempts}
                  onChange={(e) => updateField('failed_attempts', parseInt(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#0B1728',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Merchant Risk Score
                </label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={form.merchant_risk}
                    onChange={(e) => updateField('merchant_risk', parseFloat(e.target.value))}
                    style={{
                      flex: 1,
                      accentColor: '#3B82F6',
                    }}
                  />
                  <span style={{
                    fontSize: '14px',
                    fontFamily: 'monospace',
                    color: form.merchant_risk > 0.6 ? '#EF4444' : form.merchant_risk > 0.3 ? '#F59E0B' : '#22C55E',
                    minWidth: '30px',
                  }}>
                    {form.merchant_risk.toFixed(1)}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={form.device_changed}
                    onChange={(e) => updateField('device_changed', e.target.checked)}
                    style={{ accentColor: '#3B82F6' }}
                  />
                  <span style={{ fontSize: '13px', color: '#94A3B8' }}>Device Changed</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={form.location_changed}
                    onChange={(e) => updateField('location_changed', e.target.checked)}
                    style={{ accentColor: '#3B82F6' }}
                  />
                  <span style={{ fontSize: '13px', color: '#94A3B8' }}>Location Changed</span>
                </label>
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={isLoading}
              style={{
                width: '100%',
                marginTop: '24px',
                padding: '14px 24px',
                background: isLoading ? '#1E40AF' : '#3B82F6',
                border: 'none',
                borderRadius: '10px',
                color: '#fff',
                fontSize: '15px',
                fontWeight: 600,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.15s',
              }}
            >
              {isLoading ? 'Analyzing...' : 'Analyze Transaction'}
              {!isLoading && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            marginTop: '24px',
            padding: '16px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '10px',
            color: '#EF4444',
            fontSize: '14px',
            textAlign: 'center',
            maxWidth: '1100px',
            margin: '24px auto 0',
          }}>
            {error}
          </div>
        )}

        <InferenceAnimation currentStep={currentStep} success={!!result} />

        {result && <ResultPanel result={result} shapFactors={result.shap_factors} />}
      </div>
    </section>
  );
}
