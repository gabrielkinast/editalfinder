import { supabase, isSupabaseConfigured } from './supabaseClient';
import {
  VIEW_EDITAIS_FAVORITOS,
  TABLE_EDITAL_FAVORITO,
  FEATURE_EDITAL_FAVORITOS,
} from '../config/env';
import { getDeadlineAlertStatus, parsePrazoEnvio } from '../utils/deadlineAlerts';

function warnSafe(msg, err) {
  const code = err?.code || err?.message || String(err);
  console.warn(`[favoritosService] ${msg}`, code);
}

function logFavoritosSupabaseError(scope, err) {
  warnSafe(scope, err);
  if (!import.meta.env.DEV || !err || typeof err !== 'object') return;
  console.error(`[favoritosService] ${scope}`, {
    message: err.message,
    code: err.code,
    details: err.details,
    hint: err.hint,
  });
}

export function normalizeEditalLink(edital) {
  const raw =
    edital?.linkOriginal ??
    edital?.link_raw ??
    edital?.link ??
    edital?.link_inscricao ??
    edital?.edital_link ??
    null;
  if (raw == null || raw === '') return null;
  const s = String(raw).trim();
  if (!s) return null;
  try {
    const u = new URL(s);
    return u.href;
  } catch {
    return s;
  }
}

/** Comparação tolerante (view vs card): host/path minúsculos, sem barra final, sem hash. */
export function canonicalizeLinkForMatch(href) {
  if (href == null || href === '') return null;
  const s = String(href).trim();
  if (!s) return null;
  const withProto = /^https?:\/\//i.test(s) ? s : `https://${s}`;
  try {
    const u = new URL(withProto);
    u.hash = '';
    const path = (u.pathname || '/').replace(/\/+$/, '') || '/';
    const host = (u.hostname || '').toLowerCase();
    return `${u.protocol}//${host}${path === '/' ? '/' : path}${u.search}`;
  } catch {
    return s.toLowerCase();
  }
}

