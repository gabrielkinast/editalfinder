import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getPermissions } from '../permissions';

/**
 * Componente para proteção de rotas com base em autenticação e permissões.
 * @param {object} props
 * @param {React.ReactNode} props.children - Componente a ser renderizado se permitido
 * @param {string} props.requiredPermission - Nome da permissão necessária (opcional)
 */
export default function ProtectedRoute({ children, requiredPermission }) {
  const { user, authenticated, loading } = useAuth();

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  // Se uma permissão específica for necessária
  if (requiredPermission) {
    const permissions = getPermissions(user.nivel || user.tipo);
    
    if (!permissions[requiredPermission]) {
      // Se não tiver permissão, redireciona para o dashboard
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
}
