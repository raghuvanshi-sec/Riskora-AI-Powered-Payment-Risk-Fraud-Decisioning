export default function MetricsSection() {
  const metrics = [
    { value: '42%', label: 'Precision', delta: '+2.1%' },
    { value: '35%', label: 'Recall', delta: '+1.8%' },
    { value: '38%', label: 'F1 Score', delta: '+1.5%' },
    { value: '48%', label: 'PR-AUC', delta: '+3.2%' },
  ];

  return (
    <section className="ld-section ld-section--alt" id="metrics">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Model Evaluation</div>
          <h2 className="ld-h2">Performance on IEEE-CIS dataset</h2>
          <p className="ld-lede">
            Chronological replay evaluation using XGBoost with SHAP explainability.
          </p>
        </div>

        <div className="ld-metrics">
          {metrics.map((metric, i) => (
            <div key={i} className="ld-metrics__card">
              <div className="ld-metrics__value">{metric.value}</div>
              <div className="ld-metrics__label">{metric.label}</div>
              <div className="ld-metrics__delta ld-metrics__delta--up">{metric.delta} vs baseline</div>
            </div>
          ))}
        </div>

        <p style={{ textAlign: 'center', marginTop: '32px', fontSize: '13px', color: 'var(--text-tertiary)', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto' }}>
          Evaluation based on a chronological IEEE-CIS replay using a demonstrational merchant proxy. Actual production performance may vary based on data distribution.
        </p>
      </div>
    </section>
  );
}
