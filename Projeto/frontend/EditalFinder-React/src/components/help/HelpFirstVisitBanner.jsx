import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAppHelp } from '../../contexts/AppHelpContext';
import { HELP_STORAGE_KEY } from './helpContent';

const HIDDEN_ROUTES = ['/login', '/auth/callback'];

export default function HelpFirstVisitBanner() {
  const { openHelp, markHelpSeen } = useAppHelp();
  const location = useLocation();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (HIDDEN_ROUTES.some((r) => location.pathname.startsWith(r))) {
      setVisible(false);
      return;
    }
    try {
      setVisible(localStorage.getItem(HELP_STORAGE_KEY) !== '1');
    } catch {
      setVisible(false);
    }
  }, [location.pathname]);

  if (!visible) return null;

  const dismiss = () => {
    markHelpSeen();
    setVisible(false);
  };

  const openTutorial = () => {
    markHelpSeen();
    setVisible(false);
    openHelp('getting-started');
  };

  return (
    <div className="app-help-first-visit" role="status">
      <span>Primeira vez aqui? Veja o tutorial para aprender a usar o EditalFinder.</span>
      <div className="app-help-first-visit-actions">
        <button type="button" className="app-help-first-visit-primary" onClick={openTutorial}>
          Ver tutorial
        </button>
        <button type="button" className="app-help-first-visit-dismiss" onClick={dismiss}>
          Fechar
        </button>
      </div>
    </div>
  );
}
