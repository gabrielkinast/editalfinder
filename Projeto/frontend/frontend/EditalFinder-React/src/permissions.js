/**
 * Sistema de Controle de Permissões (RBAC) - EditalFinder
 */

export const PERMISSIONS = {
  ADMIN: {
    label: 'Administrador',
    level: 1,
    canViewCadastros: true,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canManageUsers: true,
  },
  CONSULTOR: {
    label: 'Consultor',
    level: 2,
    canViewCadastros: true,
    canCreate: true, // Pode criar registros (clientes, etc)
    canEdit: true,
    canDelete: false,
    canManageUsers: false,
  },
  FUNCIONARIO: {
    label: 'Funcionário',
    level: 3,
    canViewCadastros: true,
    canCreate: false, // Apenas visualização
    canEdit: false,
    canDelete: false,
    canManageUsers: false,
  }
};

/**
 * Retorna as permissões com base no tipo_usuario ou nivel_acesso
 * @param {string|number} userRoleOrLevel 
 * @returns {object}
 */
export const getPermissions = (userRoleOrLevel) => {
  // Se for nível numérico
  if (typeof userRoleOrLevel === 'number') {
    const role = Object.values(PERMISSIONS).find(p => p.level === userRoleOrLevel);
    return role || PERMISSIONS.FUNCIONARIO;
  }

  // Se for string (tipo_usuario)
  const normalizedRole = String(userRoleOrLevel).toUpperCase();
  if (normalizedRole === 'ADMINISTRADOR' || normalizedRole === 'ADMIN') return PERMISSIONS.ADMIN;
  if (normalizedRole === 'CONSULTOR') return PERMISSIONS.CONSULTOR;
  if (normalizedRole === 'FUNCIONARIO' || normalizedRole === 'FUNCIONÁRIO') return PERMISSIONS.FUNCIONARIO;

  return PERMISSIONS.FUNCIONARIO;
};
