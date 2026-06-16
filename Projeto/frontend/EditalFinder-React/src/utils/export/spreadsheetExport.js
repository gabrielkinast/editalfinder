/**
 * SECURITY 1.2 — Exportação de planilhas via ExcelJS (substitui SheetJS legado).
 * Geração apenas (write); sem parse de arquivos de usuário.
 */

/** Limite prático de caracteres por célula (Excel ~32767). */
export const MAX_SPREADSHEET_CELL_LENGTH = 32_000;

const FORMULA_INJECTION_PREFIX = /^[=+\-@]/;
const CONTROL_CHARS_RE = /[\x00-\x08\x0B\x0C\x0E-\x1F]/g;

/**
 * Mitiga formula injection em células de texto.
 * Números reais permanecem numéricos (ex.: -10).
 * @param {unknown} value
 * @returns {string|number|boolean|Date}
 */
export function sanitizeSpreadsheetCell(value) {
  if (value == null) return '';
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : '';
  }
  if (typeof value === 'boolean') return value;
  if (value instanceof Date) return value;

  let text = String(value).replace(CONTROL_CHARS_RE, '');
  if (text.length > MAX_SPREADSHEET_CELL_LENGTH) {
    text = text.slice(0, MAX_SPREADSHEET_CELL_LENGTH);
  }
  if (FORMULA_INJECTION_PREFIX.test(text)) {
    return `'${text}`;
  }
  return text;
}

/**
 * Sanitiza todas as células de linhas objeto-a-objeto.
 * Preserva chaves/colunas na ordem do primeiro objeto.
 * @param {Record<string, unknown>[]} rows
 * @param {string[]} [columnOrder]
 * @returns {Record<string, unknown>[]}
 */
export function sanitizeExportRows(rows, columnOrder) {
  if (!Array.isArray(rows) || rows.length === 0) return [];

  const columns =
    columnOrder?.length > 0
      ? columnOrder
      : Object.keys(rows[0] || {});

  return rows.map((row) => {
    const out = {};
    for (const col of columns) {
      out[col] = sanitizeSpreadsheetCell(row?.[col]);
    }
    return out;
  });
}

/**
 * Dispara download de `.xlsx` no browser.
 * @param {Record<string, unknown>[]} rows
 * @param {{
 *   fileName?: string,
 *   sheetName?: string,
 *   columns?: string[],
 *   columnWidth?: number,
 * }} [options]
 */
export async function exportRowsToXlsx(rows, options = {}) {
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error('Nenhuma linha para exportar.');
  }

  const columns =
    options.columns?.length > 0
      ? options.columns
      : Object.keys(rows[0] || {});

  const sanitized = sanitizeExportRows(rows, columns);
  const ExcelJS = (await import('exceljs')).default;

  const workbook = new ExcelJS.Workbook();
  const sheetName = String(options.sheetName || 'Sheet1').slice(0, 31);
  const worksheet = workbook.addWorksheet(sheetName);

  worksheet.columns = columns.map((key) => ({
    header: key,
    key,
    width: options.columnWidth ?? 18,
  }));

  for (const row of sanitized) {
    worksheet.addRow(row);
  }

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });

  const fileName = String(options.fileName || 'export.xlsx').replace(/[/\\?%*:|"<>]/g, '_');
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = fileName.endsWith('.xlsx') ? fileName : `${fileName}.xlsx`;
  anchor.click();
  URL.revokeObjectURL(url);
}
