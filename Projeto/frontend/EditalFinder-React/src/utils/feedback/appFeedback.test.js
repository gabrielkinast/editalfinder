import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  buildAppFeedbackPayload,
  normalizeFeedbackPayload,
  validateAppFeedbackPayload,
} from './appFeedbackPayload.js';
import {
  getFeedbackProblemType,
  mapContextToDefaultTipo,
} from './appFeedbackTaxonomy.js';
import {
  classifyAppFeedbackRemoteError,
} from './postgrestFeedbackErrors.js';
import {
  normalizeQueuedFeedback,
  readAppFeedbackQueue,
  saveAppFeedbackLocal,
  writeAppFeedbackQueue,
} from './appFeedbackQueue.js';
import {
  APP_FEEDBACK_PROBLEM_TYPES,
  APP_FEEDBACK_QUEUE_KEY,
  APP_FEEDBACK_QUEUE_MAX,
} from '../../constants/appFeedbackConfig.js';
import { getRuntimeContext } from './runtimeContext.js';

function createMemoryStorage() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => {
      map.set(key, value);
    },
    removeItem: (key) => {
      map.delete(key);
    },
  };
}

describe('getFeedbackProblemType', () => {
  it('retorna fallback para null, não null', () => {
    const result = getFeedbackProblemType(null);
    assert.ok(result);
    assert.equal(result.value, 'other');
    assert.equal(result.label, 'Outro');
    assert.equal(result.group, 'other');
  });

  it('retorna fallback para tipo inexistente', () => {
    const result = getFeedbackProblemType('tipo_inexistente');
    assert.equal(result.value, 'other');
    assert.equal(result.label, 'Outro');
  });
});

describe('mapContextToDefaultTipo', () => {
  it('não quebra com context null (startup do modal fechado)', () => {
    assert.equal(mapContextToDefaultTipo(null), 'other');
  });

  it('não quebra com context undefined', () => {
    assert.equal(mapContextToDefaultTipo(undefined), 'other');
  });
});

describe('normalizeFeedbackPayload', () => {
  it('preenche tipo em payload antigo sem tipo', () => {
    const normalized = normalizeFeedbackPayload({
      descricao: 'Relato antigo.',
      tipo_feedback: 'erro_api',
    });
    assert.equal(normalized.tipo, 'save_load_error');
    assert.ok(normalized.tipo_label);
    assert.equal(normalized.categoria, 'data');
    assert.equal(normalized.categoria_label, 'Dados');
  });

  it('normaliza severidade legado normal para Média', () => {
    const normalized = normalizeFeedbackPayload({
      descricao: 'Relato antigo.',
      severidade: 'normal',
    });
    assert.equal(normalized.severidade, 'medium');
    assert.equal(normalized.severidade_label, 'Média');
    assert.equal(normalized.severidade_email_prefix, 'MÉDIA');
  });
});

describe('APP_FEEDBACK_PROBLEM_TYPES', () => {
  it('inclui categorias desktop/EXE', () => {
    const values = APP_FEEDBACK_PROBLEM_TYPES.map((t) => t.value);
    assert.ok(values.includes('desktop_exe_error'));
    assert.ok(values.includes('desktop_open_link_error'));
    assert.ok(values.includes('desktop_startup_error'));
    assert.ok(values.includes('desktop_update_install_error'));
  });
});

describe('getRuntimeContext', () => {
  const prevTauri = global.window?.__TAURI__;

  it('retorna web_browser sem Tauri', () => {
    if (global.window) delete global.window.__TAURI__;
    const ctx = getRuntimeContext();
    assert.equal(ctx.runtime, 'web_browser');
    assert.equal(ctx.is_web, true);
    assert.equal(ctx.is_desktop, false);
  });

  it('retorna desktop_tauri com mock __TAURI__', () => {
    if (!global.window) return;
    global.window.__TAURI__ = {};
    const ctx = getRuntimeContext();
    assert.equal(ctx.runtime, 'desktop_tauri');
    assert.equal(ctx.is_desktop, true);
    if (prevTauri === undefined) delete global.window.__TAURI__;
    else global.window.__TAURI__ = prevTauri;
  });
});

