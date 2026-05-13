/**
 * Humanização de valores técnicos (snake_case, slugs) para exibição em Portais Estratégicos.
 * Nunca logar ou expor dados sensíveis.
 */

/** Frases inteiras já acordadas (chave lowercase com underscores). */
const PHRASE_OVERRIDES = {
  lockheed_martin_suppliers: 'Lockheed Martin Suppliers',
  general_dynamics_suppliers: 'General Dynamics Suppliers',
  bae_systems_suppliers: 'BAE Systems Suppliers',
  defesa_industrial: 'Defesa industrial',
  market_access: 'Market access',
  funding_hub: 'Funding hub',
  access_limited: 'Acesso limitado',
  credit_investment: 'Crédito / investimento',
  internationalization: 'Internacionalização',
  development_agency: 'Agência / desenvolvimento',
  startup_program: 'Programa startups',
};

/** Palavras que devem ficar em maiúsculas conhecidas (siglas curtas ambíguas). */
const ACRONYM_WORDS = new Set([
  'bae',
  'gd',
  'emb',
  'eu',
  'br',
  'us',
  'uk',
]);

function titleWord(part) {
  if (!part) return '';
  const lower = part.toLowerCase();
  if (ACRONYM_WORDS.has(lower) && lower.length <= 5) return lower.toUpperCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

/**
 * Converte snake_case ou slugs curtos para texto legível.
 * Mantém valores que já parecem frases livres sem destroçar números nem URLs curtas misturadas.
 * @param {string|null|undefined} raw
 * @returns {string}
 */
export function humanizeTechnicalLabel(raw) {
  if (raw == null) return '—';
  const s = String(raw).trim();
  if (!s) return '—';

  const key = s.toLowerCase().replace(/\s+/g, '_').replace(/-+/g, '_');
  if (PHRASE_OVERRIDES[key]) return PHRASE_OVERRIDES[key];

  /** Já existe espaço ou hífen e poucos underscores — apenas capitalizar gentilmente. */
  const hasSentenceShape = /\s/.test(s) || (/-/.test(s) && key.split('_').length <= 1);
  if (hasSentenceShape && key.split('_').filter(Boolean).length <= 3 && !/_/g.exec(key)) {
    return s
      .split(/\s+/)
      .map((w) => {
        const wl = w.toLowerCase().replace(/^-+|-+$/g, '');
        if (!wl) return w;
        if (ACRONYM_WORDS.has(wl.replace(/\./g, ''))) return wl.replace(/\./g, '').toUpperCase();
        return wl.charAt(0).toUpperCase() + wl.slice(1);
      })
      .join(' ')
      .replace(/-/g, ' ');
  }

  const chunks = key.split('_').filter(Boolean);
  if (chunks.length === 0) return s;
  if (chunks.length === 1) return titleWord(chunks[0]);

  return chunks.map(titleWord).join(' ');
}

/**
 * Fonte / organização (slug técnico → legível).
 * @param {string|null|undefined} raw
 */
export function labelFontePortal(raw) {
  return humanizeTechnicalLabel(raw);
}

/**
 * Categoria ou frontend_section.
 * @param {string|null|undefined} cat
 * @param {string|null|undefined} section
 */
export function labelCategoriaPortal(cat, section) {
  const c = (cat || section || '').trim();
  return humanizeTechnicalLabel(c);
}

/**
 * Setores estratégicos (lista ou valor único) humanizados.
 * @param {unknown} setorCampo — array ou string
 */
export function formatSetoresPortalDisplay(setorCampo) {
  if (setorCampo == null) return '—';
  const arr = Array.isArray(setorCampo)
    ? setorCampo.filter((x) => x != null && String(x).trim() !== '')
    : [setorCampo];
  if (arr.length === 0) return '—';
  const uniq = [...new Set(arr.map((x) => String(x).trim()))];
  uniq.sort((a, b) => a.localeCompare(b, 'pt-BR'));
  return uniq.map(humanizeTechnicalLabel).join(', ');
}

/**
 * Dropdown de validação: texto amigável (mesma família das badges quando possível).
 * @param {string|null|undefined} raw
 */
export function labelValidacaoPortalSelect(raw) {
  if (!raw || !String(raw).trim()) return '—';
  const k = String(raw).trim().toLowerCase();
  const MAP = {
    incompleto: 'Dados parciais',
    acesso_limitado: 'Acesso limitado',
    valido: 'Validado',
    validado: 'Validado',
    suspeito: 'Revisão',
  };
  return MAP[k] || humanizeTechnicalLabel(raw);
}

/**
 * Qualidade: mapas conhecidos + fallback humanizado.
 * @param {string|null|undefined} raw
 */
export function labelQualidadePortalDisplay(raw, labelQualidadeDadoFn) {
  const mapped = labelQualidadeDadoFn ? labelQualidadeDadoFn(raw) : null;
  if (mapped && mapped !== '—' && mapped !== '') return mapped;
  return humanizeTechnicalLabel(raw);
}
