import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles/global.css';
import './styles/app-help.css';
import { applyTheme, getSavedThemePreference } from './config/theme';

/* Evita um frame de login/dashboard com tema errado antes do SettingsProvider montar. */
applyTheme(getSavedThemePreference());

const rootEl = document.getElementById('root');
let bootCompleted = false;

function renderFatalBootError(error) {
  if (!rootEl) return;
  const message = error?.message || String(error);
  rootEl.innerHTML = `
    <div style="font-family:Inter,system-ui,sans-serif;padding:24px;max-width:520px;color:#e2e8f0;background:#0f172a;min-height:100vh">
      <h1 style="margin:0 0 12px;font-size:20px">EditalFinder não iniciou</h1>
      <p style="margin:0 0 16px;line-height:1.5">O aplicativo encontrou um erro ao carregar. Tente reinstalar ou gere um novo build com <code>npm run desktop:release</code>.</p>
      <pre style="white-space:pre-wrap;font-size:12px;background:#1e293b;padding:12px;border-radius:8px">${message}</pre>
    </div>
  `;
  console.error('[EditalFinder] boot failed', error);
}

window.addEventListener('error', (event) => {
  if (bootCompleted) return;
  renderFatalBootError(event.error ?? new Error(event.message || 'Erro desconhecido'));
});

window.addEventListener('unhandledrejection', (event) => {
  if (bootCompleted) return;
  const reason = event.reason;
  renderFatalBootError(reason instanceof Error ? reason : new Error(String(reason)));
});

try {
  createRoot(rootEl).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
  bootCompleted = true;
} catch (error) {
  renderFatalBootError(error);
}
