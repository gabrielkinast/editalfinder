import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  SUPABASE_ERROR_KIND,
  classifySupabaseError,
  getSupabaseSafeErrorDetails,
  getSupabaseFriendlyMessage,
} from './supabaseErrorClassifier.js';

describe('classifySupabaseError', () => {
  it('detecta row-level security', () => {
    const kind = classifySupabaseError({
      message: 'new row violates row-level security policy for table "edital"',
      code: '42501',
    });
    assert.equal(kind, SUPABASE_ERROR_KIND.RLS_POLICY);
  });

  it('detecta policy na mensagem', () => {
    const kind = classifySupabaseError({
      message: 'violates policy "edital_insert_admin" on table edital',
      status: 403,
    });
    assert.equal(kind, SUPABASE_ERROR_KIND.RLS_POLICY);
  });

  it('detecta permission denied e 403', () => {
    assert.equal(
      classifySupabaseError({ message: 'permission denied for table edital', status: 403 }),
      SUPABASE_ERROR_KIND.PERMISSION_DENIED,
    );
    assert.equal(
      classifySupabaseError({ message: 'insufficient privileges', status: 401 }),
      SUPABASE_ERROR_KIND.PERMISSION_DENIED,
    );
  });

  it('detecta schema PGRST205', () => {
    const kind = classifySupabaseError({
      code: 'PGRST205',
      message: 'Could not find the table public.edital_x in the schema cache',
    });
    assert.equal(kind, SUPABASE_ERROR_KIND.SCHEMA);
  });

  it('detecta duplicate 23505', () => {
    const kind = classifySupabaseError({
      code: '23505',
      message: 'duplicate key value violates unique constraint "edital_link_key"',
    });
    assert.equal(kind, SUPABASE_ERROR_KIND.DUPLICATE);
  });
});

describe('getSupabaseSafeErrorDetails', () => {
  it('não retorna tokens ou keys', () => {
    const details = getSupabaseSafeErrorDetails({
      message: 'Bearer access_token=secret refresh_token=abc service_role=xyz',
      code: '42501',
      status: 403,
      details: 'anon key leaked',
    });
    const blob = JSON.stringify(details).toLowerCase();
    assert.equal(blob.includes('access_token'), false);
    assert.equal(blob.includes('refresh_token'), false);
    assert.equal(blob.includes('service_role'), false);
    assert.equal(blob.includes('bearer'), false);
    assert.equal(details.message, '[mensagem redigida]');
  });
});

describe('getSupabaseFriendlyMessage', () => {
  it('mensagem admin para rls_policy', () => {
    const msg = getSupabaseFriendlyMessage(
      { message: 'new row violates row-level security policy' },
      { frontendIsAdmin: true },
    );
    assert.equal(msg.title, 'Permissão de administrador não reconhecida pelo banco');
    assert.match(msg.message, /administrador/);
  });
});
