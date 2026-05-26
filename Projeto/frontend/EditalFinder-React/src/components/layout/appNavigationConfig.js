import {
  ENABLE_CONCURSOS,
  ENABLE_CONSULTOR_WORKSPACE,
  FEATURE_RADAR,
} from '../../config/env';

const ENABLE_INDICE = import.meta.env.VITE_ENABLE_INDICE === 'true';

/**
 * Seções do menu principal (hambúrguer). Cada item: { id, to, label, end?, show? }
 * @param {object} permissions — usePermissions()
 */
export function buildAppNavigationSections(permissions = {}) {
  const sections = [];

  const principal = [
    { id: 'home-dashboard', to: '/dashboard', label: 'Dashboard', end: true },
    { id: 'editais', to: '/editais', label: 'Editais', end: false },
    { id: 'cadastros', to: '/cadastros', label: 'Cadastros', show: Boolean(permissions.canViewCadastros) },
    { id: 'radar', to: '/radar-fomento', label: 'Radar', show: FEATURE_RADAR },
  ].filter((i) => i.show !== false);

  if (principal.length) {
    sections.push({ id: 'principal', label: 'Principal', items: principal });
  }

  const workspaces = [
    {
      id: 'workspace-consultor',
      to: '/workspace-consultor',
      label: 'Workspace do Consultor',
      show: ENABLE_CONSULTOR_WORKSPACE && Boolean(permissions.canViewCadastros),
    },
  ].filter((i) => i.show !== false);

  if (workspaces.length) {
    sections.push({ id: 'workspaces', label: 'Workspaces', items: workspaces });
  }

  const conteudo = [
    { id: 'noticias', to: '/noticias', label: 'Notícias' },
    { id: 'pesquisas', to: '/pesquisas', label: 'Pesquisas' },
    { id: 'portais', to: '/portais-estrategicos', label: 'Portais' },
    { id: 'concursos', to: '/concursos', label: 'Concursos', show: ENABLE_CONCURSOS },
    { id: 'indice', to: '/indice', label: 'Índice', show: ENABLE_INDICE },
  ].filter((i) => i.show !== false);

  sections.push({ id: 'conteudo', label: 'Conteúdo', items: conteudo });

  return sections;
}

/** Rotas que ativam o item Editais no menu. */
export function isEditaisNavActive(pathname) {
  return pathname === '/editais' || pathname.startsWith('/edital/');
}

export function isDashboardNavActive(pathname) {
  return pathname === '/dashboard' || pathname === '/';
}

export function isNavItemActive(pathname, item) {
  if (!item?.to) return false;
  if (item.to === '/dashboard') return isDashboardNavActive(pathname);
  if (item.to === '/editais') return isEditaisNavActive(pathname);
  return pathname === item.to || pathname.startsWith(`${item.to}/`);
}
