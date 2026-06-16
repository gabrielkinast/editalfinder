import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  SUPPORT_EMAIL,
  buildGmailComposeUrl,
  buildSupportEmailBody,
  buildSupportEmailSubject,
  buildSupportMailtoUrl,
  openSupportEmailComposer,
} from './appFeedbackMailto.js';
import { executeAppFeedbackSubmit } from './appFeedbackSubmitFlow.js';
import { buildAppFeedbackPayload } from './appFeedbackPayload.js';
import {
  MSG_APP_FEEDBACK_SUCCESS_GMAIL,
  MSG_APP_FEEDBACK_SUCCESS_MAILTO,
  MSG_APP_FEEDBACK_SUCCESS_LOCAL,
} from '../../constants/appFeedbackConfig.js';

const samplePayload = {
  tipo: 'desktop_exe_error',
  tipo_label: 'Erro no aplicativo desktop / EXE',
  categoria: 'desktop',
  severidade: 'normal',
  descricao: 'O link do edital não abriu no aplicativo desktop.',
  rota: '/radar-fomento',
  pagina: 'radar_fomento',
  pagina_url: 'https://app.example/radar-fomento',
  runtime: 'desktop_tauri',
  is_desktop: true,
  app_version: '0.1.0',
  created_at: '2026-05-18T12:00:00.000Z',
  id_local: 'test-local-id',
  user_agent: 'Mozilla/5.0 Test',
  platform_context: {
    runtime: 'desktop_tauri',
    is_desktop: true,
    is_web: false,
    user_agent: 'Mozilla/5.0 Test',
    platform: 'Win32',
    language: 'pt-BR',
  },
};

describe('buildSupportEmailSubject', () => {
  it('inclui [EditalFinder], severidade, tipo_label e rota normalizada', () => {
    const subject = buildSupportEmailSubject(samplePayload);
    assert.match(subject, /\[EditalFinder\]/);
    assert.match(subject, /\[MÉDIA\]/);
    assert.match(subject, /Erro no aplicativo desktop \/ EXE/);
    assert.match(subject, /\/radar-fomento/);
  });

  it('inclui [ALTA] ou [CRÍTICA] conforme severidade', () => {
    const alta = buildSupportEmailSubject({ ...samplePayload, severidade: 'high' });
    const critica = buildSupportEmailSubject({ ...samplePayload, severidade: 'critical' });
    assert.match(alta, /\[ALTA\]/);
    assert.match(critica, /\[CRÍTICA\]/);
  });

  it('normaliza rota dashboard para /dashboard', () => {
    const subject = buildSupportEmailSubject({
      ...samplePayload,
      rota: 'dashboard',
      severidade: 'medium',
    });
    assert.match(subject, /\/dashboard/);
  });
});

describe('buildSupportEmailBody', () => {
  it('contém severidade, labels humanos, descrição e runtime', () => {
    const body = buildSupportEmailBody({
      ...samplePayload,
      severidade: 'high',
    });
    assert.match(body, /Severidade: Alta/);
    assert.match(body, /Tipo do problema: Erro no aplicativo desktop \/ EXE/);
    assert.match(body, /Categoria: Desktop\/EXE/);
    assert.match(body, /O link do edital não abriu/);
    assert.match(body, /desktop_tauri/);
    assert.match(body, /test-local-id/);
    assert.match(body, /Rota: \/radar-fomento/);
    assert.doesNotMatch(body, /Categoria: other/);
  });

  it('não contém tokens ou chaves sensíveis', () => {
    const body = buildSupportEmailBody({
      ...samplePayload,
      descricao: 'Falha com access_token=abc123 e api_key=secret',
      user_agent: 'Bearer eyJhbGciOiJIUzI1NiJ9',
      metadata: { session: 'sess-1', password: 'pwd' },
    });
    assert.doesNotMatch(body, /access_token=abc123/);
    assert.doesNotMatch(body, /api_key=secret/);
    assert.doesNotMatch(body, /Bearer eyJ/);
    assert.doesNotMatch(body, /sess-1/);
    assert.doesNotMatch(body, /SUPABASE_SERVICE_ROLE_KEY/);
    assert.doesNotMatch(body, /RESEND_API_KEY/);
    assert.match(body, /\[REDACTED\]/);
  });
});

describe('buildGmailComposeUrl', () => {
  it('começa com Gmail compose e contém parâmetros obrigatórios', () => {
    const url = buildGmailComposeUrl(samplePayload);
    assert.match(url, /^https:\/\/mail\.google\.com\/mail\/\?/);
    assert.match(url, /view=cm/);
    assert.match(url, /fs=1/);
    assert.match(url, /to=Suporte\.EditalFinder%40gmail\.com/);
    assert.match(url, /su=/);
    assert.match(url, /body=/);
  });

  it('subject contém [EditalFinder], severidade e rota no parâmetro su', () => {
    const url = buildGmailComposeUrl(samplePayload);
    const params = new URL(url).searchParams;
    const subject = params.get('su') || '';
    assert.match(subject, /\[EditalFinder\]/);
    assert.match(subject, /\[MÉDIA\]/);
    assert.match(subject, /\/radar-fomento/);
    assert.match(subject, /Erro no aplicativo desktop \/ EXE/);
  });

  it('body contém descrição e runtime decodificados', () => {
    const url = buildGmailComposeUrl(samplePayload);
    const body = new URL(url).searchParams.get('body') || '';
    assert.match(body, /O link do edital não abriu/);
    assert.match(body, /desktop_tauri/);
    assert.match(body, /test-local-id/);
  });
});

