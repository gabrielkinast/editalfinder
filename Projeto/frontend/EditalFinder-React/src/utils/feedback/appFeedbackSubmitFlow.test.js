import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { buildAppFeedbackPayload } from './appFeedbackPayload.js';
import {
  executeAppFeedbackSubmit,
  executeFlushPendingAppFeedback,
} from './appFeedbackSubmitFlow.js';
import {
  MSG_APP_FEEDBACK_SUCCESS_GMAIL,
  MSG_APP_FEEDBACK_SUCCESS_MAILTO,
  MSG_APP_FEEDBACK_SUCCESS_LOCAL,
} from '../../constants/appFeedbackConfig.js';

function makePayload() {
  return buildAppFeedbackPayload({
    descricao: 'Descrição válida com detalhes suficientes.',
    tipo: 'other',
  });
}

describe('executeAppFeedbackSubmit', () => {
  it('retorna opened_email_client com Gmail quando gmail_compose OK', async () => {
    const result = await executeAppFeedbackSubmit(makePayload(), {}, {
      openEmailComposer: async () => ({ ok: true, method: 'gmail_compose' }),
      saveLocal: () => {},
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.status, 'opened_email_client');
    assert.equal(result.method, 'gmail_compose');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_GMAIL);
    assert.ok(result.email_subject);
    assert.match(result.email_subject, /\[EditalFinder\]/);
    assert.doesNotMatch(result.message, /enviado/i);
    assert.match(result.message, /Revise e envie/i);
  });

  it('retorna mailto quando método mailto OK', async () => {
    const result = await executeAppFeedbackSubmit(makePayload(), {}, {
      openEmailComposer: async () => ({ ok: true, method: 'mailto' }),
      saveLocal: () => {},
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.method, 'mailto');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_MAILTO);
  });

  it('salva local quando compositor falha e devolve manual_report_text', async () => {
    let saved = false;
    const payload = makePayload();
    const result = await executeAppFeedbackSubmit(payload, {}, {
      openEmailComposer: async () => ({ ok: false, reason: 'email_composer_failed' }),
      saveLocal: (p) => {
        saved = true;
        assert.equal(p.id_local, payload.id_local);
      },
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.status, 'saved_local');
    assert.equal(result.fallback_reason, 'email_composer_failed');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_LOCAL);
    assert.equal(saved, true);
    assert.match(result.manual_report_text, /^Para: Suporte\.EditalFinder@gmail\.com/);
    assert.match(result.manual_report_text, /Assunto:/);
    assert.match(result.manual_report_text, /Mensagem:/);
    assert.match(result.manual_report_text, /Descrição válida/);
    assert.doesNotMatch(result.message, /enviado/i);
  });
});

describe('executeFlushPendingAppFeedback', () => {
  it('remove item da fila quando mailto OK', async () => {
    const payload = makePayload();
    const queue = [{ id_local: payload.id_local, payload, attempts: 0 }];

    const result = await executeFlushPendingAppFeedback(queue, {}, {
      openEmailComposer: async () => ({ ok: true, method: 'gmail_compose' }),
    });

    assert.equal(result.sent, 1);
    assert.equal(result.remaining.length, 0);
  });

  it('mantém item quando mailto falha', async () => {
    const payload = makePayload();
    const queue = [{ id_local: payload.id_local, payload, attempts: 0 }];

    const result = await executeFlushPendingAppFeedback(queue, {}, {
      openEmailComposer: async () => ({ ok: false, reason: 'email_composer_failed' }),
    });

    assert.equal(result.sent, 0);
    assert.equal(result.remaining.length, 1);
    assert.equal(result.remaining[0].attempts, 1);
  });
});
