export default function CredibilityStrip() {
  const items = [
    { icon: '📊', text: 'IEEE-CIS Dataset' },
    { icon: '🤖', text: 'XGBoost + SHAP' },
    { icon: '⚡', text: 'Real-Time Processing' },
    { icon: '🔒', text: 'Auditable Decisions' },
  ];

  return (
    <section className="ld-cred">
      <div className="ld-container ld-cred__inner">
        {items.map((item, i) => (
          <div key={i} className="ld-cred__item">
            <svg className="ld-cred__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span>{item.text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