describe('buildAppFeedbackPayload', () => {
  it('não quebra sem tipo e define fallback other', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Problema válido sem tipo explícito.',
    });
    assert.equal(payload.tipo, 'other');
    assert.equal(payload.tipo_label, 'Outro');
    assert.equal(payload.categoria, 'other');
    assert.equal(payload.categoria_label, 'Outro');
    assert.equal(payload.severidade, 'medium');
    assert.equal(payload.severidade_label, 'Média');
  });

  it('sem severidade → medium', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Problema válido com severidade padrão.',
    });
    assert.equal(payload.severidade, 'medium');
    assert.equal(payload.severidade_label, 'Média');
    assert.equal(payload.severidade_email_prefix, 'MÉDIA');
  });

  it('severidade high → severidade_label Alta', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Problema grave que impede funcionalidade.',
      severidade: 'high',
    });
    assert.equal(payload.severidade, 'high');
    assert.equal(payload.severidade_label, 'Alta');
    assert.equal(payload.severidade_email_prefix, 'ALTA');
  });

  it('severidade critical → emailPrefix CRÍTICA', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'App travou completamente na tela branca.',
      severidade: 'critical',
    });
    assert.equal(payload.severidade_email_prefix, 'CRÍTICA');
  });

  it('mapeia severidade legado normal para medium', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Payload antigo com severidade normal.',
      severidade: 'normal',
    });
    assert.equal(payload.severidade, 'medium');
    assert.equal(payload.severidade_label, 'Média');
  });

  it('não quebra com tipo null', () => {
    const payload = buildAppFeedbackPayload({
      tipo: null,
      descricao: 'Problema válido com tipo null.',
    });
    assert.equal(payload.tipo, 'other');
    assert.ok(payload.tipo_label);
  });

  it('monta payload básico com id_local e metadata', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'O botão de PDF não abre.',
      tipo: 'button_action_error',
    });

    assert.ok(payload.id_local);
    assert.equal(payload.descricao, 'O botão de PDF não abre.');
    assert.equal(payload.comentario, payload.descricao);
    assert.ok(payload.created_at);
    assert.equal(payload.status, 'pending');
    assert.ok(payload.metadata);
    assert.equal(typeof payload.is_desktop, 'boolean');
  });

  it('inclui tipo, tipo_label, categoria, runtime e platform_context', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Erro no EXE ao abrir link externo.',
      tipo: 'desktop_exe_error',
    });

    assert.equal(payload.tipo, 'desktop_exe_error');
    assert.equal(payload.tipo_label, 'Erro no aplicativo desktop / EXE');
    assert.equal(payload.categoria, 'desktop');
    assert.ok(payload.runtime);
    assert.ok(payload.platform_context);
    assert.equal(payload.platform_context.runtime, payload.runtime);
    assert.equal(payload.tipo_feedback, 'erro_global');
  });

  it('mapeia tipo legado botao_nao_funciona', () => {
    const payload = buildAppFeedbackPayload({
      descricao: 'Botão não respondeu ao clique.',
      tipo: 'botao_nao_funciona',
    });
    assert.equal(payload.tipo, 'button_action_error');
    assert.equal(payload.tipo_feedback, 'botao_nao_funciona');
  });
});

