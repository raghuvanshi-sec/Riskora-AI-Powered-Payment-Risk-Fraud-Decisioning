export default function ArchitectureSection() {
  const stages = [
    'Transactions',
    'Transaction Risk Engine',
    'Merchant Aggregation',
    'Baseline',
    'Spike Detection',
    'Exposure Estimation',
    'SHAP / Explanation',
    'Defensive Recommendation',
    'Audit Trail',
  ];

  return (
    <section className="ld-section ld-section--alt" id="architecture">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Architecture</div>
          <h2 className="ld-h2">System overview</h2>
          <p className="ld-lede">
            From raw transaction ingestion to explainable defensive action.
          </p>
        </div>

        <div className="ld-arch">
          {stages.map((label, i) => (
            <div key={i} className="ld-arch__stage">
              <div className="ld-arch__num">{String(i + 1).padStart(2, '0')}</div>
              <div className="ld-arch__label">{label}</div>
              {i < stages.length - 1 && (
                <div className="ld-arch__arrow">↓</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
