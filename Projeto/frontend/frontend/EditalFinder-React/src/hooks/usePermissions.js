import { useAuth } from '../contexts/AuthContext';
import { getPermissions } from '../permissions';

/**
 * Hook para acessar as permissões do usuário atual
 */
export const usePermissions = () => {
  const { user } = useAuth();
  
  // Se não houver usuário, retorna permissões mínimas (FUNCIONARIO)
  if (!user) {
    return getPermissions('FUNCIONARIO');
  }

  // Tenta obter por nível numérico primeiro, depois por tipo string
  return getPermissions(user.nivel || user.tipo);
};
