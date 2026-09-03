export default function ActionsSection() {
  return (
    <section className="ld-section" id="actions">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Defensive Response</div>
          <h2 className="ld-h2">Bounded action recommendations</h2>
          <p className="ld-lede">
            AI recommends. Policy constrains. Human approval remains where required.
          </p>
        </div>

        <div className="ld-workflow">
          <div className="ld-workflow__stage">
            <div className="ld-workflow__stage-header">
              <span className="ld-workflow__stage-label">Detected</span>
              <span className="ld-workflow__stage-number">1</span>
            </div>
            <div className="ld-workflow__stage-content">
              <div className="ld-workflow__title">Merchant fraud spike</div>
              <p className="ld-workflow__desc">
                Fraud rate elevated from 1.8% to 5.1% at merchant M-4471.
                Baseline deviation: HIGH.
              </p>
            </div>
          </div>

          <div className="ld-workflow__stage">
            <div className="ld-workflow__stage-header">
              <span className="ld-workflow__stage-label">Recommended</span>
              <span className="ld-workflow__stage-number">2</span>
            </div>
            <div className="ld-workflow__stage-content">
              <div className="ld-workflow__highlight">
                <div className="ld-workflow__title">TEMPORARY REVIEW</div>
                <p className="ld-workflow__confidence">Confidence: 88%</p>
              </div>
              <p className="ld-workflow__desc" style={{ marginTop: '12px' }}>
                Temporarily flag transactions from this merchant for analyst review.
                Auto-resolves after approval.
              </p>
            </div>
          </div>

          <div className="ld-workflow__stage">
            <div className="ld-workflow__stage-header">
              <span className="ld-workflow__stage-label">Alternatives</span>
              <span className="ld-workflow__stage-number">3</span>
            </div>
            <div className="ld-workflow__stage-content">
              <div className="ld-workflow__alternatives">
                <span className="ld-workflow__alt-tag">MONITOR</span>
                <span className="ld-workflow__alt-tag">STEP_UP</span>
                <span className="ld-workflow__alt-tag">RATE_LIMIT</span>
                <span className="ld-workflow__alt-tag">HOLD</span>
              </div>
              <div className="ld-workflow__audit">
                <div className="ld-workflow__audit-item">
                  <span className="ld-workflow__audit-dot" />
                  <span>Decision recorded</span>
                </div>
                <div className="ld-workflow__audit-item">
                  <span className="ld-workflow__audit-dot" />
                  <span>Policy constrained</span>
                </div>
                <div className="ld-workflow__audit-item">
                  <span className="ld-workflow__audit-dot" />
                  <span>Human controlled</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