export function getEditalNumericoId(edital) {
  if (!edital) return null;
  if (edital.idNumerico != null && Number.isFinite(Number(edital.idNumerico))) {
    return Number(edital.idNumerico);
  }
  if (edital.id_edital != null && Number.isFinite(Number(edital.id_edital))) {
    return Number(edital.id_edital);
  }
  const idStr = String(edital.id ?? '').replace(/^manual-/, '');
  const n = Number(idStr);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function rowIdEdital(row) {
  if (!row) return null;
  const v = row.id_edital ?? row.idEdital ?? row.edital_id ?? row.id_edital_fk;
  if (v == null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function rowLinkRaw(row) {
  if (!row) return null;
  return row.edital_link ?? row.link_edital ?? row.link ?? row.link_original ?? null;
}

export function favoritoRowMatchesEdital(row, edital) {
  if (!row || !edital) return false;
  const rid = rowIdEdital(row);
  const eid = getEditalNumericoId(edital);
  if (rid != null && eid != null && rid === eid) return true;
  const rl = canonicalizeLinkForMatch(rowLinkRaw(row));
  const el = canonicalizeLinkForMatch(normalizeEditalLink(edital));
  if (rl && el && rl === el) return true;
  return false;
}

function isFavoritosEnabled() {
  return FEATURE_EDITAL_FAVORITOS && isSupabaseConfigured;
}

export async function fetchFavoritos(options = {}) {
  if (!isFavoritosEnabled()) return [];
  const idUsuario = getIdUsuario(options);
  if (idUsuario == null) {
    return [];
  }
  try {
    const { data, error } = await supabase
      .from(VIEW_EDITAIS_FAVORITOS)
      .select('*')
      .eq('id_usuario', idUsuario)
      .order('id_favorito', { ascending: false });

    if (error) {
      logFavoritosSupabaseError('fetchFavoritos', error);
      throw error;
    }
    const rows = Array.isArray(data) ? data : [];
    return rows.filter((r) => r && r.ativo !== false);
  } catch (e) {
    warnSafe('fetchFavoritos', e);
    throw e;
  }
}

/** Sem fallback numérico: o hook deve passar o utilizador autenticado (ou override explícito). */
function getIdUsuario(options = {}) {
  const v = options.id_usuario ?? options.userId;
  if (v == null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function favoritoPkFromRow(row) {
  if (!row) return null;
  return row.id_favorito ?? row.idFavorito ?? row.favorito_id ?? null;
}

function buildInsertPayload(edital, options = {}) {
  const idUsuario = getIdUsuario(options);
  const idEdital = getEditalNumericoId(edital);
  const edital_link = normalizeEditalLink(edital);
  const prazoRaw = parsePrazoEnvio(edital);
  const status_prazo = getDeadlineAlertStatus(edital);
  const contexto = options.contexto === 'radar' ? 'radar' : 'editais';

  const payload = {
    id_usuario: idUsuario,
    id_edital: idEdital,
    edital_link: edital_link || null,
    edital_titulo: edital.titulo ?? edital.titulo_original_raw ?? null,
    edital_fonte: edital.fonte_recurso ?? edital.fonte ?? edital.orgao ?? null,
    prazo_envio: prazoRaw || null,
    status_prazo,
    alerta_ativo: options.alerta_ativo !== false,
    alertar_com_dias: options.alertar_com_dias ?? 7,
    origem: 'frontend',
    contexto,
    ativo: true,
    visualizado: false,
    observacao: options.observacao ?? null,
  };
  const ex = {
    favorited_from: contexto,
    client_side_created: true,
    ...(options.extras && typeof options.extras === 'object' ? options.extras : {}),
  };
  payload.extras = ex;
  return payload;
}

/**
 * Linha em public.edital_favorito (inclui ativo=false). A view de leitura só expõe ativos.
 */
async function findExistingFavoritoRowInTable(edital, options = {}) {
  if (!isFavoritosEnabled() || !edital) return null;
  const idUsuario = getIdUsuario(options);
  if (idUsuario == null) return null;
  const idEdital = getEditalNumericoId(edital);

  try {
    if (idEdital != null) {
      const { data, error } = await supabase
        .from(TABLE_EDITAL_FAVORITO)
        .select('*')
        .eq('id_usuario', idUsuario)
        .eq('id_edital', idEdital)
        .order('id_favorito', { ascending: false })
        .limit(1);
      if (error) logFavoritosSupabaseError('findExistingFavoritoRowInTable id_edital', error);
      else if (data?.[0]) return data[0];
    }

    const linkNorm = normalizeEditalLink(edital);
    if (linkNorm) {
      const { data, error } = await supabase
        .from(TABLE_EDITAL_FAVORITO)
        .select('*')
        .eq('id_usuario', idUsuario)
        .eq('edital_link', linkNorm)
        .order('id_favorito', { ascending: false })
        .limit(1);
      if (error) logFavoritosSupabaseError('findExistingFavoritoRowInTable edital_link', error);
      else if (data?.[0]) return data[0];
    }

    const { data: candidates, error: e2 } = await supabase
      .from(TABLE_EDITAL_FAVORITO)
      .select('*')
      .eq('id_usuario', idUsuario)
      .order('id_favorito', { ascending: false })
      .limit(120);
    if (e2) {
      logFavoritosSupabaseError('findExistingFavoritoRowInTable scan', e2);
      return null;
    }
    const hit = (candidates || []).find((r) => favoritoRowMatchesEdital(r, edital));
    return hit || null;
  } catch (e) {
    warnSafe('findExistingFavoritoRowInTable', e);
    return null;
  }
}

function buildReactivatePatch(edital, options = {}, existingRow = null) {
  const prazoRaw = parsePrazoEnvio(edital);
  const status_prazo = getDeadlineAlertStatus(edital);
  const contexto = options.contexto === 'radar' ? 'radar' : 'editais';
  const link = normalizeEditalLink(edital);
  const newExtras = {
    favorited_from: contexto,
    client_side_reactivated: true,
    ...(options.extras && typeof options.extras === 'object' ? options.extras : {}),
  };
  let mergedExtras = newExtras;
  const prev = existingRow?.extras;
  if (prev != null && typeof prev === 'object' && !Array.isArray(prev)) {
    mergedExtras = { ...prev, ...newExtras };
  } else if (typeof prev === 'string') {
    try {
      const parsed = JSON.parse(prev);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) mergedExtras = { ...parsed, ...newExtras };
    } catch {
      mergedExtras = newExtras;
    }
  }

  const idEdital = getEditalNumericoId(edital);
  const patch = {
    ativo: true,
    alerta_ativo: options.alerta_ativo !== false,
    alertar_com_dias: options.alertar_com_dias ?? 7,
    visualizado: false,
    prazo_envio: prazoRaw || null,
    status_prazo,
    edital_titulo: edital.titulo ?? edital.titulo_original_raw ?? null,
    edital_fonte: edital.fonte_recurso ?? edital.fonte ?? edital.orgao ?? null,
    contexto,
    origem: 'frontend',
    edital_link: link || rowLinkRaw(existingRow) || null,
    observacao: options.observacao != null ? options.observacao : existingRow?.observacao ?? null,
    extras: mergedExtras,
  };
  if (idEdital != null) patch.id_edital = idEdital;
  return patch;
}

async function reactivateFavoritoRow(existingRow, edital, options = {}) {
  const idF = favoritoPkFromRow(existingRow);
  if (idF == null) {
    warnSafe('reactivateFavoritoRow', new Error('missing_id_favorito'));
    return { ok: false, error: 'missing_id_favorito' };
  }
  const idUsuario = getIdUsuario(options);
  try {
    const patch = buildReactivatePatch(edital, options, existingRow);
    let q = supabase.from(TABLE_EDITAL_FAVORITO).update(patch).eq('id_favorito', idF);
    if (idUsuario != null) q = q.eq('id_usuario', idUsuario);
    const { data, error } = await q.select('id_favorito').limit(1);

    if (error) {
      logFavoritosSupabaseError('reactivateFavoritoRow', error);
      return { ok: false, error };
    }
    return { ok: true, data: data?.[0] ?? { id_favorito: idF }, reactivated: true };
  } catch (e) {
    warnSafe('reactivateFavoritoRow', e);
    return { ok: false, error: e };
  }
}

export async function addFavorito(edital, options = {}) {
  if (!isFavoritosEnabled() || !edital) return { ok: false, error: 'disabled' };
  try {
    if (getIdUsuario(options) == null) {
      warnSafe('addFavorito', new Error('missing_id_usuario'));
      return { ok: false, error: { message: 'missing_id_usuario', code: 'MISSING_USER' } };
    }
    const payloadPreview = buildInsertPayload(edital, options);
    if (!payloadPreview.id_edital && !payloadPreview.edital_link) {
      warnSafe('addFavorito', new Error('missing_id_and_link'));
      return { ok: false, error: 'missing_id_and_link' };
    }

    const existing = await findExistingFavoritoRowInTable(edital, options);
    if (existing) {
      return reactivateFavoritoRow(existing, edital, options);
    }

    const payload = buildInsertPayload(edital, options);
    const { data, error } = await supabase.from(TABLE_EDITAL_FAVORITO).insert([payload]).select('id_favorito');

    if (error?.code === '23505') {
      const row = await findExistingFavoritoRowInTable(edital, options);
      if (row) {
        const r = await reactivateFavoritoRow(row, edital, options);
        if (r.ok) return { ...r, recoveredFromDuplicate: true };
      }
      logFavoritosSupabaseError('addFavorito duplicate key unresolved', error);
      return { ok: false, error };
    }

    if (error) {
      logFavoritosSupabaseError('addFavorito', error);
      return { ok: false, error };
    }
    return { ok: true, data: data?.[0] ?? null };
  } catch (e) {
    warnSafe('addFavorito', e);
    return { ok: false, error: e };
  }
}

export async function removeFavorito(favoritoOrEdital, options = {}) {
  if (!isFavoritosEnabled()) return { ok: false, error: 'disabled' };
  const idFavorito =
    favoritoOrEdital?.id_favorito ??
    favoritoOrEdital?.idFavorito ??
    favoritoOrEdital?.favorito_id ??
    favoritoOrEdital?.id_favorito_pk ??
    null;
  if (idFavorito == null) {
    warnSafe('removeFavorito', new Error('missing_id_favorito'));
    return { ok: false, error: 'missing_id_favorito' };
  }
  const idUsuario = getIdUsuario(options);
  try {
    const patch = { ativo: false };
    let q = supabase.from(TABLE_EDITAL_FAVORITO).update(patch).eq('id_favorito', idFavorito);
    if (idUsuario != null) q = q.eq('id_usuario', idUsuario);
    const { error } = await q;

    if (error) {
      logFavoritosSupabaseError('removeFavorito', error);
      return { ok: false, error };
    }
    return { ok: true };
  } catch (e) {
    warnSafe('removeFavorito', e);
    return { ok: false, error: e };
  }
}

function findActiveFavoritoRow(favorites, edital) {
  const list = Array.isArray(favorites) ? favorites : [];
  return list.find((r) => r && r.ativo !== false && favoritoRowMatchesEdital(r, edital)) || null;
}

export async function toggleFavorito(edital, favorites, options = {}) {
  if (!isFavoritosEnabled() || !edital) return { ok: false, error: 'disabled' };
  if (import.meta.env.DEV) {
    const { data: sessWrap } = await supabase.auth.getSession();
    if (!sessWrap?.session?.access_token) {
      console.warn(
        '[favoritosService.toggleFavorito] Sem access_token na sessão; RLS ou PostgREST podem falhar ao gravar favorito.',
      );
    }
  }
  const existing = findActiveFavoritoRow(favorites, edital);
  if (existing) {
    return removeFavorito(existing, options);
  }
  return addFavorito(edital, options);
}

export async function markFavoritoVisualizado(id_favorito) {
  if (!isFavoritosEnabled() || id_favorito == null) return { ok: false };
  try {
    const { error } = await supabase
      .from(TABLE_EDITAL_FAVORITO)
      .update({
        visualizado: true,
        visualizado_em: new Date().toISOString(),
        atualizado_em: new Date().toISOString(),
      })
      .eq('id_favorito', id_favorito);

    if (error) warnSafe('markFavoritoVisualizado', error);
    return { ok: !error, error };
  } catch (e) {
    warnSafe('markFavoritoVisualizado', e);
    return { ok: false, error: e };
  }
}

export async function updateFavoritoAlerta(id_favorito, payload = {}) {
  if (!isFavoritosEnabled() || id_favorito == null) return { ok: false };
  try {
    const patch = {
      ...payload,
      atualizado_em: new Date().toISOString(),
    };
    const { error } = await supabase.from(TABLE_EDITAL_FAVORITO).update(patch).eq('id_favorito', id_favorito);
    if (error) warnSafe('updateFavoritoAlerta', error);
    return { ok: !error, error };
  } catch (e) {
    warnSafe('updateFavoritoAlerta', e);
    return { ok: false, error: e };
  }
}

