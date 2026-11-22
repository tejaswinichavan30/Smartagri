import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Dashboard from './pages/Dashboard.jsx';
import PriceResult from './pages/PriceResult.jsx';

export default function App() {
  // Minimal client-side session flag. The Flask backend still owns the real
  // session (via cookies from /login), this just controls which routes
  // React shows without a page reload.
  const [userName, setUserName] = useState(null);

  function handleLoggedIn(name) {
    setUserName(name);
  }

  function handleLogout() {
    setUserName(null);
  }

  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={<Login onLoggedIn={handleLoggedIn} />}
          />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              userName
                ? <Dashboard userName={userName} onLogout={handleLogout} />
                : <Navigate to="/login" replace />
            }
          />
          <Route path="/price-result" element={<PriceResult />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}
