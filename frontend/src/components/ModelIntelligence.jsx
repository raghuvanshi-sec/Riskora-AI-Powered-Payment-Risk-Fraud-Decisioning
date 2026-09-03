import { useState } from 'react';
import { getMlExplain } from '../services/riskService';

const STEPS = [
  { id: 1, label: 'Extracting features', duration: 400 },
  { id: 2, label: 'Running XGBoost', duration: 600 },
  { id: 3, label: 'Generating explanation', duration: 800 },
  { id: 4, label: 'Calculating hybrid score', duration: 400 },
  { id: 5, label: 'Decision generated', duration: 200 },
];

function InferenceAnimation({ isRunning, currentStep }) {
  if (!isRunning && currentStep === 0) return null;

  return (
    <div style={{
      padding: '16px',
      background: 'rgba(59, 130, 246, 0.08)',
      borderRadius: '8px',
      marginBottom: '16px',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {STEPS.map((step, idx) => {
          const isComplete = currentStep > step.id;
          const isActive = currentStep === step.id;
          return (
            <div key={step.id} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              opacity: isComplete || isActive ? 1 : 0.4,
            }}>
              <div style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: isComplete ? 'var(--color-success)' : isActive ? 'var(--accent)' : 'var(--bg-tertiary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                color: '#fff',
                fontWeight: 600,
              }}>
                {isComplete ? '✓' : step.id}
              </div>
              <span style={{
                fontSize: '13px',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
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

  const maxAbs = Math.max(...shapFactors.map(f => Math.abs(f.contribution)));

  return (
    <div style={{ marginTop: '16px' }}>
      <h4 style={{
        fontSize: '13px',
        fontWeight: 600,
        marginBottom: '12px',
        color: 'var(--text-secondary)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}>
        SHAP Feature Attribution
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {shapFactors.slice(0, 6).map((factor, idx) => {
          const width = Math.abs(factor.contribution / maxAbs) * 100;
          const isPositive = factor.contribution > 0;
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                fontSize: '12px',
                fontFamily: 'monospace',
                color: 'var(--text-secondary)',
                width: '140px',
                flexShrink: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                {factor.feature_name}
              </span>
              <div style={{
                flex: 1,
                height: '20px',
                background: 'var(--bg-tertiary)',
                borderRadius: '4px',
                overflow: 'hidden',
                position: 'relative',
              }}>
                <div style={{
                  position: 'absolute',
                  [isPositive ? 'left' : 'right']: '50%',
                  width: `${width}%`,
                  height: '100%',
                  background: isPositive ? 'rgba(239, 68, 68, 0.7)' : 'rgba(16, 185, 129, 0.7)',
                  borderRadius: '4px',
                  transition: 'width 0.3s ease',
                }} />
              </div>
              <span style={{
                fontSize: '11px',
                fontFamily: 'monospace',
                color: isPositive ? 'var(--color-danger)' : 'var(--color-success)',
                width: '50px',
                textAlign: 'right',
              }}>
                {isPositive ? '+' : ''}{factor.contribution.toFixed(3)}
              </span>
            </div>
          );
        })}
      </div>
      <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
        Red = increases fraud risk, Green = decreases fraud risk
      </p>
    </div>
  );
}

export default function ModelIntelligence({ transactionId, onRiskResult, riskResult }) {
  const [mlResult, setMlResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);

  const displayResult = mlResult || riskResult;

  const runAnalysis = async () => {
    setMlResult(null);
    setIsLoading(true);
    setError(null);
    setCurrentStep(1);

    const stepTimers = [];
    for (let i = 1; i <= STEPS.length; i++) {
      stepTimers.push(setTimeout(() => setCurrentStep(i), STEPS[i - 1].duration));
    }

    try {
      const res = await getMlExplain(transactionId);
      clearTimeout(stepTimers[stepTimers.length - 1]);
      setCurrentStep(STEPS.length);
      const analysisResult = res.data;
      setMlResult(analysisResult);
      if (onRiskResult) {
        onRiskResult(analysisResult);
      }
      setTimeout(() => setCurrentStep(0), 500);
    } catch (err) {
      setError('Failed to run ML analysis');
      setCurrentStep(0);
    } finally {
      stepTimers.forEach(clearTimeout);
      setIsLoading(false);
    }
  };

  const getDecisionColor = (decision) => {
    if (decision === 'ALLOW') return 'var(--color-success)';
    if (decision === 'REVIEW') return 'var(--color-warning)';
    if (decision === 'BLOCK') return 'var(--color-danger)';
    return 'var(--text-secondary)';
  };

  return (
    <div className="card" style={{ marginTop: '24px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
      }}>
        <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-primary)' }}>
          Model Intelligence
        </h3>
        <button
          onClick={runAnalysis}
          disabled={isLoading}
          className="btn btn-primary"
          style={{ fontSize: '13px' }}
        >
          {isLoading ? 'Analyzing...' : 'Analyze with ML'}
        </button>
      </div>

      <InferenceAnimation isRunning={isLoading} currentStep={currentStep} />

      {error && (
        <div style={{
          padding: '12px',
          background: 'rgba(239, 68, 68, 0.1)',
          borderRadius: '6px',
          color: 'var(--color-danger)',
          fontSize: '13px',
          marginBottom: '16px',
        }}>
          {error}
        </div>
      )}

      {displayResult && (
        <div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px',
            marginBottom: '20px',
          }}>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Model Status
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-success)' }} />
                <span style={{ fontSize: '13px', color: 'var(--color-success)', fontWeight: 500 }}>ONLINE</span>
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Model
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
                {displayResult.ml_model_version || 'XGBoost Fraud Classifier'}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Inference
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {displayResult.inference_time_ms?.toFixed(2) || '0.00'} ms
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Features
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {displayResult.feature_count || displayResult.shap_factors?.length || 0}
              </div>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '12px',
            padding: '16px',
            background: 'var(--bg-tertiary)',
            borderRadius: '8px',
            marginBottom: '16px',
          }}>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Fraud Probability
              </div>
              <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--accent)' }}>
                {((displayResult.ml_probability || 0) * 100).toFixed(1)}%
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                ML Risk Score
              </div>
              <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                {displayResult.ml_score || 0}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Rule Score
              </div>
              <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                {displayResult.rules_score || 0}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Hybrid Score
              </div>
              <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--accent)' }}>
                {displayResult.final_score || 0}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Decision
              </div>
              <div style={{
                fontSize: '16px',
                fontWeight: 700,
                color: getDecisionColor(displayResult.final_decision),
              }}>
                {displayResult.final_decision || '—'}
              </div>
            </div>
          </div>

          <details style={{ marginTop: '16px' }}>
            <summary style={{
              cursor: 'pointer',
              fontSize: '13px',
              color: 'var(--accent)',
              fontWeight: 500,
            }}>
              View ML Inference Details
            </summary>
            <div style={{
              marginTop: '12px',
              padding: '12px',
              background: 'var(--bg-tertiary)',
              borderRadius: '6px',
              fontSize: '12px',
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div><span style={{ color: 'var(--text-muted)' }}>ML Level:</span> {displayResult.ml_level || '—'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>ML Decision:</span> {displayResult.ml_decision || '—'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Rules Level:</span> {displayResult.rules_level || '—'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Rules Decision:</span> {displayResult.rules_decision || '—'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Rules Engine:</span> {displayResult.rules_engine_version || '—'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>SHAP Available:</span> {displayResult.shap_available ? 'Yes' : 'No'}</div>
              </div>
            </div>
          </details>

          <SHAPVisualization shapFactors={displayResult.shap_factors} />

          {displayResult.explanation && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(59, 130, 246, 0.06)',
              border: '1px solid rgba(59, 130, 246, 0.2)',
              borderRadius: '6px',
              fontSize: '13px',
              color: 'var(--text-secondary)',
              lineHeight: 1.5,
            }}>
              {displayResult.explanation}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
