import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './router';
import { SettingsProvider } from './contexts/SettingsContext';
import { AuthProvider } from './contexts/AuthContext';
import { AppFeedbackProvider } from './contexts/AppFeedbackContext';
import { AppHelpProvider } from './contexts/AppHelpContext';
import { ROUTER_BASENAME } from './config/routerBase';

function App() {
  return (
    <AuthProvider>
      <AppFeedbackProvider>
        <SettingsProvider>
          <BrowserRouter basename={ROUTER_BASENAME}>
            <AppHelpProvider>
              <AppRoutes />
            </AppHelpProvider>
          </BrowserRouter>
        </SettingsProvider>
      </AppFeedbackProvider>
    </AuthProvider>
  );
}

export default App;
