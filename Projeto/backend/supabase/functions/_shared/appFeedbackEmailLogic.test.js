import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  buildFeedbackEmail,
  validateFeedbackPayload,
} from './appFeedbackEmailLogic.js';

describe('validateFeedbackPayload (edge)', () => {
  it('rejeita descrição curta', () => {
    const result = validateFeedbackPayload({ descricao: 'curta' });
    assert.equal(result.valid, false);
    assert.ok(result.errors.descricao);
  });

  it('aceita payload válido', () => {
    const result = validateFeedbackPayload({
      descricao: 'Descrição válida com detalhes.',
      email_contato: 'user@example.com',
    });
    assert.equal(result.valid, true);
  });
});

describe('buildFeedbackEmail (edge)', () => {
  it('monta assunto e corpo legíveis (web)', () => {
    const email = buildFeedbackEmail({
      descricao: 'Botão travou ao abrir PDF.',
      categoria: 'ui',
      rota: '/radar-fomento',
      tipo: 'button_action_error',
      tipo_label: 'Botão ou ação não funcionou',
      runtime: 'web_browser',
      is_desktop: false,
      id_local: 'test-id',
    });

    assert.match(email.subject, /\[EditalFinder\] Reporte — Navegador — \/radar-fomento/);
    assert.match(email.text, /Botão travou ao abrir PDF/);
    assert.match(email.text, /Botão ou ação não funcionou/);
    assert.match(email.text, /Rota: \/radar-fomento/);
    assert.match(email.text, /test-id/);
  });

  it('destaca desktop no assunto e corpo', () => {
    const email = buildFeedbackEmail({
      descricao: 'Link do edital não abriu no EXE.',
      tipo: 'desktop_exe_error',
      tipo_label: 'Erro no aplicativo desktop / EXE',
      categoria: 'desktop',
      rota: '/editais',
      runtime: 'desktop_tauri',
      is_desktop: true,
    });

    assert.match(email.subject, /Desktop\/EXE/);
    assert.match(email.text, /Erro no aplicativo desktop \/ EXE/);
    assert.match(email.text, /Ambiente detectado: Desktop\/Tauri/);
  });

  it('assunto específico para export PDF', () => {
    const email = buildFeedbackEmail({
      descricao: 'Falha ao gerar PDF do edital.',
      tipo: 'pdf_export_error',
      rota: '/editais',
    });
    assert.match(email.subject, /PDF export/);
  });
});
