import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  getOfficialEditalUrl,
  resolveOfficialEditalUrlInfo,
  extractGrantsOpportunityId,
  buildGrantsCanonicalUrl,
  isBrokenUrl,
  isGrantsGovUrl,
} from './officialEditalUrl.js';

test('usa link canônico search-results-detail quando já válido', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'Grants.gov',
    link: 'https://www.grants.gov/search-results-detail/361410',
  });
  assert.equal(info.url, 'https://www.grants.gov/search-results-detail/361410');
  assert.equal(info.canonicalized, false);
  assert.equal(info.source, 'grants');
});

test('nunca escolhe page-not-found', () => {
  const url = getOfficialEditalUrl({
    fonte: 'Grants.gov',
    link: 'https://www.grants.gov/page-not-found',
    extras: { grants_opportunity_id: '361410' },
  });
  assert.ok(!/page-not-found/i.test(url));
  assert.equal(url, 'https://www.grants.gov/search-results-detail/361410');
});

test('descarta url_detalhe quebrada e cai no fallback de busca', () => {
  const url = getOfficialEditalUrl({
    fonte: 'Grants.gov',
    link: 'https://www.grants.gov/page-not-found',
    url_detalhe: 'https://www.grants.gov/404',
  });
  assert.ok(!isBrokenUrl(url));
  assert.match(url, /grants\.gov\/search-grants/);
});

test('constrói canônico a partir de extras.grants_opportunity_id', () => {
  const url = getOfficialEditalUrl({
    fonte: 'Grants.gov',
    extras: { grants_opportunity_id: '361410' },
  });
  assert.equal(url, 'https://www.grants.gov/search-results-detail/361410');
});

test('normaliza simpler.grants.gov/opportunity/<id> para search-results-detail', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'Grants.gov',
    link: 'https://simpler.grants.gov/opportunity/361410',
  });
  assert.equal(info.url, 'https://www.grants.gov/search-results-detail/361410');
  assert.equal(info.canonicalized, true);
});

test('normaliza view-opportunity e oppId querystring', () => {
  assert.equal(
    getOfficialEditalUrl({ fonte: 'grants', link: 'https://www.grants.gov/view-opportunity/361410' }),
    'https://www.grants.gov/search-results-detail/361410',
  );
  assert.equal(
    getOfficialEditalUrl({ fonte: 'grants', link: 'https://www.grants.gov/web/grants/view?oppId=361410' }),
    'https://www.grants.gov/search-results-detail/361410',
  );
});

test('normaliza view-opportunity.html com query id', () => {
  assert.equal(
    getOfficialEditalUrl({
      fonte: 'Grants.gov',
      link: 'https://www.grants.gov/view-opportunity.html?id=361410',
    }),
    'https://www.grants.gov/search-results-detail/361410',
  );
});

test('link_inscricao page-not-found não vence official URL (via action resolver)', async () => {
  const { resolveActionUrl } = await import('../externalActions/actionUrlResolver.js');
  const { EXTERNAL_ACTION_TYPES } = await import('../externalActions/actionTypes.js');
  const url = resolveActionUrl(
    {
      fonte: 'Grants.gov',
      link: 'https://www.grants.gov/page-not-found',
      link_inscricao: 'https://www.grants.gov/page-not-found',
      extras: { grants_opportunity_id: '555666' },
    },
    EXTERNAL_ACTION_TYPES.EDITAL_INSCRICAO,
  );
  assert.equal(url, 'https://www.grants.gov/search-results-detail/555666');
});

test('pdf_url preservado apenas em botão PDF', async () => {
  const { resolveActionUrl } = await import('../externalActions/actionUrlResolver.js');
  const { EXTERNAL_ACTION_TYPES } = await import('../externalActions/actionTypes.js');
  const item = {
    fonte: 'Grants.gov',
    link: 'https://simpler.grants.gov/opportunity/361410',
    pdf_url: 'https://files.example.com/grant.pdf',
  };
  assert.equal(
    resolveActionUrl(item, EXTERNAL_ACTION_TYPES.EDITAL_PDF),
    'https://files.example.com/grant.pdf',
  );
  assert.match(
    resolveActionUrl(item, EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY),
    /search-results-detail\/361410/,
  );
});

test('javascript: rejeitado em URL genérica', () => {
  assert.equal(getOfficialEditalUrl({ fonte: 'FAPESP', link: 'javascript:alert(1)' }), null);
});

test('metadata inclui rejectedUrls e fieldUsed', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'Grants.gov',
    link: 'https://www.grants.gov/page-not-found',
    extras: { grants_opportunity_id: '123456' },
  });
  assert.equal(info.fieldUsed, 'extras.grants_opportunity_id');
  assert.equal(info.canonicalized, true);
  assert.ok(Array.isArray(info.rejectedUrls));
  assert.ok(info.rejectedUrls.some((u) => /page-not-found/i.test(u)));
});

test('extractGrantsOpportunityId só aceita domínio grants.gov', () => {
  assert.equal(extractGrantsOpportunityId('https://www.grants.gov/opportunity/123456'), '123456');
  assert.equal(extractGrantsOpportunityId('https://example.com/opportunity/123456'), null);
});

test('buildGrantsCanonicalUrl valida id numérico', () => {
  assert.equal(buildGrantsCanonicalUrl('123456'), 'https://www.grants.gov/search-results-detail/123456');
  assert.equal(buildGrantsCanonicalUrl('abc'), null);
  assert.equal(buildGrantsCanonicalUrl(''), null);
});

test('detecta Grants.gov por fonte mesmo sem domínio no link', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'Grants.gov',
    extras: { opportunity_id: '999888' },
  });
  assert.equal(info.source, 'grants');
  assert.equal(info.url, 'https://www.grants.gov/search-results-detail/999888');
});

test('edital genérico usa primeira URL válida (não-grants)', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'FAPESP',
    link: 'https://fapesp.br/chamada/123',
  });
  assert.equal(info.source, 'generic');
  assert.equal(info.url, 'https://fapesp.br/chamada/123');
  assert.equal(info.canonicalized, false);
});

test('genérico ignora link quebrado e usa próximo campo', () => {
  const info = resolveOfficialEditalUrlInfo({
    fonte: 'FAPESP',
    link: 'https://fapesp.br/page-not-found',
    url: 'https://fapesp.br/chamada/ok',
  });
  assert.equal(info.url, 'https://fapesp.br/chamada/ok');
});

test('sem nenhum link válido retorna null (genérico)', () => {
  assert.equal(getOfficialEditalUrl({ fonte: 'FAPESP' }), null);
  assert.equal(getOfficialEditalUrl(null), null);
});

test('helpers de detecção', () => {
  assert.equal(isGrantsGovUrl('https://www.grants.gov/x'), true);
  assert.equal(isGrantsGovUrl('https://simpler.grants.gov/x'), true);
  assert.equal(isGrantsGovUrl('https://fapesp.br'), false);
  assert.equal(isBrokenUrl('https://x/page-not-found'), true);
  assert.equal(isBrokenUrl('https://x/ok'), false);
});
