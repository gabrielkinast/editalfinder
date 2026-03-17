import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

export default function ProtectedRoute({ children }) {
  const user = authService.getUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
