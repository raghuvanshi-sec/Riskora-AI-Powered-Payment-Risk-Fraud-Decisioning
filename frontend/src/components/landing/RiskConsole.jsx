import { useState, useEffect } from 'react';

export default function RiskConsole() {
  const [fraudRate, setFraudRate] = useState(1.8);
  const [exposure, setExposure] = useState(12400);
  const [spikeDetected, setSpikeDetected] = useState(false);
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const sequence = [
      { delay: 0, rate: 2.1, exp: 18400, spike: false },
      { delay: 1000, rate: 2.8, exp: 32000, spike: false },
      { delay: 2000, rate: 3.4, exp: 58000, spike: false },
      { delay: 3000, rate: 4.2, exp: 96000, spike: false },
      { delay: 4000, rate: 5.1, exp: 156000, spike: true },
      { delay: 5000, rate: 5.8, exp: 204000, spike: true },
      { delay: 6000, rate: 5.1, exp: 168000, spike: true },
      { delay: 7000, rate: 4.2, exp: 112000, spike: false },
      { delay: 8000, rate: 2.8, exp: 48000, spike: false },
      { delay: 9000, rate: 1.8, exp: 12400, spike: false },
    ];

    const timers = sequence.map(({ delay, rate, exp, spike }) =>
      setTimeout(() => {
        setFraudRate(rate);
        setExposure(exp);
        setSpikeDetected(spike);
      }, delay)
    );

    const cycleTimer = setTimeout(() => {
      setPhase(p => p + 1);
    }, 10000);

    return () => {
      timers.forEach(clearTimeout);
      clearTimeout(cycleTimer);
    };
  }, [phase]);

  const signals = [
    { label: 'Transaction Velocity', status: spikeDetected ? 'HIGH' : 'MEDIUM', statusClass: spikeDetected ? 'high' : 'medium' },
    { label: 'Fraud Probability', status: spikeDetected ? 'HIGH' : 'LOW', statusClass: spikeDetected ? 'high' : 'low' },
    { label: 'Merchant Deviation', status: spikeDetected ? 'HIGH' : 'LOW', statusClass: spikeDetected ? 'high' : 'low' },
    { label: 'Baseline Deviation', status: spikeDetected ? 'MEDIUM' : 'LOW', statusClass: spikeDetected ? 'medium' : 'low' },
  ];

  const chartPoints = [
    { x: 0, y: 30 }, { x: 10, y: 28 }, { x: 20, y: 32 }, { x: 30, y: 26 },
    { x: 40, y: 31 }, { x: 50, y: 29 }, { x: 60, y: 35 }, { x: 70, y: 42 },
    { x: 80, y: 58 }, { x: 85, y: 72 }, { x: 90, y: 85 }, { x: 95, y: 78 },
    { x: 100, y: 65 }, { x: 110, y: 48 }, { x: 120, y: 35 }, { x: 130, y: 30 },
  ];

  const baselineY = 32;
  const maxY = 90;
  const height = 80;
  const width = 320;

  const scaleY = (y) => height - ((y / maxY) * height);
  const scaleX = (x) => (x / 130) * width;

  const actualPath = chartPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.y)}`)
    .join(' ');

  const baselinePath = `M ${scaleX(0)} ${scaleY(baselineY)} L ${scaleX(130)} ${scaleY(baselineY)}`;

  return (
    <>
      <div className="ld-console__header">
        <span className="ld-console__title">Risk Intelligence</span>
        <div className="ld-console__status">
          <span className="ld-console__status-dot" />
          <span>Monitoring</span>
        </div>
      </div>

      <div className="ld-console__body">
        <div className="ld-console__section">
          <div className="ld-console__merchant">
            <div className="ld-console__merchant-info">
              <span className="ld-console__merchant-id">M-4471</span>
              <span className="ld-console__merchant-name">Global Retail Corp</span>
            </div>
            <span className={`ld-console__badge ${spikeDetected ? 'ld-console__badge--critical' : 'ld-console__badge--success'}`}>
              {spikeDetected ? 'SPIKE DETECTED' : 'NORMAL'}
            </span>
          </div>

          <div className="ld-console__risk-row">
            <div className="ld-console__risk-item">
              <div className="ld-console__risk-label">Fraud Rate</div>
              <div className={`ld-console__risk-value ${fraudRate > 5 ? 'ld-console__risk-value--critical' : fraudRate > 3 ? 'ld-console__risk-value--warning' : ''}`}>
                {fraudRate.toFixed(1)}%
              </div>
              <div className="ld-console__risk-sub">Baseline 1.8%</div>
            </div>
            <div className="ld-console__risk-item">
              <div className="ld-console__risk-label">Risk Status</div>
              <div className="ld-console__risk-value" style={{ fontSize: '14px', color: spikeDetected ? 'var(--risk-critical)' : 'var(--risk-low)' }}>
                {spikeDetected ? 'ELEVATED' : 'BASELINE'}
              </div>
              <div className="ld-console__risk-sub">Confidence 88%</div>
            </div>
            <div className="ld-console__risk-item">
              <div className="ld-console__risk-label">Exposure</div>
              <div className="ld-console__risk-value ld-console__risk-value--critical">
                ₹{(exposure / 1000).toFixed(0)}K
              </div>
              <div className="ld-console__risk-sub">Potential loss</div>
            </div>
            <div className="ld-console__risk-item">
              <div className="ld-console__risk-label">Change</div>
              <div className="ld-console__risk-value ld-console__risk-value--critical">
                +{(fraudRate / 1.8 * 100 - 100).toFixed(0)}%
              </div>
              <div className="ld-console__risk-sub">vs baseline</div>
            </div>
          </div>
        </div>

        <div className="ld-console__section">
          <div className="ld-console__chart">
            <div className="ld-console__chart-header">
              <span className="ld-console__chart-title">Fraud Activity</span>
              <div className="ld-console__chart-legend">
                <span className="ld-console__legend-item">
                  <span className="ld-console__legend-dot ld-console__legend-dot--actual" />
                  Actual
                </span>
                <span className="ld-console__legend-item">
                  <span className="ld-console__legend-dot ld-console__legend-dot--baseline" />
                  Baseline
                </span>
              </div>
            </div>
            <div className="ld-console__chart-area">
              <svg className="ld-console__chart-svg" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
                <path d={baselinePath} stroke="#C8CBD0" strokeWidth="1" strokeDasharray="4 2" fill="none" />
                <path d={actualPath} stroke="#2563EB" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                {spikeDetected && (
                  <circle cx={scaleX(90)} cy={scaleY(85)} r="4" fill="#DC2626" />
                )}
              </svg>
            </div>
          </div>
        </div>

        <div className="ld-console__section">
          <div className="ld-console__signals">
            <div className="ld-console__signals-header">
              <span>Risk Signal</span>
              <span>Status</span>
            </div>
            {signals.map((signal, i) => (
              <div key={i} className="ld-console__signal-row">
                <span className="ld-console__signal-label">{signal.label}</span>
                <span className={`ld-console__signal-status ld-console__signal-status--${signal.statusClass}`}>
                  {signal.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="ld-console__recommendation">
          <div className="ld-console__recommendation-header">
            <span className="ld-console__recommendation-label">Recommended Action</span>
          </div>
          <div className="ld-console__recommendation-value">
            {spikeDetected ? 'TEMPORARY REVIEW' : 'MONITOR'}
          </div>
          <div className="ld-console__recommendation-meta">
            Confidence: 88% • AI recommendation
          </div>
          <div className="ld-console__recommendation-actions">
            <button className="ld-console__action-btn">Review</button>
            <button className="ld-console__action-btn ld-console__action-btn--primary">Approve</button>
          </div>
          <div className="ld-console__recommendation-note">
            AI recommendation • Policy constrained • Human controlled
          </div>
        </div>
      </div>
    </>
  );
}
