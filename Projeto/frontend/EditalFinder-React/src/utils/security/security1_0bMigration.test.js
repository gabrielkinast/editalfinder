import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, it } from 'node:test';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MIGRATION = resolve(
  __dirname,
  '../../../../../backend/migrations/20260610_security_1_0b_edital_admin_write_policy.sql',
);

describe('SECURITY 1.0B migration (estático)', () => {
  it('arquivo de migration existe', () => {
    assert.equal(existsSync(MIGRATION), true);
  });

  it('contém policies admin select/insert/update sem delete', () => {
    const raw = readFileSync(MIGRATION, 'utf8');
    const active = raw.replace(/^--.*$/gm, '').toLowerCase();
    assert.match(active, /edital_admin_select/);
    assert.match(active, /edital_admin_insert/);
    assert.match(active, /edital_admin_update/);
    assert.match(active, /for select/);
    assert.match(active, /for insert/);
    assert.match(active, /for update/);
    assert.match(active, /to authenticated/);
    assert.match(active, /using \(public\.current_app_user_is_admin\(\)\)/);
    assert.match(active, /current_app_user_is_admin\(\)/);
    assert.equal(active.includes('for delete'), false);
    assert.equal(/with\s+check\s*\(\s*true\s*\)/i.test(active), false);
    const selectBlock = active.split('edital_admin_select')[1]?.split('edital_admin_insert')[0] ?? '';
    assert.equal(selectBlock.includes('to anon'), false);
  });
});
