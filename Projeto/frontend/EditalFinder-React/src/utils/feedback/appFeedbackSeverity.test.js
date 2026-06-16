import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  getFeedbackSeverity,
  normalizeLegacySeverity,
} from './appFeedbackSeverity.js';
import { normalizeRouteForEmail } from './appFeedbackLabels.js';

describe('normalizeLegacySeverity', () => {
  it('mapeia normal para medium', () => {
    assert.equal(normalizeLegacySeverity('normal'), 'medium');
  });

  it('mapeia urgent para high', () => {
    assert.equal(normalizeLegacySeverity('urgent'), 'high');
  });
});

describe('getFeedbackSeverity', () => {
  it('null → medium (Média)', () => {
    const result = getFeedbackSeverity(null);
    assert.equal(result.value, 'medium');
    assert.equal(result.label, 'Média');
    assert.equal(result.emailPrefix, 'MÉDIA');
  });

  it('"normal" → medium', () => {
    assert.equal(getFeedbackSeverity('normal').value, 'medium');
  });

  it('"low" → Baixa', () => {
    const result = getFeedbackSeverity('low');
    assert.equal(result.label, 'Baixa');
    assert.equal(result.emailPrefix, 'BAIXA');
  });

  it('"critical" → Crítica', () => {
    const result = getFeedbackSeverity('critical');
    assert.equal(result.label, 'Crítica');
    assert.equal(result.emailPrefix, 'CRÍTICA');
  });

  it('desconhecido → medium', () => {
    assert.equal(getFeedbackSeverity('xyz_invalid').value, 'medium');
  });
});

describe('normalizeRouteForEmail', () => {
  it('normaliza dashboard para /dashboard', () => {
    assert.equal(normalizeRouteForEmail('dashboard'), '/dashboard');
  });

  it('retorna sem rota quando vazio', () => {
    assert.equal(normalizeRouteForEmail(''), 'sem rota');
    assert.equal(normalizeRouteForEmail(null), 'sem rota');
  });
});
