import { Link, useLocation } from 'react-router-dom';
import Footer from '../components/Footer.jsx';

export default function PriceResult() {
  // Expects to be navigated to with router state: { prediction: <number|string> }
  // e.g. navigate('/price-result', { state: { prediction: 2450 } })
  const { state } = useLocation();
  const prediction = state?.prediction ?? '—';

  return (
    <>
      <header className="gov-header">
        <div className="header-top">
          <div className="header-logo" role="img" aria-label="Wheat sheaf icon">🌾</div>
          <div className="header-text">
            <h1>SmartAgri AI</h1>
            <p>Agent-Based Intelligent System for Farmer Decision Support</p>
          </div>
          <div className="header-emblem" role="img" aria-label="Indian flag">🇮🇳</div>
        </div>
      </header>

      <div className="main-container">
        <div className="breadcrumb">
          <Link to="/">🏠 Home</Link>
          <span> › </span>
          <span>Market Price Prediction Result</span>
        </div>

        <div className="section-box" style={{ maxWidth: '600px', margin: '30px auto' }}>
          <div className="section-header">
            <span className="section-icon" role="img" aria-label="Money bag">💰</span>
            <div>
              <h2>Market Price Prediction Result</h2>
              <p className="section-desc">AI-predicted mandi price for your selected crop</p>
            </div>
          </div>

          <div className="price-display-box">
            <div className="price-label">Predicted Market Price</div>
            <div className="price-value">₹ {prediction}</div>
            <div className="price-unit">per quintal</div>
          </div>

          <div className="info-note" style={{ marginTop: '20px' }}>
            📌 This price is predicted based on historical mandi data.
            Actual market prices may vary. Always verify with your local mandi
            before making selling decisions.
          </div>

          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Link to="/" className="gov-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
              ← Go Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}
