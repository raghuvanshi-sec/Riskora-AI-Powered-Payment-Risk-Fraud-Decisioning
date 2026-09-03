export default function FeaturesSection() {
  const capabilities = [
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
      ),
      title: 'AI Fraud Detection',
      desc: 'XGBoost model with hybrid rules engine processes transaction-level signals, merchant context, and temporal patterns in real time.',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 3v18h18"/>
          <path d="m19 9-5 5-4-4-3 3"/>
        </svg>
      ),
      title: 'Spike Detection',
      desc: 'Time-series deviation analysis identifies abnormal fraud activity at the merchant level before losses accumulate.',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4"/>
          <path d="M12 8h.01"/>
        </svg>
      ),
      title: 'Explainable AI',
      desc: 'SHAP-powered feature attribution and triggered rules explain exactly why each risk score was generated.',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18"/>
          <path d="M9 21V9"/>
        </svg>
      ),
      title: 'Risk Case Management',
      desc: 'Structured workflow for analyst review with full transaction context, risk evidence, and decision history.',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
      ),
      title: 'Rule-Based Engine',
      desc: 'Configurable business rules that complement ML models with deterministic policy controls.',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      ),
      title: 'Audit Trail',
      desc: 'Complete decision logging with timestamps, actor information, and reasoning for compliance.',
    },
  ];

  return (
    <section className="ld-section" id="features">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Product</div>
          <h2 className="ld-h2">Enterprise fraud risk infrastructure</h2>
          <p className="ld-lede">
            From real-time transaction evaluation to analyst-assisted decisions.
            Riskora handles the complete fraud risk lifecycle.
          </p>
        </div>

        <div className="ld-features">
          {capabilities.map((cap, i) => (
            <div key={i} className="ld-feature">
              <div className="ld-feature__icon">{cap.icon}</div>
              <h3 className="ld-feature__title">{cap.title}</h3>
              <p className="ld-feature__desc">{cap.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
