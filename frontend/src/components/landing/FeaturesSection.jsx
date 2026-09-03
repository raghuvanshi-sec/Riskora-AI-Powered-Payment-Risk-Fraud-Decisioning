export default function FeaturesSection() {
  const capabilities = [
    {
      num: '01',
      title: 'Transaction Risk',
      desc: 'XGBoost model with hybrid rules engine processes transaction-level signals, merchant context, and temporal patterns in real time.',
    },
    {
      num: '02',
      title: 'Merchant Spike Detection',
      desc: 'Time-series deviation analysis identifies abnormal fraud activity at the merchant level before losses accumulate.',
    },
    {
      num: '03',
      title: 'Explainable Decisions',
      desc: 'SHAP-powered feature attribution and triggered rules explain exactly why each risk score was generated.',
    },
  ];

  return (
    <section className="ld-section ld-section--alt" id="intelligence">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Risk Intelligence</div>
          <h2 className="ld-h2">Not just risk scores — actual intelligence</h2>
          <p className="ld-lede">
            From raw transaction signals to explainable defensive recommendations.
            Riskora provides the complete toolkit for financial fraud risk operations.
          </p>
        </div>

        <div className="ld-intelligence">
          {capabilities.map((cap) => (
            <div key={cap.num} className="ld-intelligence__card">
              <div className="ld-intelligence__num">{cap.num}</div>
              <h3 className="ld-intelligence__title">{cap.title}</h3>
              <p className="ld-intelligence__desc">{cap.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
