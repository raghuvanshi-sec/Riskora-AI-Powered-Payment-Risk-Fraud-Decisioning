import { useNavigate } from 'react-router-dom';

export default function Footer() {
  const navigate = useNavigate();

  return (
    <footer className="ld-footer">
      <div className="ld-container">
        <div className="ld-footer__inner">
          <div className="ld-footer__brand">
            <div className="ld-footer__logo">R</div>
            <div>
              <div className="ld-footer__name">Riskora</div>
              <div className="ld-footer__tagline">AI Fraud Risk Intelligence</div>
            </div>
          </div>

          <div className="ld-footer__links">
            <div>
              <div className="ld-footer__column-title">Product</div>
              <a href="#features" className="ld-footer__link">Features</a>
              <a href="#pipeline" className="ld-footer__link">How It Works</a>
              <a href="#metrics" className="ld-footer__link">Metrics</a>
            </div>
            <div>
              <div className="ld-footer__column-title">Resources</div>
              <a href="#exposure" className="ld-footer__link">Exposure Analysis</a>
              <a href="#actions" className="ld-footer__link">Defensive Actions</a>
            </div>
            <div>
              <div className="ld-footer__column-title">Platform</div>
              <button onClick={() => navigate('/app')} className="ld-footer__link">Dashboard</button>
              <button onClick={() => navigate('/login')} className="ld-footer__link">Sign In</button>
            </div>
          </div>
        </div>

        <div className="ld-footer__bottom">
          <div className="ld-footer__copy">
            © 2024 Riskora. Fraud risk intelligence for financial operations.
          </div>
          <div className="ld-footer__links" style={{ gap: '24px', marginTop: 0 }}>
            <a href="#" className="ld-footer__link" style={{ marginBottom: 0 }}>Privacy</a>
            <a href="#" className="ld-footer__link" style={{ marginBottom: 0 }}>Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
