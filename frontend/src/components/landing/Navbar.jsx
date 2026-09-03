import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="ld-nav">
      <div className="ld-container ld-nav__inner">
        <a href="#top" className="ld-nav__brand">
          <div className="ld-nav__logo">R</div>
          <span className="ld-nav__name">Riskora</span>
        </a>

        <div className="ld-nav__center">
          <a href="#features" className="ld-nav__link">Product</a>
          <a href="#pipeline" className="ld-nav__link">How It Works</a>
          <a href="#intelligence" className="ld-nav__link">Risk Intelligence</a>
          <a href="#metrics" className="ld-nav__link">Metrics</a>
        </div>

        <div className="ld-nav__actions">
          <button
            onClick={() => navigate('/login')}
            className="ld-btn ld-btn--ghost ld-btn--sm"
          >
            Sign In
          </button>
          <button
            onClick={() => navigate('/app')}
            className="ld-btn ld-btn--primary ld-btn--sm"
          >
            Open Dashboard
          </button>
        </div>
      </div>
    </nav>
  );
}
