export default function ExposureSection() {
  return (
    <section className="ld-section ld-section--alt" id="exposure">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Exposure Analysis</div>
          <h2 className="ld-h2">Know the risk. Quantify the loss.</h2>
        </div>

        <div className="ld-exposure">
          <div className="ld-exposure__metrics">
            <div className="ld-exposure__metric">
              <div className="ld-exposure__metric-label">Observed Fraud</div>
              <div className="ld-exposure__metric-value">₹48,200</div>
              <div className="ld-exposure__metric-sub">24h window</div>
            </div>
            <div className="ld-exposure__metric">
              <div className="ld-exposure__metric-label">Baseline Fraud</div>
              <div className="ld-exposure__metric-value">₹4,200</div>
              <div className="ld-exposure__metric-sub">Expected for period</div>
            </div>
            <div className="ld-exposure__metric ld-exposure__metric--highlighted">
              <div className="ld-exposure__metric-label">Potential Exposure</div>
              <div className="ld-exposure__metric-value">₹204,000</div>
              <div className="ld-exposure__metric-sub">At current trajectory</div>
            </div>
            <div className="ld-exposure__metric">
              <div className="ld-exposure__metric-label">Detection Delay</div>
              <div className="ld-exposure__metric-value">18 min</div>
              <div className="ld-exposure__metric-sub">Avg. time to alert</div>
            </div>
          </div>
          
          <div className="ld-exposure__content">
            <h3 className="ld-exposure__title">
              Exposure estimation for informed decisions
            </h3>
            <p className="ld-exposure__desc">
              Riskora estimates financial exposure associated with abnormal merchant
              activity so analysts can prioritize intervention based on potential
              impact rather than just risk scores.
            </p>
            <div className="ld-exposure__demo">Illustrative scenario</div>
          </div>
        </div>
      </div>
    </section>
  );
}
