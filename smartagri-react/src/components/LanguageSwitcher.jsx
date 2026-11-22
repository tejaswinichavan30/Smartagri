import { useLanguage } from '../context/LanguageContext.jsx';

export default function LanguageSwitcher() {
  const { lang, setLang, t } = useLanguage();

  const options = [
    { code: 'en', name: 'English', sub: 'EN' },
    { code: 'kn', name: 'ಕನ್ನಡ', sub: 'KN' },
    { code: 'hi', name: 'हिंदी', sub: 'HI' }
  ];

  return (
    <div className="lang-switcher">
      <span className="lang-note">🌐 {t('langNote')}</span>
      <div className="lang-buttons-group">
        {options.map((opt) => (
          <button
            key={opt.code}
            type="button"
            className={`lang-btn${lang === opt.code ? ' active' : ''}`}
            onClick={() => setLang(opt.code)}
          >
            <span className="lang-name">{opt.name}</span>
            <span className="lang-badge">{opt.sub}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
