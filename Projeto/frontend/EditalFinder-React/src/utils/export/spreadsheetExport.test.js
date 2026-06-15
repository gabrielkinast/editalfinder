import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, it } from 'node:test';
import {
  sanitizeSpreadsheetCell,
  sanitizeExportRows,
  MAX_SPREADSHEET_CELL_LENGTH,
} from './spreadsheetExport.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

describe('sanitizeSpreadsheetCell', () => {
  it('prefixa =cmd contra formula injection', () => {
    assert.equal(sanitizeSpreadsheetCell('=cmd'), "'=cmd");
  });

  it('prefixa +SUM(...) contra formula injection', () => {
    assert.equal(sanitizeSpreadsheetCell('+SUM(1)'), "'+SUM(1)");
  });

  it('mantém número real -10', () => {
    assert.equal(sanitizeSpreadsheetCell(-10), -10);
  });

  it('protege string textual -10', () => {
    assert.equal(sanitizeSpreadsheetCell('-10'), "'-10");
  });

  it('prefixa @abc', () => {
    assert.equal(sanitizeSpreadsheetCell('@abc'), "'@abc");
  });

  it('strings normais não mudam', () => {
    assert.equal(sanitizeSpreadsheetCell('Edital FAPESP 2026'), 'Edital FAPESP 2026');
  });

  it('null e undefined viram vazio', () => {
    assert.equal(sanitizeSpreadsheetCell(null), '');
    assert.equal(sanitizeSpreadsheetCell(undefined), '');
  });

  it('trunca células muito grandes', () => {
    const long = 'a'.repeat(MAX_SPREADSHEET_CELL_LENGTH + 100);
    assert.equal(sanitizeSpreadsheetCell(long).length, MAX_SPREADSHEET_CELL_LENGTH);
  });
});

describe('sanitizeExportRows', () => {
  it('preserva ordem e nomes das colunas', () => {
    const rows = [
      { Título: 'A', Status: 'Aberto', 'Status Detalhado': 'Det A', Fonte: 'CNPq' },
      { Título: 'B', Status: 'Encerrado', 'Status Detalhado': 'Det B', Fonte: 'FAPESP' },
    ];
    const columns = ['Título', 'Status', 'Status Detalhado', 'Fonte'];
    const out = sanitizeExportRows(rows, columns);

    assert.equal(out.length, 2);
    assert.deepEqual(Object.keys(out[0]), columns);
    assert.equal(out[0].Status, 'Aberto');
    assert.equal(out[0]['Status Detalhado'], 'Det A');
    assert.equal(out[1].Fonte, 'FAPESP');
  });

  it('sanitiza fórmulas nas células exportadas', () => {
    const out = sanitizeExportRows([{ link: '=HYPERLINK("evil")' }], ['link']);
    assert.equal(out[0].link, "'=HYPERLINK(\"evil\")");
  });
});

describe('spreadsheetExport module', () => {
  it('não importa pacote xlsx', () => {
    const src = readFileSync(resolve(__dirname, 'spreadsheetExport.js'), 'utf8');
    assert.ok(
      !/from\s+['"]xlsx['"]|import\s*\(\s*['"]xlsx['"]\)/.test(src),
      'spreadsheetExport não deve importar o pacote xlsx',
    );
    assert.ok(src.includes('exceljs'), 'deve usar exceljs');
  });
});
