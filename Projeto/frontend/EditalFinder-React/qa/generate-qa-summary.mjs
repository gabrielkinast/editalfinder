#!/usr/bin/env node
/**
 * QA 1.3A — gera qa/artifacts/qa_summary_latest.md a partir de qa_results.json.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ARTIFACTS = resolve(ROOT, 'qa/artifacts');
const RESULTS_PATH = resolve(ARTIFACTS, 'qa_results.json');
const LATEST_PATH = resolve(ARTIFACTS, 'qa_summary_latest.md');
const HISTORY_PATH = resolve(ARTIFACTS, 'qa_summary.md');

function fmtSec(sec) {
  if (sec == null || Number.isNaN(Number(sec))) return '—';
  return `${Number(sec).toFixed(1)}s`;
}

function statusEmoji(status) {
  if (status === 'passed') return 'passed';
  if (status === 'failed') return '**failed**';
  if (status === 'skipped') return 'skipped';
  return status || 'unknown';
}

/** @param {object} results */
export function renderQaSummaryMarkdown(results) {
  const env = results.environment || {};
  const unit = results.A_unit || {};
  const build = results.B_build || {};
  const e2e = results.C_e2e || {};
  const specs = Array.isArray(results.e2e_specs) ? results.e2e_specs : [];

  const lines = [
    '# QA Summary — Latest Run',
    '',
    `Generated at: ${results.generated_at || new Date().toISOString()}`,
    '',
    '## Environment',
    '',
    `- Auth configured: ${env.authConfigured ? 'yes' : 'no'}${env.authEmailMasked ? ` (${env.authEmailMasked})` : ''}`,
    `- Write tests enabled: ${env.writeTestsEnabled ? 'yes' : 'no'}`,
    `- CI: ${env.ci ? 'yes' : 'no'}`,
    `- Platform: ${env.platform || '—'} · Node ${env.node || '—'}`,
    `- Supabase URL in env: ${env.hasSupabaseUrl ? 'yes' : 'no'}`,
    '',
    '## Results',
    '',
    '| Layer | Status | Passed | Failed | Skipped | Duration |',
    '| --- | --- | ---: | ---: | ---: | ---: |',
    `| Unit | ${statusEmoji(unit.status)} | ${unit.passed ?? '—'} | ${unit.failed ?? 0} | ${unit.skipped ?? 0} | ${fmtSec(unit.duration_sec)} |`,
    `| Build | ${statusEmoji(build.status)} | — | ${build.status === 'failed' ? 1 : 0} | — | ${fmtSec(build.duration_sec)} |`,
    `| E2E | ${statusEmoji(e2e.status)} | ${e2e.passed ?? '—'} | ${e2e.failed ?? 0} | ${e2e.skipped ?? 0} | ${fmtSec(e2e.duration_sec)} |`,
    '',
  ];

  if (specs.length) {
    lines.push('## E2E Specs', '');
    lines.push('| Status | Project | File | Test | Duration |');
    lines.push('| --- | --- | --- | --- | ---: |');
    for (const s of specs) {
      const dur = s.duration_ms != null ? `${(s.duration_ms / 1000).toFixed(1)}s` : '—';
      const fileShort = String(s.file || '').replace(/^tests\/e2e\//, '');
      lines.push(
        `| ${s.status} | ${s.project} | \`${fileShort}\` | ${s.title} | ${dur} |`,
      );
    }
    lines.push('');
  }

  lines.push(
    '## Artifacts',
    '',
    '- Logs: `qa/artifacts/logs/`',
    '- Playwright JSON: `qa/artifacts/playwright/results.json`',
    '- Playwright HTML: `qa/artifacts/playwright/html/`',
    '- QA results: `qa/artifacts/qa_results.json`',
    '- Run state: `qa/artifacts/qa_run_state.json`',
    '',
    '## Notes',
    '',
    '- E2E autenticados fazem skip sem `E2E_USER_EMAIL` / `E2E_USER_PASSWORD`.',
    '- Escrita em Cadastros exige `E2E_ALLOW_WRITE_TESTS=1`.',
    '- Skips por dados/permissões são esperados em alguns ambientes.',
    '- Gerado por `npm run qa:local` (QA 1.3A).',
    '',
  );

  return lines.join('\n');
}

/** Atualiza seção curta em qa_summary.md (histórico preservado). */
export function patchQaSummaryHistory(markdown, results) {
  const section = [
    '## Última execução automática',
    '',
    `Atualizado: ${results.generated_at || new Date().toISOString()}`,
    '',
    `| Camada | Status | Detalhe |`,
    `| --- | --- | --- |`,
    `| Unit | ${results.A_unit?.status || '—'} | ${results.A_unit?.passed ?? '—'} passed |`,
    `| Build | ${results.B_build?.status || '—'} | ${fmtSec(results.B_build?.duration_sec)} |`,
    `| E2E | ${results.C_e2e?.status || '—'} | ${results.C_e2e?.passed ?? '—'} passed, ${results.C_e2e?.skipped ?? 0} skipped |`,
    '',
    'Ver detalhes: `qa/artifacts/qa_summary_latest.md`',
    '',
  ].join('\n');

  const marker = '## Última execução automática';
  if (!existsSync(HISTORY_PATH)) {
    return `# QA Summary — EditalFinder\n\n${section}`;
  }

  let content = readFileSync(HISTORY_PATH, 'utf8');
  const idx = content.indexOf(marker);
  if (idx === -1) {
    return `${content.trimEnd()}\n\n${section}`;
  }

  const after = content.slice(idx + marker.length);
  const nextH2 = after.search(/\n## /);
  const tail = nextH2 >= 0 ? after.slice(nextH2) : '';
  const before = content.slice(0, idx);
  return `${before}${section}${tail.startsWith('\n') ? tail : `\n${tail}`}`;
}

export function generateQaSummary(options = {}) {
  const root = options.root || ROOT;
  const artifacts = resolve(root, 'qa/artifacts');
  const resultsPath = resolve(artifacts, 'qa_results.json');
  const latestPath = resolve(artifacts, 'qa_summary_latest.md');
  const historyPath = resolve(artifacts, 'qa_summary.md');

  mkdirSync(artifacts, { recursive: true });

  if (!existsSync(resultsPath)) {
    throw new Error(`qa_results.json não encontrado: ${resultsPath}. Rode qa:results primeiro.`);
  }

  const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
  const markdown = renderQaSummaryMarkdown(results);
  writeFileSync(latestPath, markdown, 'utf8');

  const history = patchQaSummaryHistory(markdown, results);
  writeFileSync(historyPath, history, 'utf8');

  return { latestPath, historyPath, results };
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const { latestPath, historyPath } = generateQaSummary();
  console.info(`[qa:summary] wrote ${latestPath}`);
  console.info(`[qa:summary] updated ${historyPath}`);
}
