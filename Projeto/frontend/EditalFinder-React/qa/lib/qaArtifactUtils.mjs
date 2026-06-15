/**
 * QA 1.3A — utilitários puros para artefatos de QA (parse, sanitize, summary).
 */
import { readFileSync, existsSync } from 'node:fs';

const SENSITIVE_ENV_KEYS = new Set([
  'E2E_USER_PASSWORD',
  'VITE_SUPABASE_ANON_KEY',
  'SUPABASE_SERVICE_ROLE_KEY',
  'SUPABASE_SERVICE_ROLE',
  'SUPABASE_ANON_KEY',
]);

/** @param {string} email */
export function maskEmail(email) {
  const s = String(email || '').trim();
  if (!s || !s.includes('@')) return '[REDACTED_EMAIL]';
  const [local, domain] = s.split('@');
  const maskedLocal = local.length <= 1 ? '*' : `${local[0]}***`;
  return `${maskedLocal}@${domain}`;
}

/**
 * Sanitiza texto de log antes de persistir.
 * @param {string} text
 * @param {{ email?: string, password?: string }} [opts]
 */
export function sanitizeLogText(text, opts = {}) {
  let out = String(text ?? '');

  if (opts.password) {
    const pwd = String(opts.password);
    if (pwd.length > 0) {
      out = out.split(pwd).join('[REDACTED]');
    }
  }

  if (opts.email) {
    const email = String(opts.email).trim();
    if (email) {
      out = out.split(email).join(maskEmail(email));
    }
  }

  const patterns = [
    [/Bearer\s+[A-Za-z0-9._\-+/=]+/gi, 'Bearer [REDACTED]'],
    [/Authorization:\s*Bearer\s+[A-Za-z0-9._\-+/=]+/gi, 'Authorization: Bearer [REDACTED]'],
    [/"access_token"\s*:\s*"[^"]*"/gi, '"access_token":"[REDACTED]"'],
    [/"refresh_token"\s*:\s*"[^"]*"/gi, '"refresh_token":"[REDACTED]"'],
    [/access_token=[A-Za-z0-9._\-+/=]+/gi, 'access_token=[REDACTED]'],
    [/refresh_token=[A-Za-z0-9._\-+/=]+/gi, 'refresh_token=[REDACTED]'],
    [/eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/g, '[REDACTED_JWT]'],
    [/VITE_SUPABASE_ANON_KEY[=:]\s*['"]?[A-Za-z0-9._\-+/=]+/gi, 'VITE_SUPABASE_ANON_KEY=[REDACTED]'],
    [/SUPABASE_SERVICE_ROLE[_KEY]*[=:]\s*['"]?[A-Za-z0-9._\-+/=]+/gi, 'SUPABASE_SERVICE_ROLE_KEY=[REDACTED]'],
    [/E2E_USER_PASSWORD[=:]\s*['"]?[^\s'"]+/gi, 'E2E_USER_PASSWORD=[REDACTED]'],
  ];

  for (const [re, repl] of patterns) {
    out = out.replace(re, repl);
  }

  return out;
}

/** @param {string} logText */
export function parseUnitLog(logText) {
  const text = String(logText || '');
  const passMatch = text.match(/ℹ\s+pass\s+(\d+)/i) || text.match(/(\d+)\s*\/\s*(\d+)\s+passed/i);
  const failMatch = text.match(/ℹ\s+fail\s+(\d+)/i);
  const skipMatch = text.match(/ℹ\s+skipped\s+(\d+)/i);

  let passed = 0;
  let failed = 0;
  let skipped = 0;

  if (passMatch) {
    if (passMatch[2] != null) {
      passed = Number(passMatch[1]) || 0;
    } else {
      passed = Number(passMatch[1]) || 0;
    }
  }
  if (failMatch) failed = Number(failMatch[1]) || 0;
  if (skipMatch) skipped = Number(skipMatch[1]) || 0;

  const totalMatch = text.match(/ℹ\s+tests\s+(\d+)/i);
  const total = totalMatch ? Number(totalMatch[1]) : passed + failed + skipped;

  let status = 'unknown';
  if (failMatch || /fail\s+[1-9]/i.test(text)) {
    status = Number(failed) > 0 ? 'failed' : 'passed';
  } else if (passed > 0 && failed === 0) {
    status = 'passed';
  } else if (/✖|not ok/i.test(text)) {
    status = 'failed';
  }

  return { passed, failed, skipped, total, status };
}

/**
 * @param {unknown} json
 */
export function parsePlaywrightResults(json) {
  const empty = {
    passed: 0,
    failed: 0,
    skipped: 0,
    duration_sec: null,
    specs: [],
    status: 'unknown',
  };

  if (!json || typeof json !== 'object') return empty;

  const specs = [];
  walkSuites(json.suites, specs);

  const stats = json.stats;
  let passed = stats?.expected ?? 0;
  let failed = stats?.unexpected ?? 0;
  let skipped = stats?.skipped ?? 0;
  let duration_sec = stats?.duration != null ? Number(stats.duration) / 1000 : null;

  if (!stats) {
    passed = 0;
    failed = 0;
    skipped = 0;
    for (const s of specs) {
      if (s.status === 'passed') passed += 1;
      else if (s.status === 'failed') failed += 1;
      else if (s.status === 'skipped') skipped += 1;
    }
  }

  let status = 'unknown';
  if (specs.length || stats) {
    status = failed > 0 ? 'failed' : 'passed';
  }

  return { passed, failed, skipped, duration_sec, specs, status };
}

/** @param {unknown[]} suites @param {object[]} out */
function walkSuites(suites, out) {
  if (!Array.isArray(suites)) return;
  for (const suite of suites) {
    for (const spec of suite.specs || []) {
      for (const test of spec.tests || []) {
        const result = test.results?.[0];
        let status = result?.status || 'unknown';
        if (status === 'timedOut') status = 'failed';
        if (test.status === 'skipped' && status === 'unknown') status = 'skipped';

        const file = spec.file ? `tests/e2e/${spec.file}` : 'tests/e2e/unknown';
        out.push({
          title: spec.title || '(sem título)',
          file,
          project: test.projectName || test.projectId || 'unknown',
          status,
          duration_ms: result?.duration ?? null,
        });
      }
    }
    walkSuites(suite.suites, out);
  }
}

/**
 * Monta objeto qa_results.json.
 * @param {object} params
 */
export function summarizeQaResults({
  runState,
  unitParsed,
  playwrightParsed,
  environment,
}) {
  const steps = runState?.steps || {};

  const unitExit = steps.unit?.exitCode;
  const buildExit = steps.build?.exitCode;
  const e2eExit = steps.e2e?.exitCode;

  const A_unit = {
    status:
      unitExit === 0
        ? unitParsed.status === 'failed'
          ? 'failed'
          : 'passed'
        : unitExit != null
          ? 'failed'
          : unitParsed.status,
    passed: unitParsed.passed,
    failed: unitParsed.failed,
    skipped: unitParsed.skipped,
    total: unitParsed.total,
    duration_sec: steps.unit?.duration_sec ?? null,
    log: 'qa/artifacts/logs/unit.log',
  };

  const B_build = {
    status: buildExit === 0 ? 'passed' : buildExit != null ? 'failed' : 'unknown',
    duration_sec: steps.build?.duration_sec ?? null,
    log: 'qa/artifacts/logs/build.log',
  };

  let e2eStatus = 'unknown';
  if (e2eExit != null) {
    if (e2eExit !== 0) e2eStatus = 'failed';
    else if (playwrightParsed.failed > 0) e2eStatus = 'failed';
    else e2eStatus = 'passed';
  } else if (playwrightParsed.specs.length) {
    e2eStatus = playwrightParsed.failed > 0 ? 'failed' : 'passed';
  }

  const C_e2e = {
    status: e2eStatus,
    passed: playwrightParsed.passed,
    failed: playwrightParsed.failed,
    skipped: playwrightParsed.skipped,
    duration_sec: steps.e2e?.duration_sec ?? playwrightParsed.duration_sec,
    results: 'qa/artifacts/playwright/results.json',
    html: 'qa/artifacts/playwright/html',
    log: 'qa/artifacts/logs/e2e.log',
  };

  return {
    generated_at: new Date().toISOString(),
    patch: 'QA 1.3A — Standardized QA scripts',
    environment,
    A_unit,
    B_build,
    C_e2e,
    e2e_specs: playwrightParsed.specs,
    steps: runState?.steps || {},
    artifacts: {
      logs: 'qa/artifacts/logs',
      playwright: 'qa/artifacts/playwright',
      qa_run_state: 'qa/artifacts/qa_run_state.json',
      qa_summary_latest: 'qa/artifacts/qa_summary_latest.md',
    },
  };
}

/** @param {string} path */
export function readTextIfExists(path) {
  if (!existsSync(path)) return '';
  try {
    return readFileSync(path, 'utf8');
  } catch {
    return '';
  }
}

export function buildEnvironmentMeta(env = process.env) {
  const email = String(env.E2E_USER_EMAIL || '').trim();
  const password = String(env.E2E_USER_PASSWORD || '');
  return {
    node: process.version,
    platform: process.platform,
    authConfigured: Boolean(email && password),
    authEmailMasked: email ? maskEmail(email) : null,
    writeTestsEnabled: String(env.E2E_ALLOW_WRITE_TESTS || '').trim() === '1',
    ci: Boolean(env.CI),
    hasSupabaseUrl: Boolean(String(env.VITE_SUPABASE_URL || '').trim()),
  };
}

export function getSanitizeOptsFromEnv(env = process.env) {
  return {
    email: env.E2E_USER_EMAIL,
    password: env.E2E_USER_PASSWORD,
  };
}
