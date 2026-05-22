import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './router';
import { SettingsProvider } from './contexts/SettingsContext';
import { AuthProvider } from './contexts/AuthContext';
import { AppFeedbackProvider } from './contexts/AppFeedbackContext';

function App() {
  return (
    <AuthProvider>
      <AppFeedbackProvider>
        <SettingsProvider>
          <BrowserRouter basename="/editalfinder">
            <AppRoutes />
          </BrowserRouter>
        </SettingsProvider>
      </AppFeedbackProvider>
    </AuthProvider>
  );
}

export default App;
