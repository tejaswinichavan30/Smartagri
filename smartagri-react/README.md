# SmartAgri AI — React Frontend

This is a React (Vite) conversion of the original Flask/Jinja2 templates
(`index.html`, `login.html`, `register.html`, `results.html`) for the
SmartAgri AI farmer decision-support app.

## What changed from the Jinja templates

- **Routing**: `react-router-dom` replaces server-rendered pages.
  `/login`, `/register`, `/` (dashboard), `/price-result`.
- **Language switching**: `{% if data-en/data-kn/data-hi %}` attributes became
  a `LanguageContext` + `translations` dictionary (`src/context/LanguageContext.jsx`),
  with the login/register pages keeping their own small string tables since
  they're outside the main app shell.
- **Forms**: every `<form action="/..." method="POST">` became a React form
  that calls the matching Flask endpoint through `src/api.js` with `fetch`.
- **Voice input**: `startVoice()` is implemented with the browser
  `SpeechRecognition` API (falls back to a friendly alert if unsupported).
- **District soil auto-fill**: `autoFillSoilData()` is implemented in
  `src/data/districts.js` with placeholder typical N/P/K/pH/rainfall values
  per Karnataka district — swap in your real dataset/backend call as needed.
- **Styling**: `style.css` plus the inline `<style>` blocks from the login and
  register pages were merged into `src/index.css`, class names untouched.

## Backend contract assumptions

The Flask endpoints below are called as-is. Where the original template only
showed pre-rendered HTML, this frontend expects **JSON** responses so it can
render them into components:

| Endpoint            | Method | Expected JSON shape (suggested)                                   |
|----------------------|--------|---------------------------------------------------------------------|
| `/login`             | POST   | sets session cookie; any 200 response                              |
| `/register`          | POST   | any 200 response                                                    |
| `/answer_query`      | POST   | `{ "answer": "..." }` or plain text                                 |
| `/predict_disease`   | POST   | `{ "result": "..." }` or plain text                                 |
| `/predict_price`     | POST   | `{ "prediction": 2450 }` or plain text                               |
| `/predict_crop`      | POST   | `{ "crop": "...", "weather": "..." }` or plain text                 |
| `/planner`           | POST   | `{ "priority": [...], "summary": "...", "advice": [...], "alerts": [...], "planting_schedule": "...", "harvest_schedule": "...", "fertilizer_plan": "...", "sell_recommendation": "...", "pest_guide": [...] }` |

If your Flask routes still return full HTML pages, either add a JSON mode
(e.g. checking `Accept: application/json` or a `?format=json` param) or
adjust `src/api.js` to parse the HTML response.

## Getting started

```bash
npm install
npm run dev      # http://localhost:5173, proxies API calls to Flask on :5000
npm run build    # production build into dist/
```

Update the proxy target in `vite.config.js` if your Flask server runs on a
different host/port.
