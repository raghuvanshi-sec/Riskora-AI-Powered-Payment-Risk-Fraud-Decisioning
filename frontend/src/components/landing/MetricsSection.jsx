export default function MetricsSection() {
  const metrics = [
    { value: '42%', label: 'Precision' },
    { value: '35%', label: 'Recall' },
    { value: '38%', label: 'F1 Score' },
    { value: '48%', label: 'PR-AUC' },
  ];

  return (
    <section className="ld-section" id="metrics">
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
            </div>
          ))}
        </div>

        <div className="ld-metrics__note">
          Evaluation based on a chronological IEEE-CIS replay using a demonstrational
          merchant proxy. Actual production performance may vary based on data distribution.
        </div>
      </div>
    </section>
  );
}
