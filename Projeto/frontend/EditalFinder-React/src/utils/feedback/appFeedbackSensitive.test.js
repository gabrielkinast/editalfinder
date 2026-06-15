import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  redactSensitiveFeedbackValue,
  sanitizePayloadForSupportEmail,
} from './appFeedbackSensitive.js';
import { buildSupportEmailBody } from './appFeedbackMailto.js';

describe('redactSensitiveFeedbackValue', () => {
  it('redige chaves sensíveis', () => {
    assert.equal(redactSensitiveFeedbackValue('access_token', 'abc'), '[REDACTED]');
    assert.equal(redactSensitiveFeedbackValue('session_id', 'xyz'), '[REDACTED]');
    assert.equal(redactSensitiveFeedbackValue('password', '123'), '[REDACTED]');
  });

  it('redige Bearer em strings preservando prefixo', () => {
    const out = redactSensitiveFeedbackValue('user_agent', 'Bearer eyJhbGciOiJIUzI1NiJ9');
    assert.equal(out, 'Bearer [REDACTED]');
  });
});

describe('sanitizePayloadForSupportEmail no corpo mailto', () => {
  it('não vaza token/authorization/password/session no body', () => {
    const body = buildSupportEmailBody({
      descricao: 'Erro ao salvar',
      tipo_label: 'Outro',
      categoria: 'other',
      platform_context: {
        access_token: 'secret-token-123',
        authorization: 'Bearer abc.def.ghi',
        session: 'sess-999',
      },
      metadata: {
        api_key: 'key-abc',
        password: 'p@ss',
      },
      mensagem_erro: 'authorization header invalid Bearer xyz',
    });

    assert.doesNotMatch(body, /secret-token-123/);
    assert.doesNotMatch(body, /key-abc/);
    assert.doesNotMatch(body, /p@ss/);
    assert.doesNotMatch(body, /Bearer abc\.def\.ghi/);
    assert.match(body, /\[REDACTED\]/);
  });

  it('sanitiza objeto aninhado', () => {
    const safe = sanitizePayloadForSupportEmail({
      metadata: { refresh_token: 'rt-1', origem: 'user_report' },
    });
    assert.equal(safe.metadata.refresh_token, '[REDACTED]');
    assert.equal(safe.metadata.origem, 'user_report');
  });
});
