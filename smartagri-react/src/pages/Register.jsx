import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';

const STRINGS = {
  title: { en: 'Create Account', kn: 'ಹೊಸ ಖಾತೆ ರಚಿಸಿ', hi: 'नया खाता बनाएं' },
  subtitle: {
    en: 'Join SmartAgri AI Farmer Decision Support Platform',
    kn: 'SmartAgri AI ರೈತ ಬೆಂಬಲ ವೇದಿಕೆಗೆ ಸೇರಿ',
    hi: 'SmartAgri AI किसान सहायता मंच से जुड़ें'
  },
  fullName: { en: 'Full Name', kn: 'ಪೂರ್ಣ ಹೆಸರು', hi: 'पूरा नाम' },
  fullNamePlaceholder: { en: 'Enter your full name', kn: 'ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರನ್ನು ನಮೂದಿಸಿ', hi: 'अपना पूरा नाम दर्ज करें' },
  username: { en: 'Username / Mobile Number', kn: 'ಬಳಕೆದಾರ ಹೆಸರು / ಮೊಬೈಲ್ ಸಂಖ್ಯೆ', hi: 'उपयोगकर्ता नाम / मोबाइल नंबर' },
  usernamePlaceholder: { en: 'Choose a username or mobile', kn: 'ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಮೊಬೈಲ್ ಆಯ್ಕೆಮಾಡಿ', hi: 'उपयोगकर्ता नाम या मोबाइल चुनें' },
  registerAs: { en: 'Register As', kn: 'ನೋಂದಣಿ ಪ್ರಕಾರ', hi: 'पंजीकरण प्रकार' },
  farmer: { en: '👨‍🌾 Farmer', kn: '👨‍🌾 ರೈತ', hi: '👨‍🌾 किसान' },
  officer: { en: '👨‍💼 Agriculture Officer', kn: '👨‍💼 ಕೃಷಿ ಅಧಿಕಾರಿ', hi: '👨‍💼 कृषि अधिकारी' },
  password: { en: 'Password', kn: 'ಪಾಸ್‌ವರ್ಡ್', hi: 'पासवर्ड' },
  passwordPlaceholder: { en: 'At least 6 characters', kn: 'ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು', hi: 'कम से कम 6 अक्षर' },
  confirmPassword: { en: 'Confirm Password', kn: 'ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ', hi: 'पासवर्ड पुष्टि करें' },
  confirmPasswordPlaceholder: { en: 'Re-enter your password', kn: 'ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಪುನಃ ನಮೂದಿಸಿ', hi: 'अपना पासवर्ड पुनः दर्ज करें' },
  createBtn: { en: '📝 Create Account', kn: '📝 ಖಾತೆ ರಚಿಸಿ', hi: '📝 खाता बनाएं' },
  hasAccount: { en: 'Already have an account?', kn: 'ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ?', hi: 'क्या आपके पास पहले से एक खाता है?' },
  loginHere: { en: 'Login Here →', kn: 'ಇಲ್ಲಿ ಲಾಗಿನ್ ಮಾಡಿ →', hi: 'यहाँ लॉगिन करें →' }
};

export default function Register() {
  const [lang, setLang] = useState('en');
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [userType, setUserType] = useState('farmer');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const s = (key) => STRINGS[key]?.[lang] || STRINGS[key]?.en || key;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setSubmitting(true);
    try {
      await api.register(fullName, username, userType, password, confirmPassword);
      navigate('/login');
    } catch (err) {
      console.error('Registration failed:', err);
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
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
            <h1>{s('title')}</h1>
            <p>{s('subtitle')}</p>
          </div>

          {error && (
            <div className="alert-toast error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">{s('fullName')}</label>
              <div className="input-wrapper">
                <span className="input-icon">👤</span>
                <input
                  type="text"
                  className="gov-input"
                  placeholder={s('fullNamePlaceholder')}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{s('username')}</label>
              <div className="input-wrapper">
                <span className="input-icon">📱</span>
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
              <label className="form-label">{s('registerAs')}</label>
              <div className="input-wrapper">
                <span className="input-icon">🏷️</span>
                <select
                  className="gov-input"
                  value={userType}
                  onChange={(e) => setUserType(e.target.value)}
                >
                  <option value="farmer">{s('farmer')}</option>
                  <option value="officer">{s('officer')}</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{s('password')}</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type="password"
                  className="gov-input"
                  placeholder={s('passwordPlaceholder')}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{s('confirmPassword')}</label>
              <div className="input-wrapper">
                <span className="input-icon">🔐</span>
                <input
                  type="password"
                  className="gov-input"
                  placeholder={s('confirmPasswordPlaceholder')}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button type="submit" className="submit-btn" disabled={submitting}>
              <span>{submitting ? '…' : s('createBtn')}</span>
            </button>
          </form>

          <div className="card-footer-links">
            <span>{s('hasAccount')}</span>{' '}
            <Link to="/login">{s('loginHere')}</Link>
          </div>
        </div>

        <div className="login-page-footer">
          <p><strong>SmartAgri AI</strong> — Karnataka State Agricultural Decision Support</p>
        </div>
      </div>
    </div>
  );
}
