import { getPermissions, PERMISSIONS } from '../permissions.js';

/** id do dono na linha `cliente` (PostgREST / normalizado). */
export function clientOwnerUserId(client) {
  if (!client || typeof client !== 'object') return null;
  const raw = client.id_usuario ?? client.idUsuario ?? client.usuario_id;
  if (raw == null || raw === '') return null;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : null;
}

/** id do utilizador na sessão (`authService` / AuthContext). */
export function sessionUserId(user) {
  if (!user || user.id_usuario == null || user.id_usuario === '') return null;
  const n = Number(user.id_usuario);
  return Number.isFinite(n) && n > 0 ? n : null;
}

/**
 * Administrador: `tipo_usuario` / `tipo` === "Administrador" (ou variantes)
 * ou nível de acesso mapeado para {@link PERMISSIONS.ADMIN} (nível 1).
 */
export function isAdminUser(user) {
  if (!user) return false;
  const tipo = String(user.tipo ?? user.tipo_usuario ?? '').trim();
  const tUp = tipo.toUpperCase();
  if (tUp === 'ADMINISTRADOR' || tUp === 'ADMIN') return true;
  const nivel = user.nivel ?? user.nivel_acesso;
  if (nivel != null && nivel !== '') {
    const p = getPermissions(typeof nivel === 'number' ? nivel : Number(nivel));
    if (p?.level === PERMISSIONS.ADMIN.level) return true;
  }
  const pByTipo = getPermissions(tipo || 'FUNCIONARIO');
  return pByTipo?.level === PERMISSIONS.ADMIN.level;
}

/** Utilizador comum / consultor: só clientes com mesmo `id_usuario`; linhas sem dono ficam invisíveis. */
export function canViewClient(user, client) {
  if (!client) return false;
  if (isAdminUser(user)) return true;
  const sid = sessionUserId(user);
  if (sid == null) return false;
  const oid = clientOwnerUserId(client);
  if (oid == null) return false;
  return oid === sid;
}

export function canEditClient(user, client) {
  return canViewClient(user, client);
}

/**
 * Garante `id_usuario` no insert de cliente (dono = utilizador atual quando o id existir na sessão).
 */
export function attachOwnerToClientPayload(user, payload) {
  const base = payload && typeof payload === 'object' ? { ...payload } : {};
  const sid = sessionUserId(user);
  if (sid != null) base.id_usuario = sid;
  return base;
}

/**
 * Remove `id_usuario` do payload para não-admin (não pode reatribuir dono pelo formulário).
 * Administrador mantém o payload (pode preservar dono existente ao editar).
 */
export function sanitizeClientWritePayload(user, payload) {
  if (!payload || typeof payload !== 'object') return payload;
  const out = { ...payload };
  if (!isAdminUser(user)) delete out.id_usuario;
  return out;
}

/** Filtro defensivo após `select` (ex.: cache ou rotas sem filtro server-side). */
export function filterClientsForUser(user, clients) {
  if (!Array.isArray(clients)) return [];
  if (isAdminUser(user)) return clients;
  return clients.filter((c) => canViewClient(user, c));
}
