import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import AppHelpModal from '../components/help/AppHelpModal';
import HelpFirstVisitBanner from '../components/help/HelpFirstVisitBanner';
import { HELP_STORAGE_KEY, sectionFromPathname } from '../components/help/helpContent';

const AppHelpContext = createContext(null);

export function AppHelpProvider({ children }) {
  const [open, setOpen] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState('getting-started');
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();

  const markHelpSeen = useCallback(() => {
    try {
      localStorage.setItem(HELP_STORAGE_KEY, '1');
    } catch {
      /* ignore */
    }
  }, []);

  const openHelp = useCallback(
    (sectionId) => {
      if (sectionId) setActiveSectionId(sectionId);
      setOpen(true);
      markHelpSeen();
    },
    [markHelpSeen],
  );

  const closeHelp = useCallback(() => {
    setOpen(false);
    if (searchParams.get('help')) {
      const next = new URLSearchParams(searchParams);
      next.delete('help');
      setSearchParams(next, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    const param = searchParams.get('help');
    if (!param) return;
    openHelp(param);
  }, [searchParams, openHelp]);

  const value = useMemo(
    () => ({
      open,
      activeSectionId,
      openHelp,
      closeHelp,
      markHelpSeen,
      openHelpForCurrentPage: () => openHelp(sectionFromPathname(location.pathname)),
    }),
    [open, activeSectionId, openHelp, closeHelp, markHelpSeen, location.pathname],
  );

  return (
    <AppHelpContext.Provider value={value}>
      {children}
      <HelpFirstVisitBanner />
      {open && (
        <AppHelpModal
          activeSectionId={activeSectionId}
          onSectionChange={setActiveSectionId}
          onClose={closeHelp}
        />
      )}
    </AppHelpContext.Provider>
  );
}

export function useAppHelp() {
  const ctx = useContext(AppHelpContext);
  if (!ctx) {
    throw new Error('useAppHelp deve ser usado dentro de AppHelpProvider');
  }
  return ctx;
}

export function useAppHelpOptional() {
  return useContext(AppHelpContext);
}
