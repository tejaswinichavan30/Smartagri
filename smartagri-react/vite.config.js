import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// SmartAgri AI frontend build config.
// The dev server proxies API calls to the Flask backend running on :5000,
// so components can just call fetch('/predict_crop') etc. without a full URL.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/login': 'http://localhost:5000',
      '/register': 'http://localhost:5000',
      '/logout': 'http://localhost:5000',
      '/reset': 'http://localhost:5000',
      '/api': 'http://localhost:5000',
      '/answer_query': 'http://localhost:5000',
      '/predict_disease': 'http://localhost:5000',
      '/predict_price': 'http://localhost:5000',
      '/predict_crop': 'http://localhost:5000',
      '/predict_irrigation': 'http://localhost:5000',
      '/planner': 'http://localhost:5000',
      '/uploads': 'http://localhost:5000'
    }
  }
});
