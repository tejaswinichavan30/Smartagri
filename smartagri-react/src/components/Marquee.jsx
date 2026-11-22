import { useLanguage } from '../context/LanguageContext.jsx';

export default function Marquee() {
  const { t } = useLanguage();
  return (
    <div className="marquee-bar" aria-label="Announcements">
      <div className="marquee-track">
        <span>{t('marquee')}</span>
      </div>
    </div>
  );
}
