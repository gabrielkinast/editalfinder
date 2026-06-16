import { BrowserRouter, HashRouter } from 'react-router-dom';
import AppRoutes from './router';
import { SettingsProvider } from './contexts/SettingsContext';
import { AuthProvider } from './contexts/AuthContext';
import { AppFeedbackProvider } from './contexts/AppFeedbackContext';
import { AppHelpProvider } from './contexts/AppHelpContext';
import { ROUTER_BASENAME, IS_TAURI_BUILD } from './config/routerBase';

const AppRouter = IS_TAURI_BUILD ? HashRouter : BrowserRouter;

function App() {
  return (
    <AuthProvider>
      <AppFeedbackProvider>
        <SettingsProvider>
          <AppRouter basename={ROUTER_BASENAME}>
            <AppHelpProvider>
              <AppRoutes />
            </AppHelpProvider>
          </AppRouter>
        </SettingsProvider>
      </AppFeedbackProvider>
    </AuthProvider>
  );
}

export default App;
