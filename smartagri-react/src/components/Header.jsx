import { useLanguage } from '../context/LanguageContext.jsx';

export default function Header({ userName, onLogout, showNav = true }) {
  const { t } = useLanguage();

  return (
    <header className="gov-header">
      <div className="header-top">
        <div className="header-left">
          <div className="header-logo" role="img" aria-label="Wheat sheaf icon">🌾</div>
        </div>

        <div className="header-text">
          <h1>SmartAgri AI</h1>
          <p>{t('tagline')}</p>
        </div>

        <div className="header-right">
          {userName && (
            <div className="header-user">
              <span>👤 Welcome, {userName}!</span>
              <a href="/logout" className="logout-btn" onClick={onLogout}>🚪 Logout</a>
            </div>
          )}
        </div>
      </div>

      {showNav && (
        <nav className="gov-nav">
          <a href="#crop">{t('navCrop')}</a>
          <a href="#price">{t('navPrice')}</a>
          <a href="#disease">{t('navDisease')}</a>
          <a href="#irrigation">{t('navIrrigation')}</a>
          <a href="#planner">{t('navPlanner')}</a>
          <a href="#decision-intelligence">🧠 Decision Intelligence</a>
        </nav>
      )}
    </header>
  );
}
