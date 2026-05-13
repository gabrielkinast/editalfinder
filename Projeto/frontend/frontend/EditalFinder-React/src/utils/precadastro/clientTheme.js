/**
 * Tema visual opcional por cliente (UI + PDF).
 * Campos reconhecidos no objeto cliente: cor_primaria, cor_secundaria, logo_url (ou logoUrl), logo_data_url.
 */

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

function hexToRgb(hex) {
  if (!hex || typeof hex !== 'string') return null;
  let h = hex.replace('#', '').trim();
  if (h.length === 3) {
    h = h
      .split('')
      .map((c) => c + c)
      .join('');
  }
  if (h.length !== 6) return null;
  const n = parseInt(h, 16);
  if (Number.isNaN(n)) return null;
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/** Luminância relativa (0–1) para escolher texto sobre fundo colorido */
function luminance([r, g, b]) {
  const s = (v) => {
    const x = v / 255;
    return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * s(r) + 0.7152 * s(g) + 0.0722 * s(b);
}

/**
 * @param {Record<string, unknown> | null | undefined} cliente
 * @returns {{
 *   primary: string;
 *   secondary: string;
 *   accent: string;
 *   textOnPrimary: string;
 *   textOnSecondary: string;
 *   primaryRgb: [number, number, number];
 *   secondaryRgb: [number, number, number];
 *   logoUrl: string | null;
 *   logoDataUrl: string | null;
 * }}
 */
export function getClientTheme(cliente) {
  const fallbackPrimary = '#1e3a5f';
  const fallbackSecondary = '#0f766e';

  const rawP = cliente?.cor_primaria || cliente?.cor_primary || cliente?.cor_prim;
  const rawS = cliente?.cor_secundaria || cliente?.cor_secondary || cliente?.cor_sec;

  const primary = typeof rawP === 'string' && rawP.trim() ? rawP.trim() : fallbackPrimary;
  const secondary = typeof rawS === 'string' && rawS.trim() ? rawS.trim() : fallbackSecondary;

  let primaryRgb = hexToRgb(primary.startsWith('#') ? primary : `#${primary}`);
  if (!primaryRgb) primaryRgb = hexToRgb(fallbackPrimary);

  let secondaryRgb = hexToRgb(secondary.startsWith('#') ? secondary : `#${secondary}`);
  if (!secondaryRgb) secondaryRgb = hexToRgb(fallbackSecondary);

  const onPrimary = luminance(primaryRgb) > 0.45 ? '#0f172a' : '#ffffff';
  const onSecondary = luminance(secondaryRgb) > 0.45 ? '#0f172a' : '#ffffff';

  const accentRgb = [
    clamp(Math.round((primaryRgb[0] + secondaryRgb[0]) / 2), 0, 255),
    clamp(Math.round((primaryRgb[1] + secondaryRgb[1]) / 2), 0, 255),
    clamp(Math.round((primaryRgb[2] + secondaryRgb[2]) / 2), 0, 255),
  ];

  const logoUrl =
    (typeof cliente?.logo_url === 'string' && cliente.logo_url.trim()) ||
    (typeof cliente?.logoUrl === 'string' && cliente.logoUrl.trim()) ||
    null;

  const logoDataUrl =
    (typeof cliente?.logo_data_url === 'string' && cliente.logo_data_url.trim()) ||
    (typeof cliente?.logoDataUrl === 'string' && cliente.logoDataUrl.trim()) ||
    null;

  return {
    primary,
    secondary,
    accent: `rgb(${accentRgb.join(',')})`,
    textOnPrimary: onPrimary,
    textOnSecondary: onSecondary,
    primaryRgb,
    secondaryRgb,
    logoUrl,
    logoDataUrl,
  };
}

/**
 * Estilos React inline/CSS variables para o shell do pré-cadastro
 */
export function themeToCssVars(theme) {
  return {
    '--precad-primary': theme.primary,
    '--precad-secondary': theme.secondary,
    '--precad-accent': theme.accent,
    '--precad-on-primary': theme.textOnPrimary,
    '--precad-on-secondary': theme.textOnSecondary,
  };
}
