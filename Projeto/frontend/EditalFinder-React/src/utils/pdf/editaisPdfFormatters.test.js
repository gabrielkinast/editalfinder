import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  safeText,
  truncateForPdf,
  formatLocationForPdf,
  formatPrazoForPdf,
  formatAreaForPdf,
  formatStatusForPdf,
  buildEditaisPdfRows,
  buildEditaisPdfColumns,
  buildPdfFiltersSummary,
} from './editaisPdfFormatters.js';

describe('safeText', () => {
  it('null retorna -', () => {
    assert.equal(safeText(null), '-');
  });

  it('array vira string curta', () => {
    assert.equal(safeText(['Tecnologia', 'Inovação']), 'Tecnologia, Inovação');
  });

  it('objeto não vira [object Object]', () => {
    assert.equal(safeText({}), '-');
  });
});

describe('truncateForPdf', () => {
  it('trunca texto longo', () => {
    const long = 'a'.repeat(120);
    const out = truncateForPdf(long, 40);
    assert.ok(out.length < 120);
    assert.match(out, /…$/);
  });
});

describe('formatLocationForPdf', () => {
  it('monta RS / Brasil', () => {
    assert.equal(formatLocationForPdf({ uf_raw: 'RS', pais_raw: 'Brasil' }), 'RS / Brasil');
  });

  it('fallback - sem local', () => {
    assert.equal(formatLocationForPdf({}), '-');
  });
});

describe('formatPrazoForPdf', () => {
  it('formata data ISO', () => {
    const out = formatPrazoForPdf({ prazo_envio_raw: '2026-12-31' });
    assert.match(out, /\d{2}\/\d{2}\/\d{4}/);
  });

  it('sem prazo', () => {
    assert.equal(formatPrazoForPdf({}), 'Sem prazo');
  });
});

describe('formatAreaForPdf', () => {
  it('junta arrays de área', () => {
    const out = formatAreaForPdf({ area_tecnologica_raw: ['Biotech', 'IA'] });
    assert.match(out, /Biotech/);
    assert.match(out, /IA/);
  });
});

describe('buildEditaisPdfRows', () => {
  it('nunca retorna undefined nos campos', () => {
    const rows = buildEditaisPdfRows([{}, { titulo: 'Teste' }]);
    assert.equal(rows.length, 2);
    rows.forEach((row) => {
      Object.values(row).forEach((cell) => {
        assert.notEqual(cell, undefined);
      });
    });
  });

  it('lida com campos ausentes', () => {
    const row = buildEditaisPdfRows([{ titulo: 'Edital X' }])[0];
    assert.equal(row.titulo, 'Edital X');
    assert.equal(row.fonte, '-');
    assert.equal(row.prazo, 'Sem prazo');
    assert.match(row.status, /Sem prazo|indefinido/i);
  });

  it('inclui coluna Status', () => {
    const row = buildEditaisPdfRows([
      { titulo: 'Edital Y', prazo_envio: '2026-12-31' },
    ])[0];
    assert.ok(row.status);
    assert.notEqual(row.status, '-');
  });
});

describe('formatStatusForPdf', () => {
  it('retorna label curto', () => {
    const out = formatStatusForPdf({ titulo: 'Chamada aberta' });
    assert.match(out, /Sem prazo|Aberto/i);
  });
});

describe('buildEditaisPdfColumns', () => {
  it('inclui coluna Status (10 colunas)', () => {
    const cols = buildEditaisPdfColumns();
    assert.equal(cols.length, 10);
    assert.ok(cols.some((c) => c.dataKey === 'status'));
  });
});

describe('buildPdfFiltersSummary', () => {
  it('{} retorna nenhum filtro aplicado', () => {
    assert.equal(buildPdfFiltersSummary([]), 'Filtros: nenhum filtro aplicado');
  });

  it('não retorna JSON bruto', () => {
    const summary = buildPdfFiltersSummary(['Área: Tecnologia', 'UF: RS']);
    assert.match(summary, /Filtros:/);
    assert.doesNotMatch(summary, /\{/);
    assert.match(summary, /Área/);
  });
});
