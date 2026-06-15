#!/usr/bin/env node
/**
 * QA 1.3A — runner local: unit → build → e2e → artefatos.
 */
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, appendFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { sanitizeLogText, getSanitizeOptsFromEnv } from './lib/qaArtifactUtils.mjs';
import { generateQaResults } from './generate-qa-results.mjs';
import { generateQaSummary } from './generate-qa-summary.mjs';
import { loadLocalEnvFiles } from '../tests/e2e/_env.js';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ARTIFACTS = resolve(ROOT, 'qa/artifacts');
const LOGS_DIR = resolve(ARTIFACTS, 'logs');
const RUN_STATE_PATH = resolve(ARTIFACTS, 'qa_run_state.json');
const QA_LOCAL_LOG = resolve(LOGS_DIR, 'qa-local.log');

const STEPS = [
  { key: 'unit', command: 'npm', args: ['test'], log: 'unit.log' },
  { key: 'build', command: 'npm', args: ['run', 'build'], log: 'build.log' },
  { key: 'e2e', command: 'npm', args: ['run', 'e2e'], log: 'e2e.log' },
];

/**
 * @param {string} command
 * @param {string[]} args
 * @param {string} logPath
 */
function runStep(command, args, logPath) {
  const sanitizeOpts = getSanitizeOptsFromEnv();
  const started = Date.now();

  return new Promise((resolvePromise) => {
    const chunks = [];
    const child = spawn(command, args, {
      cwd: ROOT,
      env: { ...process.env },
      shell: process.platform === 'win32',
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    const onData = (buf) => {
      const text = buf.toString();
      chunks.push(text);
      process.stdout.write(text);
    };

    child.stdout?.on('data', onData);
    child.stderr?.on('data', onData);

    child.on('close', (code) => {
      const duration_sec = (Date.now() - started) / 1000;
      const raw = chunks.join('');
      const sanitized = sanitizeLogText(raw, sanitizeOpts);
      writeFileSync(logPath, sanitized, 'utf8');
      resolvePromise({
        exitCode: code ?? 1,
        duration_sec,
        command: `${command} ${args.join(' ')}`.trim(),
        log: `qa/artifacts/logs/${logPath.split(/[/\\]/).pop()}`,
      });
    });

    child.on('error', (err) => {
      const duration_sec = (Date.now() - started) / 1000;
      const msg = sanitizeLogText(String(err), sanitizeOpts);
      writeFileSync(logPath, msg, 'utf8');
      resolvePromise({
        exitCode: 1,
        duration_sec,
        command: `${command} ${args.join(' ')}`.trim(),
        log: `qa/artifacts/logs/${logPath.split(/[/\\]/).pop()}`,
        error: err.message,
      });
    });
  });
}

function logLine(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  appendFileSync(QA_LOCAL_LOG, line, 'utf8');
  console.info(msg);
}

export async function runLocalQa() {
  loadLocalEnvFiles();
  mkdirSync(LOGS_DIR, { recursive: true });
  mkdirSync(ARTIFACTS, { recursive: true });
  writeFileSync(QA_LOCAL_LOG, '', 'utf8');

  const generated_at = new Date().toISOString();
  const steps = {};
  let overallFailed = false;

  logLine('QA 1.3A — iniciando qa:local');

  for (const step of STEPS) {
    const logPath = resolve(LOGS_DIR, step.log);
    logLine(`→ ${step.key}: ${step.command} ${step.args.join(' ')}`);
    const result = await runStep(step.command, step.args, logPath);
    steps[step.key] = result;
    logLine(
      `  ${step.key} finished exit=${result.exitCode} duration=${result.duration_sec.toFixed(1)}s`,
    );
    if (result.exitCode !== 0) overallFailed = true;
  }

  const runState = { generated_at, steps };
  writeFileSync(RUN_STATE_PATH, `${JSON.stringify(runState, null, 2)}\n`, 'utf8');
  logLine(`run state → ${RUN_STATE_PATH}`);

  try {
    const { path: resultsPath } = generateQaResults({ root: ROOT });
    logLine(`qa results → ${resultsPath}`);
  } catch (err) {
    logLine(`qa:results error: ${err?.message || err}`);
    overallFailed = true;
  }

  try {
    const { latestPath } = generateQaSummary({ root: ROOT });
    logLine(`qa summary → ${latestPath}`);
  } catch (err) {
    logLine(`qa:summary error: ${err?.message || err}`);
    overallFailed = true;
  }

  logLine(overallFailed ? 'QA local finished WITH FAILURES' : 'QA local finished OK');
  return { overallFailed, runState };
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  runLocalQa()
    .then(({ overallFailed }) => {
      process.exit(overallFailed ? 1 : 0);
    })
    .catch((err) => {
      console.error('[qa:local] fatal:', err);
      process.exit(1);
    });
}
