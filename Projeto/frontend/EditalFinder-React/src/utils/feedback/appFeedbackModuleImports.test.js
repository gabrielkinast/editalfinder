import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

describe('app feedback modules import safely', () => {
  it('mapContextToDefaultTipo(null) não lança', async () => {
    const { mapContextToDefaultTipo } = await import('./appFeedbackTaxonomy.js');
    assert.equal(mapContextToDefaultTipo(null), 'other');
  });

  it('importa mailto e runtime sem executar mailto', async () => {
    const mailto = await import('./appFeedbackMailto.js');
    const runtime = await import('./runtimeContext.js');
    const submitFlow = await import('./appFeedbackSubmitFlow.js');

    assert.equal(typeof mailto.buildSupportMailtoUrl, 'function');
    assert.equal(typeof mailto.openSupportMailto, 'function');
    assert.equal(typeof mailto.openSupportEmailComposer, 'function');
    assert.equal(typeof mailto.buildGmailComposeUrl, 'function');
    assert.equal(typeof runtime.getRuntimeContext, 'function');
    assert.equal(typeof submitFlow.executeAppFeedbackSubmit, 'function');

    const ctx = runtime.getRuntimeContext();
    assert.equal(ctx.runtime, 'web_browser');

    const url = mailto.buildSupportMailtoUrl({
      descricao: 'Teste de import seguro.',
      tipo_label: 'Outro',
      rota: '/',
    });
    assert.match(url, /^mailto:/);
  });

  it('getRuntimeContext com mock Tauri', async () => {
    const prev = global.window?.__TAURI__;
    if (!global.window) return;
    global.window.__TAURI__ = {};
    const { getRuntimeContext } = await import('./runtimeContext.js');
    assert.equal(getRuntimeContext().runtime, 'desktop_tauri');
    if (prev === undefined) delete global.window.__TAURI__;
    else global.window.__TAURI__ = prev;
  });
});
