import { useState, useEffect, useMemo } from 'react';

const CONSOLE_LINES = [
  { label: 'TX_ID', value: 'TXN-8821', type: 'default' },
  { label: 'MERCHANT', value: 'M-4471', type: 'default' },
  { label: 'RISK_SCORE', value: '94/100', type: 'danger' },
  { label: 'SPIKE_DETECTED', value: 'ABNORMAL +312%', type: 'warn' },
  { label: 'EXPOSURE_EST', value: '₹48,200', type: 'warn' },
  { label: 'BASELINE', value: '₹4,200/hr', type: 'default' },
  { label: 'CURRENT', value: '₹17,600/hr', type: 'danger' },
  { label: 'CONFIDENCE', value: '0.88', type: 'default' },
  { label: 'RECOMMENDATION', value: 'TEMPORARY_RATE_LIMIT', type: 'success' },
  { label: 'STATUS', value: 'ANALYST_REVIEW', type: 'default' },
];

export default function ConsoleSection() {
  const [activeLine, setActiveLine] = useState(0);
  const lineCount = useMemo(() => CONSOLE_LINES.length, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveLine((prev) => (prev + 1) % lineCount);
    }, 800);
    return () => clearInterval(interval);
  }, [lineCount]);

  return (
    <section className="ld-section ld-section--alt" id="console">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Detection Console</div>
          <h2 className="ld-h2">Real-Time Fraud Spike Detection</h2>
          <p className="ld-lede">
            Illustrative demo scenario showing how Riskora identifies abnormal merchant fraud activity
            and quantifies potential exposure.
          </p>
        </div>

        <div className="ld-console">
          <div className="ld-console__header">
            <span className="ld-console__dot ld-console__dot--red" />
            <span className="ld-console__dot ld-console__dot--yellow" />
            <span className="ld-console__dot ld-console__dot--green" />
            <span className="ld-console__title">riskora_detector.sh</span>
          </div>

          <div className="ld-console__body">
            {CONSOLE_LINES.map((line, i) => (
              <div key={i} className="ld-console__line" style={{ opacity: i <= activeLine ? 1 : 0.4 }}>
                <span className="ld-console__prompt">{'>'}</span>
                <span className="ld-console__label">{line.label}:</span>
                <span className={`ld-console__value ld-console__value--${line.type}`}>
                  {line.value}
                </span>
                {i === activeLine && (
                  <span style={{ animation: 'blink 1s infinite' }}>_</span>
                )}
              </div>
            ))}

            <div style={{
              marginTop: '20px',
              padding: '12px 16px',
              background: 'rgba(249, 115, 22, 0.08)',
              border: '1px solid rgba(249, 115, 22, 0.2)',
              borderRadius: '8px',
              fontSize: '12px',
              color: 'var(--ld-text-2)',
              fontFamily: 'var(--font-mono)'
            }}>
              <span style={{ color: 'var(--ld-orange)', fontWeight: 600 }}>⚠ ALERT:</span>{' '}
              This is a demonstration scenario. Actual Riskora metrics are derived from real transaction analysis.
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </section>
  );
}
