import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';

const STRINGS = {
  tagline: {
    en: 'Agent-Based AI System for Farmer Decision Support',
    kn: 'ರೈತ ನಿರ್ಧಾರ ಬೆಂಬಲಕ್ಕಾಗಿ AI ವ್ಯವಸ್ಥೆ',
    hi: 'किसान निर्णय समर्थन के लिए AI प्रणाली'
  },
  farmer: { en: '👨‍🌾 Farmer', kn: '👨‍🌾 ರೈತ', hi: '👨‍🌾 किसान' },
  officer: { en: '👨‍💼 Officer', kn: '👨‍💼 ಅಧಿಕಾರಿ', hi: '👨‍💼 अधिकारी' },
  admin: { en: '⚙ Admin', kn: '⚙ ನಿರ್ವಾಹಕ', hi: '⚙ व्यवस्थापक' },
  loginTitle: { en: '🔐 Login to Your Account', kn: '🔐 ನಿಮ್ಮ ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ', hi: '🔐 अपने खाते में लॉगिन करें' },
  usernameLabel: {
    en: 'Username / Mobile Number',
    kn: 'ಬಳಕೆದಾರ ಹೆಸರು / ಮೊಬೈಲ್ ಸಂಖ್ಯೆ',
    hi: 'उपयोगकर्ता नाम / मोबाइल नंबर'
  },
  usernamePlaceholder: {
    en: 'Enter username or mobile number',
    kn: 'ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ನಮೂದಿಸಿ',
    hi: 'उपयोगकर्ता नाम या मोबाइल नंबर दर्ज करें'
  },
  passwordLabel: { en: 'Password', kn: 'ಪಾಸ್‌ವರ್ಡ್', hi: 'पासवर्ड' },
  passwordPlaceholder: {
    en: 'Enter your secure password',
    kn: 'ನಿಮ್ಮ ರಹಸ್ಯ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ',
    hi: 'अपना सुरक्षित पासवर्ड दर्ज करें'
  },
  showPassword: { en: 'Show Password', kn: 'ಪಾಸ್‌ವರ್ಡ್ ತೋರಿಸಿ', hi: 'पासवर्ड दिखाएं' },
  rememberMe: { en: 'Remember me', kn: 'ನನ್ನನ್ನು ನೆನಪಿಸಿಕೊಳ್ಳಿ', hi: 'मुझे याद रखें' },
  forgotPassword: { en: 'Forgot Password?', kn: 'ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?', hi: 'पासवर्ड भूल गए?' },
  loginBtn: { en: 'Login to Dashboard', kn: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಲಾಗಿನ್', hi: 'डैशबोर्ड में लॉगिन करें' },
  noAccount: { en: "Don't have an account?", kn: 'ಖಾತೆ ಇಲ್ಲವೇ?', hi: 'खाता नहीं है?' },
  registerHere: { en: 'Create Account →', kn: 'ಖಾತೆ ರಚಿಸಿ →', hi: 'खाता बनाएं →' },
  demoLogin: { en: 'Quick Demo 1-Click Login:', kn: 'ತ್ವರಿತ ಡೆಮೊ ಲಾಗಿನ್:', hi: 'त्वरित डेमो लॉगिन:' }
};

export default function Login({ onLoggedIn }) {
  const [lang, setLang] = useState('en');
  const [userType, setUserType] = useState('farmer');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const s = (key) => STRINGS[key]?.[lang] || STRINGS[key]?.en || key;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await api.login(username, password, userType, remember);
      onLoggedIn?.(username);
      navigate('/');
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.message || 'Login failed. Please check your username and password.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleQuickFill(role, user, pass) {
    setUserType(role);
    setUsername(user);
    setPassword(pass);
  }

  return (
    <div className="login-page">
      <div className="ambient-orb orb-1"></div>
      <div className="ambient-orb orb-2"></div>

      <div className="login-wrapper">
        <div className="lang-bar">
          {['en', 'kn', 'hi'].map((code) => (
            <button
              key={code}
              type="button"
              className={`lang-btn${lang === code ? ' active' : ''}`}
              onClick={() => setLang(code)}
            >
              {code === 'en' ? '🇬🇧 English' : code === 'kn' ? '🇮🇳 ಕನ್ನಡ' : '🇮🇳 हिंदी'}
            </button>
          ))}
        </div>

        <div className="login-card">
          <div className="brand-header">
            <div className="logo-emblem">🌾</div>
            <h1>
              SmartAgri AI
              <span className="badge-tag">Portal</span>
            </h1>
            <p>{s('tagline')}</p>
          </div>

          <div className="role-selector">
            {['farmer', 'officer', 'admin'].map((type) => (
              <button
                key={type}
                type="button"
                className={`role-tab${userType === type ? ' active' : ''}`}
                onClick={() => setUserType(type)}
              >
                {s(type)}
              </button>
            ))}
          </div>

          {error && (
            <div className="alert-toast error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">{s('usernameLabel')}</label>
              <div className="input-wrapper">
                <span className="input-icon">👤</span>
                <input
                  type="text"
                  className="gov-input"
                  placeholder={s('usernamePlaceholder')}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{s('passwordLabel')}</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type={showPwd ? 'text' : 'password'}
                  className="gov-input"
                  placeholder={s('passwordPlaceholder')}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowPwd(!showPwd)}
                  title={showPwd ? 'Hide Password' : 'Show Password'}
                >
                  {showPwd ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div className="form-options">
              <label className="remember-checkbox">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                />
                <span>{s('rememberMe')}</span>
              </label>
              <a href="#" className="forgot-link">{s('forgotPassword')}</a>
            </div>

            <button type="submit" className="submit-btn" disabled={submitting}>
              <span>🔐</span>
              <span>{submitting ? '…' : s('loginBtn')}</span>
            </button>
          </form>

          <div className="demo-credentials-box">
            <div className="demo-title">
              <span>⚡</span>
              <span>{s('demoLogin')}</span>
            </div>
            <div className="demo-pills">
              <button
                type="button"
                className="demo-pill"
                onClick={() => handleQuickFill('farmer', 'farmer1', 'farmer123')}
              >
                👨‍🌾 Farmer
              </button>
              <button
                type="button"
                className="demo-pill"
                onClick={() => handleQuickFill('officer', 'officer1', 'officer123')}
              >
                👨‍💼 Officer
              </button>
              <button
                type="button"
                className="demo-pill"
                onClick={() => handleQuickFill('admin', 'admin', 'admin123')}
              >
                ⚙ Admin
              </button>
            </div>
          </div>

          <div className="card-footer-links">
            <span>{s('noAccount')}</span>
            <Link to="/register">{s('registerHere')}</Link>
          </div>
        </div>

        <div className="login-page-footer">
          <p><strong>SmartAgri AI</strong> — Karnataka State Agricultural Decision Support</p>
          <p>Powered by Deep Learning CNNs & Random Forest Models</p>
        </div>
      </div>
    </div>
  );
}
