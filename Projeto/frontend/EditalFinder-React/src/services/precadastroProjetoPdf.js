import { jsPDF } from 'jspdf';
import { buildPreCadastroPdfModel } from './precadastroPdf/buildPreCadastroPdfModel';
import { getPdfDocumentTheme } from './precadastroPdf/pdfTheme';
import {
  renderPreCadastroDocument,
  stampFooters,
} from './precadastroPdf/renderPreCadastroPdf';

export { IMP_ECO } from './precadastroProjetoPdfConstants.js';

/**
 * Gera PDF de pre-cadastro (capa + secoes, jsPDF — nao eh print da tela).
 * @param {Record<string, unknown>} state
 * @param {{
 *   empresaNome?: string;
 *   arquivoStem?: string;
 *   cliente?: object;
 *   edital?: object | null;
 *   radarMatch?: object | null;
 *   editalTitulo?: string;
 *   preCadPdfModel?: object;
 *   sistema?: string;
 *   suppressAlerts?: boolean;
 * }} meta
 */
export function exportPrecadastroProjetoPdf(state, meta = {}) {
  const model =
    meta.preCadPdfModel ||
    buildPreCadastroPdfModel({
      cliente: meta.cliente || null,
      edital:
        meta.edital ||
        (meta.editalTitulo ? { titulo: meta.editalTitulo } : null),
      radarMatch: meta.radarMatch || null,
      formData: state,
    });

  maybeWarnIncomplete(model, meta);

  const theme = getPdfDocumentTheme(meta.cliente || {});
  const doc = new jsPDF('p', 'mm', 'a4');
  renderPreCadastroDocument(doc, model, theme, state);
  stampFooters(doc, meta.empresaNome || model.cover.empresa);

  const stem = meta.arquivoStem || model.meta.stem;
  doc.save(`${stem}_${model.meta.dataFilename}.pdf`);
}

/** Mesmo fluxo para preview em nova aba. */
export function buildPrecadastroProjetoPdfBlob(state, meta = {}) {
  const model =
    meta.preCadPdfModel ||
    buildPreCadastroPdfModel({
      cliente: meta.cliente || null,
      edital:
        meta.edital ||
        (meta.editalTitulo ? { titulo: meta.editalTitulo } : null),
      radarMatch: meta.radarMatch || null,
      formData: state,
    });

  maybeWarnIncomplete(model, meta);

  const theme = getPdfDocumentTheme(meta.cliente || {});
  const doc = new jsPDF('p', 'mm', 'a4');
  renderPreCadastroDocument(doc, model, theme, state);
  stampFooters(doc, meta.empresaNome || model.cover.empresa);

  return doc.output('blob');
}

function maybeWarnIncomplete(model, meta) {
  if (meta.suppressAlerts) return;
  const alerts = model.alertasEssenciais || [];
  if (!alerts.length) return;
  const lines = alerts.slice(0, 8).join('\n- ');
  window.alert(
    `Algumas informacoes importantes estao pendentes e serao destacadas no PDF.\n\n- ${lines}`,
  );
}
