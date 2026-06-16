#!/usr/bin/env node
/**
 * QA 1.3A — gera qa/artifacts/qa_results.json a partir do estado da execução.
 */
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  parseUnitLog,
  parsePlaywrightResults,
  summarizeQaResults,
  readTextIfExists,
  buildEnvironmentMeta,
} from './lib/qaArtifactUtils.mjs';
import { loadLocalEnvFiles } from '../tests/e2e/_env.js';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ARTIFACTS = resolve(ROOT, 'qa/artifacts');
const RUN_STATE_PATH = resolve(ARTIFACTS, 'qa_run_state.json');
const PLAYWRIGHT_RESULTS = resolve(ARTIFACTS, 'playwright/results.json');
const OUT_PATH = resolve(ARTIFACTS, 'qa_results.json');

export function generateQaResults(options = {}) {
  loadLocalEnvFiles();
  const root = options.root || ROOT;
  const artifacts = resolve(root, 'qa/artifacts');
  const runStatePath = resolve(artifacts, 'qa_run_state.json');
  const playwrightPath = resolve(artifacts, 'playwright/results.json');
  const outPath = resolve(artifacts, 'qa_results.json');

  mkdirSync(artifacts, { recursive: true });

  let runState = {};
  if (existsSync(runStatePath)) {
    try {
      runState = JSON.parse(readFileSync(runStatePath, 'utf8'));
    } catch {
      runState = {};
    }
  }

  const unitLog = readTextIfExists(resolve(artifacts, 'logs/unit.log'));
  const unitParsed = parseUnitLog(unitLog);

  let playwrightJson = null;
  if (existsSync(playwrightPath)) {
    try {
      playwrightJson = JSON.parse(readFileSync(playwrightPath, 'utf8'));
    } catch {
      playwrightJson = null;
    }
  }
  const playwrightParsed = parsePlaywrightResults(playwrightJson);

  const environment = buildEnvironmentMeta(process.env);

  const results = summarizeQaResults({
    runState,
    unitParsed,
    playwrightParsed,
    environment,
  });

  writeFileSync(outPath, `${JSON.stringify(results, null, 2)}\n`, 'utf8');
  return { path: outPath, results };
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const { path } = generateQaResults();
  console.info(`[qa:results] wrote ${path}`);
}
