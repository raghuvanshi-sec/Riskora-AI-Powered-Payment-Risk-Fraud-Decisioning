import { useNavigate } from 'react-router-dom';
import RiskConsole from './RiskConsole';

export default function Hero() {
  const navigate = useNavigate();

  return (
    <section className="ld-hero" id="top">
      <div className="ld-hero__bg" aria-hidden="true">
        <div className="ld-hero__bg-grid" />
        <div className="ld-hero__bg-glow" />
      </div>

      <div className="ld-container ld-hero__inner">
        <div className="ld-hero__content">
          <div className="ld-hero__eyebrow">AI Fraud Risk Intelligence</div>

          <h1 className="ld-hero__headline">
            AI-Powered Payment<br />
            <em>Risk & Fraud</em><br />
            Decisioning
          </h1>

          <p className="ld-hero__subhead">
            Riskora evaluates every transaction, detects suspicious merchant behavior,
            generates explainable risk scores, and supports both automated and analyst-assisted
            decisions — all within bounded, auditable policy controls.
          </p>

          <div className="ld-hero__actions">
            <button
              onClick={() => navigate('/app')}
              className="ld-btn ld-btn--primary ld-btn--lg"
            >
              Open Dashboard
            </button>
            <a href="#pipeline" className="ld-btn ld-btn--secondary ld-btn--lg">
              Explore the System
            </a>
          </div>

          <div className="ld-hero__meta">
            <div className="ld-hero__meta-item">
              <span className="ld-hero__meta-label">Dataset</span>
              <span className="ld-hero__meta-value">IEEE-CIS</span>
            </div>
            <div className="ld-hero__meta-item">
              <span className="ld-hero__meta-label">Model</span>
              <span className="ld-hero__meta-value">XGBoost + SHAP</span>
            </div>
            <div className="ld-hero__meta-item">
              <span className="ld-hero__meta-label">Engine</span>
              <span className="ld-hero__meta-value">Hybrid Risk</span>
            </div>
            <div className="ld-hero__meta-item">
              <span className="ld-hero__meta-label">Detection</span>
              <span className="ld-hero__meta-value">Spike Analysis</span>
            </div>
          </div>
        </div>

        <div className="ld-hero__console">
          <RiskConsole />
        </div>
      </div>
    </section>
  );
}
