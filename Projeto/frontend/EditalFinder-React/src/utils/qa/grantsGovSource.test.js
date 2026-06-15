import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { isGrantsGovSource } from './grantsGovSource.js';
import { isGrantsCardRecord } from './grantsCardMatch.js';

describe('isGrantsGovSource', () => {
  it('Grants.gov => true', () => {
    assert.equal(isGrantsGovSource('Grants.gov'), true);
  });

  it('grants_gov => true', () => {
    assert.equal(isGrantsGovSource('grants_gov'), true);
  });

  it('GRANTS.GOV => true', () => {
    assert.equal(isGrantsGovSource('GRANTS.GOV'), true);
  });

  it('U.S. Grants.gov => true', () => {
    assert.equal(isGrantsGovSource('U.S. Grants.gov'), true);
  });

  it('BNDES => false', () => {
    assert.equal(isGrantsGovSource('BNDES'), false);
  });

  it('null/undefined => false', () => {
    assert.equal(isGrantsGovSource(null), false);
    assert.equal(isGrantsGovSource(undefined), false);
  });
});

describe('isGrantsCardRecord', () => {
  it('detecta por data-fonte Grants.gov', () => {
    assert.equal(isGrantsCardRecord({ fonte: 'Grants.gov', source: '' }), true);
  });

  it('detecta por URL resolvida', () => {
    assert.equal(
      isGrantsCardRecord({
        fonte: '',
        qaResolvedUrl: 'https://www.grants.gov/search-results-detail/12345',
      }),
      true,
    );
  });
});
