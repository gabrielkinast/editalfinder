import { useState, useEffect, useCallback } from 'react';

const LS_KEY = 'editais_catalog_prefs_v1';

export const DEFAULT_EDITAIS_PAGE_PREFS = {
  showRuidos: false,
  preferPdf: false,
  preferNacional: false,
  preferInternacional: false,
  density: 'normal',
  pageSize: 40,
};

function loadPrefs() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return { ...DEFAULT_EDITAIS_PAGE_PREFS };
    return { ...DEFAULT_EDITAIS_PAGE_PREFS, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_EDITAIS_PAGE_PREFS };
  }
}

export function useEditaisPagePrefs() {
  const [prefs, setPrefsState] = useState(loadPrefs);

  useEffect(() => {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(prefs));
    } catch {
      /* ignore */
    }
  }, [prefs]);

  const updatePrefs = useCallback((partial) => {
    setPrefsState((p) => ({ ...p, ...partial }));
  }, []);

  return { prefs, setPrefsState, updatePrefs };
}
