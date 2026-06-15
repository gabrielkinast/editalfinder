import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { normalizeExternalUrl } from './normalizeExternalUrl.js';
import { resolveActionUrl } from './actionUrlResolver.js';
import { EXTERNAL_ACTION_TYPES } from './actionTypes.js';

describe('normalizeExternalUrl', () => {
  it('aceita http/https e adiciona https quando ausente', () => {
    assert.equal(normalizeExternalUrl('https://example.com/a'), 'https://example.com/a');
    assert.equal(normalizeExternalUrl('http://example.com'), 'http://example.com/');
    assert.equal(normalizeExternalUrl('example.org/path'), 'https://example.org/path');
    assert.equal(normalizeExternalUrl('//cdn.example.com/x.pdf'), 'https://cdn.example.com/x.pdf');
  });

  it('rejeita placeholders e javascript', () => {
    assert.equal(normalizeExternalUrl(''), null);
    assert.equal(normalizeExternalUrl('#'), null);
    assert.equal(normalizeExternalUrl('javascript:alert(1)'), null);
    assert.equal(normalizeExternalUrl(null), null);
  });

  it('aceita mailto para uso explícito no feedback', () => {
    const url = normalizeExternalUrl('mailto:Suporte.EditalFinder@gmail.com?subject=test');
    assert.ok(url?.startsWith('mailto:'));
  });
});

describe('resolveActionUrl', () => {
  const edital = {
    link: 'https://edital.example/1',
    pdf_url: 'https://edital.example/1.pdf',
    link_inscricao: 'https://inscricao.example/1',
    url_detalhe: 'https://detalhe.example/1',
  };

  it('prioriza campos canónicos', () => {
    assert.equal(
      resolveActionUrl(edital, EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY),
      'https://edital.example/1',
    );
    assert.equal(
      resolveActionUrl(edital, EXTERNAL_ACTION_TYPES.EDITAL_PDF),
      'https://edital.example/1.pdf',
    );
    assert.equal(
      resolveActionUrl(edital, EXTERNAL_ACTION_TYPES.EDITAL_INSCRICAO),
      'https://inscricao.example/1',
    );
  });

  it('usa fallback legado só quando canónico ausente', () => {
    const legacy = { url_pdf: 'https://legacy.example/pdf' };
    assert.equal(
      resolveActionUrl(legacy, EXTERNAL_ACTION_TYPES.EDITAL_PDF),
      'https://legacy.example/pdf',
    );
  });

  it('resolve concursos com link e link_edital', () => {
    const concurso = {
      link: 'https://portal.example',
      link_edital: 'https://portal.example/edital.pdf',
    };
    assert.equal(
      resolveActionUrl(concurso, EXTERNAL_ACTION_TYPES.CONCURSO_PRIMARY),
      'https://portal.example/',
    );
    assert.equal(
      resolveActionUrl(concurso, EXTERNAL_ACTION_TYPES.CONCURSO_EDITAL),
      'https://portal.example/edital.pdf',
    );
  });

  it('honra rawUrl em options', () => {
    assert.equal(
      resolveActionUrl(null, EXTERNAL_ACTION_TYPES.GENERIC_URL, {
        rawUrl: 'https://override.example',
      }),
      'https://override.example/',
    );
  });
});
