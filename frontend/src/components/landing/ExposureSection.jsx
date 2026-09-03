export default function ExposureSection() {
  return (
    <section className="ld-section" id="exposure">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Exposure Analysis</div>
          <h2 className="ld-h2">Know the risk. Quantify the loss.</h2>
          <p className="ld-lede">
            Riskora estimates financial exposure so analysts can prioritize intervention
            based on potential impact.
          </p>
        </div>

        <div className="ld-metrics">
          <div className="ld-metrics__card">
            <div className="ld-metrics__value">₹48.2K</div>
            <div className="ld-metrics__label">Observed Fraud</div>
            <div className="ld-metrics__delta ld-metrics__delta--up">24h window</div>
          </div>
          <div className="ld-metrics__card">
            <div className="ld-metrics__value">₹4.2K</div>
            <div className="ld-metrics__label">Baseline Fraud</div>
            <div className="ld-metrics__delta">Expected</div>
          </div>
          <div className="ld-metrics__card">
            <div className="ld-metrics__value" style={{ color: 'var(--risk-high)' }}>₹204K</div>
            <div className="ld-metrics__label">Potential Exposure</div>
            <div className="ld-metrics__delta ld-metrics__delta--down">At trajectory</div>
          </div>
          <div className="ld-metrics__card">
            <div className="ld-metrics__value">18m</div>
            <div className="ld-metrics__label">Detection Delay</div>
            <div className="ld-metrics__delta">Avg. alert time</div>
          </div>
        </div>
      </div>
    </section>
  );
}
