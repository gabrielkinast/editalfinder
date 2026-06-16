import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  getEditalOfficialUrl,
  getEditalPdfUrl,
  getEditalInscricaoUrl,
  resolveEditalActionUrls,
  resolveExternalActionUrl,
  UNSAFE_OFFICIAL_LINK_MSG,
} from './getEditalActionUrls.js';
import { EXTERNAL_ACTION_TYPES } from '../externalActions/actionTypes.js';

const GRANTS = {
  fonte: 'Grants.gov',
  link: 'https://www.grants.gov/page-not-found',
  extras: { grants_opportunity_id: '361410' },
  pdf_url: 'https://cdn.example.com/doc.pdf',
  link_inscricao: 'https://www.grants.gov/page-not-found',
};

test('botão principal usa official URL canonicalizada', () => {
  const url = getEditalOfficialUrl({
    fonte: 'Grants.gov',
    link: 'https://simpler.grants.gov/opportunity/361410',
  });
  assert.equal(url, 'https://www.grants.gov/search-results-detail/361410');
});

test('botão PDF usa pdf_url, não Grants detail', () => {
  const pdf = getEditalPdfUrl(GRANTS);
  assert.equal(pdf, 'https://cdn.example.com/doc.pdf');
  assert.ok(!pdf.includes('search-results-detail'));
});

test('inscrição page-not-found cai para official URL', () => {
  const info = getEditalInscricaoUrl(GRANTS);
  assert.equal(info.url, 'https://www.grants.gov/search-results-detail/361410');
  assert.equal(info.fallback, true);
});

test('inscrição segura não usa fallback', () => {
  const info = getEditalInscricaoUrl({
    fonte: 'FAPESP',
    link_inscricao: 'https://fapesp.br/inscricao',
    link: 'https://fapesp.br/edital',
  });
  assert.equal(info.url, 'https://fapesp.br/inscricao');
  assert.equal(info.fallback, false);
});

test('resolveEditalActionUrls retorna site/pdf/inscricao coerentes', () => {
  const r = resolveEditalActionUrls(GRANTS);
  assert.match(r.site, /search-results-detail\/361410/);
  assert.equal(r.pdf, 'https://cdn.example.com/doc.pdf');
  assert.match(r.inscricao, /search-results-detail\/361410/);
  assert.ok(r.rejectedUrls.some((u) => /page-not-found/i.test(u)));
});

test('resolveExternalActionUrl recanoniza override Grants.gov quebrado', () => {
  const url = resolveExternalActionUrl(
    { fonte: 'Grants.gov', extras: { grants_opportunity_id: '999' } },
    EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY,
    'https://www.grants.gov/page-not-found',
    EXTERNAL_ACTION_TYPES,
  );
  assert.equal(url, 'https://www.grants.gov/search-results-detail/999');
});

test('resolveExternalActionUrl rejeita javascript:', () => {
  const url = resolveExternalActionUrl(
    { link: 'https://fapesp.br/ok' },
    EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY,
    'javascript:alert(1)',
    EXTERNAL_ACTION_TYPES,
  );
  assert.equal(url, 'https://fapesp.br/ok');
});

test('fonte não-Grants continua usando link normal', () => {
  assert.equal(
    getEditalOfficialUrl({ fonte: 'FAPESP', link: 'https://fapesp.br/chamada/1' }),
    'https://fapesp.br/chamada/1',
  );
});

test('UNSAFE_OFFICIAL_LINK_MSG definida', () => {
  assert.match(UNSAFE_OFFICIAL_LINK_MSG, /link oficial seguro/i);
});

test('PDF legado url_pdf quando pdf_url ausente', () => {
  assert.equal(
    getEditalPdfUrl({ url_pdf: 'https://legacy.example/pdf' }),
    'https://legacy.example/pdf',
  );
});
