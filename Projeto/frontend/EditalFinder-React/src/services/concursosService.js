/**
 * Concursos & Seleções — leitura via views públicas (chave anon, RLS).
 * Não usar service_role.
 */
import { supabase, isSupabaseConfigured } from './supabaseClient';
import { VIEW_CONCURSOS, VIEW_VESTIBULARES } from '../config/env';

const PAGE_SIZE = 800;

const ORDER_FALLBACKS = [
  ['atualizado_em', false],
  ['id_concurso', false],
  ['criado_em', false],
];

/**
 * @param {Record<string, unknown>} row
 * @returns {Record<string, unknown>}
 */
export function normalizeConcursoRow(row) {
  if (!row || typeof row !== 'object') return row;
  return {
    ...row,
    inscricoes_abertas: Boolean(row.inscricoes_abertas),
    prova_proxima: Boolean(row.prova_proxima),
    dias_ate_fim_inscricao:
      row.dias_ate_fim_inscricao != null && row.dias_ate_fim_inscricao !== ''
        ? Number(row.dias_ate_fim_inscricao)
        : null,
    dias_ate_prova:
      row.dias_ate_prova != null && row.dias_ate_prova !== ''
        ? Number(row.dias_ate_prova)
        : null,
  };
}

async function fetchAllFromView(viewName) {
  if (!isSupabaseConfigured || !viewName) return [];

  let lastErr;
  for (const [orderCol, ascending] of ORDER_FALLBACKS) {
    const all = [];
    let from = 0;
    try {
      for (;;) {
        const { data, error } = await supabase
          .from(viewName)
          .select('*')
          .order(orderCol, { ascending, nullsFirst: false })
          .range(from, from + PAGE_SIZE - 1);

        if (error) throw error;
        if (!data?.length) break;
        all.push(...data);
        if (data.length < PAGE_SIZE) break;
        from += PAGE_SIZE;
      }
      return all;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error(`fetch ${viewName}`);
}

/** Lista completa da view principal (cards + filtros). */
export async function fetchConcursos() {
  const raw = await fetchAllFromView(VIEW_CONCURSOS);
  return (raw || []).map(normalizeConcursoRow);
}

/** Subconjunto vestibular/ingresso (view dedicada). */
export async function fetchVestibulares() {
  const raw = await fetchAllFromView(VIEW_VESTIBULARES);
  return (raw || []).map(normalizeConcursoRow);
}