describe('validateAppFeedbackPayload', () => {
  it('rejeita descrição vazia', () => {
    const result = validateAppFeedbackPayload(buildAppFeedbackPayload({ descricao: '' }));
    assert.equal(result.valid, false);
    assert.ok(result.errors.descricao);
  });

  it('aceita descrição válida', () => {
    const result = validateAppFeedbackPayload(
      buildAppFeedbackPayload({ descricao: 'Descrição válida com detalhes.' }),
    );
    assert.equal(result.valid, true);
  });

  it('rejeita e-mail inválido', () => {
    const payload = buildAppFeedbackPayload({ descricao: 'Descrição válida com detalhes.' });
    payload.email_contato = 'abc';
    const result = validateAppFeedbackPayload(payload);
    assert.equal(result.valid, false);
    assert.ok(result.errors.email_contato);
  });
});

describe('classifyAppFeedbackRemoteError', () => {
  it('detecta PGRST205', () => {
    assert.equal(
      classifyAppFeedbackRemoteError({
        code: 'PGRST205',
        message: "Could not find the table 'public.app_feedback' in the schema cache",
      }),
      'remote_table_missing',
    );
  });

  it('detecta RLS', () => {
    assert.equal(
      classifyAppFeedbackRemoteError({ message: 'new row violates row-level security policy' }),
      'permission_error',
    );
  });

  it('detecta network', () => {
    assert.equal(
      classifyAppFeedbackRemoteError({ message: 'Failed to fetch' }),
      'network_error',
    );
  });
});

describe('appFeedbackQueue', () => {
  it('salva item no storage mock e limita fila', () => {
    const storage = createMemoryStorage();
    const payload = buildAppFeedbackPayload({ descricao: 'Relato de teste com detalhes.' });

    saveAppFeedbackLocal(payload, 'remote_table_missing', storage);
    const queue = readAppFeedbackQueue(storage);

    assert.equal(queue.length, 1);
    assert.equal(queue[0].id_local, payload.id_local);
    assert.equal(queue[0].payload.descricao, payload.descricao);
    assert.equal(queue[0].last_error_reason, 'remote_table_missing');
  });

  it('não duplica id_local igual', () => {
    const storage = createMemoryStorage();
    const payload = buildAppFeedbackPayload({ descricao: 'Relato de teste com detalhes.' });

    saveAppFeedbackLocal(payload, 'network_error', storage);
    saveAppFeedbackLocal(payload, 'network_error', storage);

    assert.equal(readAppFeedbackQueue(storage).length, 1);
  });

  it('limita fila a APP_FEEDBACK_QUEUE_MAX', () => {
    const storage = createMemoryStorage();
    const entries = [];

    for (let i = 0; i < APP_FEEDBACK_QUEUE_MAX + 5; i += 1) {
      entries.push({
        id_local: `id_${i}`,
        payload: { descricao: `Item ${i} com texto longo.` },
        saved_at: new Date().toISOString(),
        attempts: 0,
      });
    }

    writeAppFeedbackQueue(entries, storage);
    const raw = JSON.parse(storage.getItem(APP_FEEDBACK_QUEUE_KEY));
    assert.equal(raw.length, APP_FEEDBACK_QUEUE_MAX);
  });
});

describe('submit fallback pattern', () => {
  it('remote_table_missing aciona save local com sucesso parcial', () => {
    const storage = createMemoryStorage();
    const payload = buildAppFeedbackPayload({ descricao: 'Falha remota simulada aqui.' });
    const reason = classifyAppFeedbackRemoteError({
      code: 'PGRST205',
      message: 'schema cache',
    });

    saveAppFeedbackLocal(payload, reason, storage);

    const queue = readAppFeedbackQueue(storage);
    assert.equal(queue.length, 1);
    assert.equal(queue[0].last_error_reason, 'remote_table_missing');
  });

  it('normalizeQueuedFeedback preenche campos em item legado', () => {
    const legacy = normalizeQueuedFeedback({
      id_local: 'old-1',
      payload: {
        descricao: 'Relato antigo sem taxonomia.',
        tipo_feedback: 'erro_api',
      },
    });
    assert.equal(legacy.payload.tipo, 'save_load_error');
    assert.equal(legacy.payload.categoria, 'data');
    assert.ok(legacy.payload.tipo_label);
  });
});
