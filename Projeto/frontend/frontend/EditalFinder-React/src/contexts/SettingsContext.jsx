import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { applyTheme, getSavedThemePreference, clearThemeSystemListener } from '../config/theme';

const STORAGE_KEY = 'editalfinder_app_settings';

const DEFAULT_SETTINGS = {
  logoText: 'Edital Finder',
  logoImage: null,
  primaryBlue: '#1E88E5',
  primaryYellow: '#FFC107',
};

function loadStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_SETTINGS };
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

const SettingsContext = createContext(null);

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(loadStored);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      /* quota ou modo privado */
    }
    const root = document.documentElement;
    if (settings.primaryBlue) root.style.setProperty('--primary-blue', settings.primaryBlue);
    if (settings.primaryYellow) root.style.setProperty('--primary-yellow', settings.primaryYellow);
  }, [settings]);

  // Tema global (light/dark/system) — independente das demais configurações.
  useEffect(() => {
    applyTheme(getSavedThemePreference());
    return () => {
      clearThemeSystemListener();
    };
  }, []);

  const updateSettings = useCallback((partial) => {
    setSettings((prev) => ({ ...prev, ...partial }));
  }, []);

  const value = useMemo(() => ({ settings, updateSettings }), [settings, updateSettings]);

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error('useSettings deve ser usado dentro de SettingsProvider');
  }
  return ctx;
}
