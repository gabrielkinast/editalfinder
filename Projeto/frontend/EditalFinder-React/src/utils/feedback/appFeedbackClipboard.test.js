import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  buildManualSupportInstructions,
  copyTextToClipboard,
} from './appFeedbackClipboard.js';

describe('buildManualSupportInstructions', () => {
  it('monta Para, Assunto e Mensagem', () => {
    const text = buildManualSupportInstructions({
      supportEmail: 'Suporte.EditalFinder@gmail.com',
      subject: '[EditalFinder] Teste',
      body: 'Descrição do problema.',
    });
    assert.match(text, /^Para: Suporte\.EditalFinder@gmail\.com/);
    assert.match(text, /Assunto: \[EditalFinder\] Teste/);
    assert.match(text, /Mensagem:\nDescrição do problema\./);
  });
});

describe('copyTextToClipboard', () => {
  it('rejeita texto vazio', async () => {
    const result = await copyTextToClipboard('');
    assert.equal(result.ok, false);
    assert.equal(result.reason, 'empty_text');
  });

  it('usa navigator.clipboard quando disponível', async () => {
    let written = null;
    const original = global.navigator?.clipboard;
    Object.defineProperty(global.navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async (t) => {
          written = t;
        },
      },
    });
    try {
      const result = await copyTextToClipboard('texto de teste');
      assert.equal(result.ok, true);
      assert.equal(result.method, 'navigator_clipboard');
      assert.equal(written, 'texto de teste');
    } finally {
      if (original === undefined) {
        delete global.navigator.clipboard;
      } else {
        Object.defineProperty(global.navigator, 'clipboard', {
          configurable: true,
          value: original,
        });
      }
    }
  });

  it('usa execCommand como fallback', async () => {
    const prevDoc = global.document;
    global.document = {
      body: {
        appendChild() {},
        removeChild() {},
      },
      createElement() {
        return {
          value: '',
          style: {},
          setAttribute() {},
          select() {},
        };
      },
      execCommand(cmd) {
        return cmd === 'copy';
      },
    };
    const prevNav = global.navigator;
    Object.defineProperty(global, 'navigator', {
      configurable: true,
      value: {},
    });
    try {
      const result = await copyTextToClipboard('fallback copy');
      assert.equal(result.ok, true);
      assert.equal(result.method, 'exec_command');
    } finally {
      global.document = prevDoc;
      Object.defineProperty(global, 'navigator', {
        configurable: true,
        value: prevNav,
      });
    }
  });
});
