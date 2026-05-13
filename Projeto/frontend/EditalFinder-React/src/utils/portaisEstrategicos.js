/**
 * Helpers para linhas de portais estratégicos (views vw_* / portal_estrategico).
 */
import { labelPortalTipo } from './labels';

/** Chave técnica do tipo para estilização (prioriza Wave 1). */
export function getPortalTipoSemanticKey(row) {
  const ex = parseExtras(row?.extras);
  const w = String(ex.portal_tipo_wave1 || '').trim().toLowerCase();
  if (w) return w.replace(/\s+/g, '_');
  const p = String(row?.portal_tipo || '').trim().toLowerCase();
  return p.replace(/\s+/g, '_');
}

export function parseExtras(extras) {
  if (extras == null) return {};
  if (typeof extras === 'object' && !Array.isArray(extras)) return extras;
  if (typeof extras === 'string') {
    try {
      const j = JSON.parse(extras);
      return j && typeof j === 'object' ? j : {};
    } catch {
      return {};
    }
  }
  return {};
}

/** Rótulo de tipo: prioriza extras.portal_tipo_wave1, senão portal_tipo. */
export function getPortalTipoDisplay(row) {
  const ex = parseExtras(row?.extras);
  const wave = ex.portal_tipo_wave1;
  if (wave != null && String(wave).trim() !== '') {
    return labelPortalTipo(String(wave).trim());
  }
  return labelPortalTipo(row?.portal_tipo);
}

/** Data para ordenação “mais recentes”. */
export function getPortalUpdatedAt(row) {
  const t =
    row?.updated_at ||
    row?.atualizado_em ||
    row?.criado_em ||
    row?.data_publicacao ||
    '';
  return t ? new Date(String(t)).getTime() : 0;
}

export function isPortalInactive(row) {
  return row?.ativo === false;
}

export function isHubOrDocTipo(row) {
  const ex = parseExtras(row?.extras);
  const w = String(ex.portal_tipo_wave1 || '').toLowerCase();
  const p = String(row?.portal_tipo || '').toLowerCase();
  const blob = `${w} ${p}`;
  return (
    /hub|documentation|supplier|procurement|funding|documentacao|recurso/.test(blob) ||
    ['hub', 'documentation', 'supplier_resource', 'procurement', 'funding_hub'].includes(p)
  );
}

export function isAcessoLimitadoRow(row) {
  const vs = String(row?.validacao_status || '').toLowerCase();
  const at = String(row?.acesso_tipo || '').toLowerCase();
  return vs === 'acesso_limitado' || at === 'acesso_limitado';
}

export function pickPortalResumo(row) {
  const r = (row?.resumo || '').trim();
  if (r) return r;
  const d = (row?.descricao || '').trim();
  if (d) return d.length > 280 ? `${d.slice(0, 277)}…` : d;
  return 'Portal estratégico cadastrado para consulta.';
}
