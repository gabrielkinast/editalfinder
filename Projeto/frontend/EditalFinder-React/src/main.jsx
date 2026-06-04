import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles/global.css';
import './styles/app-help.css';
import { applyTheme, getSavedThemePreference } from './config/theme';

/* Evita um frame de login/dashboard com tema errado antes do SettingsProvider montar. */
applyTheme(getSavedThemePreference());

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
