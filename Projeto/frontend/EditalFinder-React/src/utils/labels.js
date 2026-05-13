/**
 * Rótulos amigáveis para valores vindos do backend (sem lógica de negócio pesada).
 */
import { humanizeTechnicalLabel } from './portaisDisplayLabels.js';

const VALIDACAO_MAP = {
  incompleto: 'Incompleto',
  valido: 'Válido',
  validado: 'Validado',
  suspeito: 'Suspeito',
  acesso_limitado: 'Acesso limitado',
};

/** Textos de badge na área Portais Estratégicos (produto). */
const VALIDACAO_BADGE_PORTAIS = {
  incompleto: 'Dados parciais',
  acesso_limitado: 'Acesso limitado',
  valido: 'Validado',
  validado: 'Validado',
  suspeito: 'Revisão',
};

const QUALIDADE_MAP = {
  alta: 'Alta',
  media: 'Média',
  baixa: 'Baixa',
  desconhecida: 'Desconhecida',
};

/** Taxonomia portal_tipo / Wave 1 (portal_estrategico). */
const PORTAL_TIPO_MAP = {
  hub: 'Hub',
  registration: 'Cadastro',
  procurement: 'Procurement',
  documentation: 'Documentação',
  supplier_resource: 'Recurso fornecedor',
  access_limited: 'Acesso limitado',
  investment: 'Investimento',
  funding_hub: 'Funding hub',
  market_access: 'Market access',
  internationalization: 'Internacionalização',
  development_agency: 'Desenvolvimento',
  credit_investment: 'Crédito / investimento',
  startup_program: 'Startup program',
  accelerator: 'Aceleradora',
  corporate_venture: 'Corporate venture',
  other: 'Outro',
};

/**
 * @param {string|null|undefined} raw
 * @returns {string}
 */
export function labelValidacaoStatus(raw) {
  if (raw == null || String(raw).trim() === '') return '—';
  const k = String(raw).trim().toLowerCase();
  return VALIDACAO_MAP[k] || raw;
}

/**
 * @param {string|null|undefined} raw
 * @returns {string}
 */
export function labelQualidadeDado(raw) {
  if (raw == null || String(raw).trim() === '') return '—';
  const k = String(raw).trim().toLowerCase();
  return QUALIDADE_MAP[k] || humanizeTechnicalLabel(raw);
}

/**
 * Rótulo para `portal_tipo` ou semântica Wave 1 (snake_case ou legado).
 * @param {string|null|undefined} raw
 * @returns {string}
 */
export function labelPortalTipo(raw) {
  if (raw == null || String(raw).trim() === '') return '—';
  const k = String(raw).trim().toLowerCase().replace(/\s+/g, '_');
  return PORTAL_TIPO_MAP[k] || humanizeTechnicalLabel(raw);
}

/**
 * Badge de validação para cards de portais (rótulos de produto).
 * @param {string|null|undefined} raw
 * @returns {string}
 */
export function labelPortaisValidacaoBadge(raw) {
  if (raw == null || String(raw).trim() === '') return '—';
  const k = String(raw).trim().toLowerCase();
  if (VALIDACAO_BADGE_PORTAIS[k]) return VALIDACAO_BADGE_PORTAIS[k];
  return labelValidacaoStatus(raw);
}

/**
 * Fallback extra para valores de validação não mapeados (snake_case do cluster).
 */
export function labelPortaisValidacaoDisplay(raw) {
  if (raw == null || String(raw).trim() === '') return '—';
  const k = String(raw).trim().toLowerCase();
  if (VALIDACAO_BADGE_PORTAIS[k]) return VALIDACAO_BADGE_PORTAIS[k];
  if (VALIDACAO_MAP[k]) return VALIDACAO_MAP[k];
  return humanizeTechnicalLabel(raw);
}
