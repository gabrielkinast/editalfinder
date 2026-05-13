import { getClientTheme } from '../../utils/precadastro/clientTheme';

/** Realce dourado/ambar suave para badges (sob fundo claro) */
const DEFAULT_GOLD = [180, 138, 42];

/**
 * Cores numeradas para jsPDF + identidade do cliente.
 */
export function getPdfDocumentTheme(cliente) {
  const base = getClientTheme(cliente);
  return {
    ...base,
    primaryColor: base.primaryRgb,
    secondaryColor: base.secondaryRgb,
    accentColor: base.secondaryRgb,
    textColor: [15, 23, 42],
    mutedTextColor: [100, 116, 139],
    borderColor: [226, 232, 240],
    surfaceColor: [248, 250, 252],
    highlightGoldRgb: DEFAULT_GOLD,
    logoUrl: base.logoUrl,
    logoDataUrl: base.logoDataUrl,
  };
}
