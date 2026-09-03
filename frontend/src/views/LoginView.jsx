import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../services/api';

export default function LoginView() {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  // After login, land on the dashboard (/app) by default; if the user
  // was redirected from a protected route, return them to that page.
  const from = location.state?.from?.pathname || '/app';

  // If the user is already authenticated, skip the login form and go
  // straight to the dashboard (or back to the page they were redirected from).
  useEffect(() => {
    if (user) {
      navigate(from, { replace: true });
    }
  }, [user, from, navigate]);

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setName('');
    setError('');
  };

  const toggleMode = () => {
    setMode((m) => (m === 'login' ? 'register' : 'login'));
    resetForm();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      if (mode === 'register') {
        await api.post('/auth/register', {
          email,
          password,
          name,
        });
        // Auto-login after successful registration
        await login(email, password);
      } else {
        await login(email, password);
      }
      navigate(from, { replace: true });
    } catch (err) {
      if (err.response && err.response.status === 400) {
        const detail = err.response.data?.detail;
        if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError('Invalid email or password.');
        }
      } else {
        setError('Unable to connect to Riskora. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card card">
        <div className="login-header">
          <div className="login-logo">
            <div className="logo-icon">R</div>
            <h2>Riskora</h2>
          </div>
          <p className="login-subtitle">AI-Powered Risk Intelligence</p>
          <div className="login-title-area">
            <h3>{mode === 'register' ? 'Create account' : 'Welcome back'}</h3>
            <p>{mode === 'register' ? 'Sign up to continue' : 'Sign in to continue'}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="alert alert-error">{error}</div>}

          {mode === 'register' && (
            <div className="form-group">
              <label className="form-label" htmlFor="name">Name</label>
              <input
                className="form-input"
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={isSubmitting}
                minLength={2}
                maxLength={100}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email</label>
            <input
              className="form-input"
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              className="form-input"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isSubmitting}
              minLength={6}
              maxLength={100}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary login-btn"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? mode === 'register'
                ? 'Creating account...'
                : 'Signing in...'
              : mode === 'register'
                ? 'Sign Up'
                : 'Sign In'}
          </button>
        </form>

        <div className="login-footer">
          <p className="security-notice">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Secured by Riskora Core Auth
          </p>
          <p className="login-toggle" style={{ marginTop: '12px', fontSize: '14px' }}>
            {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={toggleMode}
              style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '14px', fontWeight: 600, padding: 0 }}
            >
              {mode === 'login' ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>

      <style>{`
        .login-container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background-color: var(--bg-main);
          padding: 20px;
        }
        .login-card {
          width: 100%;
          max-width: 400px;
          padding: 40px;
          border-radius: 12px;
          border: 1px solid var(--border-color);
        }
        .login-header {
          text-align: center;
          margin-bottom: 30px;
        }
        .login-logo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          margin-bottom: 8px;
        }
        .login-logo .logo-icon {
          width: 32px;
          height: 32px;
          background-color: var(--accent);
          color: white;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 18px;
        }
        .login-logo h2 {
          font-size: 24px;
          color: var(--text-main);
          margin: 0;
        }
        .login-subtitle {
          color: var(--text-secondary);
          font-size: 14px;
          margin-bottom: 24px;
        }
        .login-title-area h3 {
          font-size: 20px;
          margin: 0 0 4px 0;
          color: var(--text-main);
        }
        .login-title-area p {
          color: var(--text-secondary);
          margin: 0;
          font-size: 14px;
        }
        .login-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .login-btn {
          width: 100%;
          padding: 12px;
          font-size: 15px;
          font-weight: 600;
          margin-top: 10px;
        }
        .alert-error {
          background-color: rgba(220, 38, 38, 0.1);
          color: var(--color-high);
          border: 1px solid rgba(220, 38, 38, 0.2);
          padding: 12px;
          border-radius: 6px;
          font-size: 14px;
        }
        .login-footer {
          margin-top: 30px;
          text-align: center;
          border-top: 1px solid var(--border-color);
          padding-top: 20px;
        }
        .security-notice {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          color: var(--text-muted);
          font-size: 12px;
          margin: 0;
        }
      `}</style>
    </div>
  );
}