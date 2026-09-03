export default function CredibilityStrip() {
  const items = [
    'IEEE-CIS Fraud Data',
    'XGBoost',
    'SHAP Explainability',
    'Time-Series Analytics',
    'Auditable Decisions',
  ];

  return (
    <section className="ld-credibility">
      <div className="ld-container ld-credibility__inner">
        {items.map((item, i) => (
          <div key={i} className="ld-credibility__item">
            {i > 0 && <span className="ld-credibility__dot" />}
            <span>{item}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