describe('buildSupportMailtoUrl', () => {
  it('inclui destinatário, subject e body URL-encoded', () => {
    const url = buildSupportMailtoUrl(samplePayload);
    assert.ok(url);
    assert.match(url, new RegExp(`mailto:${SUPPORT_EMAIL.replace('.', '\\.')}`, 'i'));
    assert.match(url, /subject=/);
    assert.match(url, /body=/);
    const decoded = decodeURIComponent(url.replace(/\+/g, ' '));
    assert.match(decoded, /Suporte\.EditalFinder@gmail\.com/);
    assert.match(decoded, /O link do edital não abriu/);
  });
});

describe('openSupportEmailComposer', () => {
  it('tenta Gmail primeiro', async () => {
    const calls = [];
    const result = await openSupportEmailComposer(samplePayload, {
      openExternalUrl: async (url, opts) => {
        calls.push({ url, opts });
        if (url.includes('mail.google.com')) return true;
        return false;
      },
    });

    assert.equal(result.ok, true);
    assert.equal(result.method, 'gmail_compose');
    assert.equal(calls.length, 1);
    assert.match(calls[0].url, /mail\.google\.com/);
  });

  it('tenta mailto se Gmail falha', async () => {
    const calls = [];
    const result = await openSupportEmailComposer(samplePayload, {
      openExternalUrl: async (url, opts) => {
        calls.push({ url, opts });
        if (url.startsWith('mailto:')) {
          assert.equal(opts.allowMailto, true);
          return true;
        }
        return false;
      },
    });

    assert.equal(result.ok, true);
    assert.equal(result.method, 'mailto');
    assert.equal(calls.length, 2);
    assert.match(calls[0].url, /mail\.google\.com/);
    assert.match(calls[1].url, /^mailto:/);
  });

  it('retorna ok:false se Gmail e mailto falham', async () => {
    const result = await openSupportEmailComposer(samplePayload, {
      openExternalUrl: async () => false,
    });

    assert.equal(result.ok, false);
    assert.equal(result.reason, 'email_composer_failed');
  });
});

describe('openSupportMailto', () => {
  it('não define window.location.href no fallback', async () => {
    const prevHref = Object.getOwnPropertyDescriptor(global, 'location');
    let hrefAssigned = false;
    Object.defineProperty(global, 'location', {
      configurable: true,
      get() {
        return { href: 'http://localhost/' };
      },
      set(v) {
        hrefAssigned = String(v).startsWith('mailto:');
      },
    });

    const { openSupportMailto } = await import('./appFeedbackMailto.js');
    const result = await openSupportMailto({
      descricao: 'Falha simulada ao abrir mailto.',
      tipo_label: 'Outro',
      rota: '/',
    });

    assert.equal(hrefAssigned, false);

    if (prevHref) Object.defineProperty(global, 'location', prevHref);
    else delete global.location;
    assert.equal(typeof result.ok, 'boolean');
  });
});

describe('executeAppFeedbackSubmit (Gmail → mailto → local)', () => {
  const payload = buildAppFeedbackPayload({
    descricao: 'Descrição válida com detalhes suficientes.',
    tipo: 'other',
  });

  it('retorna gmail_compose quando Gmail abre', async () => {
    const result = await executeAppFeedbackSubmit(payload, {}, {
      openEmailComposer: async () => ({ ok: true, method: 'gmail_compose' }),
      saveLocal: () => {},
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.status, 'opened_email_client');
    assert.equal(result.method, 'gmail_compose');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_GMAIL);
  });

  it('retorna mailto quando Gmail falha e mailto abre', async () => {
    const result = await executeAppFeedbackSubmit(payload, {}, {
      openEmailComposer: async () => ({ ok: true, method: 'mailto' }),
      saveLocal: () => {},
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.method, 'mailto');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_MAILTO);
  });

  it('salva local quando compositor falha', async () => {
    let saved = false;
    const result = await executeAppFeedbackSubmit(payload, {}, {
      openEmailComposer: async () => ({ ok: false, reason: 'email_composer_failed' }),
      saveLocal: () => {
        saved = true;
      },
      flushPending: async () => {},
    });

    assert.equal(result.ok, true);
    assert.equal(result.status, 'saved_local');
    assert.equal(result.message, MSG_APP_FEEDBACK_SUCCESS_LOCAL);
    assert.equal(saved, true);
  });
});
