import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  maskEmail,
  sanitizeLogText,
  parseUnitLog,
  parsePlaywrightResults,
  summarizeQaResults,
} from './lib/qaArtifactUtils.mjs';

describe('maskEmail', () => {
  it('mascara e-mail', () => {
    assert.equal(maskEmail('user@example.com'), 'u***@example.com');
    assert.equal(maskEmail(''), '[REDACTED_EMAIL]');
  });
});

describe('sanitizeLogText', () => {
  it('remove senha e tokens', () => {
    const out = sanitizeLogText(
      'password=secret123 Bearer eyJhbGciOiJIUzI1NiJ9.x.y access_token=abc',
      { password: 'secret123' },
    );
    assert.ok(!out.includes('secret123'));
    assert.match(out, /\[REDACTED\]/);
    assert.match(out, /Bearer \[REDACTED\]/);
  });

  it('mascara e-mail no log', () => {
    const out = sanitizeLogText('login user@test.com ok', { email: 'user@test.com' });
    assert.ok(!out.includes('user@test.com'));
    assert.match(out, /u\*\*\*@test\.com/);
  });
});

describe('parseUnitLog', () => {
  it('extrai contagens do node:test', () => {
    const log = `
ℹ tests 283
ℹ pass 283
ℹ fail 0
ℹ skipped 0
`;
    const p = parseUnitLog(log);
    assert.equal(p.passed, 283);
    assert.equal(p.failed, 0);
    assert.equal(p.status, 'passed');
  });
});

describe('parsePlaywrightResults', () => {
  it('usa stats do JSON Playwright', () => {
    const p = parsePlaywrightResults({
      stats: { expected: 15, skipped: 4, unexpected: 0, duration: 96000 },
      suites: [],
    });
    assert.equal(p.passed, 15);
    assert.equal(p.skipped, 4);
    assert.equal(p.failed, 0);
    assert.equal(p.status, 'passed');
  });

  it('extrai specs aninhadas', () => {
    const p = parsePlaywrightResults({
      suites: [
        {
          specs: [
            {
              title: 'smoke test',
              file: 'smoke.spec.js',
              tests: [
                {
                  projectName: 'public',
                  results: [{ status: 'passed', duration: 1200 }],
                },
              ],
            },
          ],
        },
      ],
    });
    assert.equal(p.specs.length, 1);
    assert.equal(p.specs[0].status, 'passed');
    assert.equal(p.specs[0].project, 'public');
  });
});

describe('summarizeQaResults', () => {
  it('monta camadas A/B/C', () => {
    const out = summarizeQaResults({
      runState: {
        steps: {
          unit: { exitCode: 0, duration_sec: 10 },
          build: { exitCode: 0, duration_sec: 2 },
          e2e: { exitCode: 0, duration_sec: 90 },
        },
      },
      unitParsed: { passed: 283, failed: 0, skipped: 0, total: 283, status: 'passed' },
      playwrightParsed: { passed: 5, failed: 0, skipped: 13, duration_sec: 20, specs: [], status: 'passed' },
      environment: { authConfigured: false, ci: false },
    });
    assert.equal(out.A_unit.status, 'passed');
    assert.equal(out.B_build.status, 'passed');
    assert.equal(out.C_e2e.status, 'passed');
    assert.equal(out.C_e2e.skipped, 13);
  });
});
