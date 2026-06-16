import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import {
  buildEditaisPdfColumns,
  buildEditaisPdfRows,
  buildPdfFiltersSummary,
} from '../utils/pdf/editaisPdfFormatters.js';

const MARGIN = 14;
const TABLE_BOTTOM_MARGIN = 16;

/** Larguras fixas (mm) — soma ~253 em A4 paisagem com margens 14. */
const EDITAIS_PDF_COLUMN_STYLES = {
  titulo: { cellWidth: 50 },
  status: { cellWidth: 24 },
  fonte: { cellWidth: 26 },
  tipo: { cellWidth: 24 },
  area: { cellWidth: 34 },
  local: { cellWidth: 20 },
  situacao: { cellWidth: 20 },
  prazo: { cellWidth: 20 },
  valor: { cellWidth: 22 },
  qualidade: { cellWidth: 14 },
};

function detectImageFormat(dataUrl) {
  if (!dataUrl || typeof dataUrl !== 'string') return 'PNG';
  if (dataUrl.includes('image/jpeg') || dataUrl.includes('image/jpg')) return 'JPEG';
  if (dataUrl.includes('image/png')) return 'PNG';
  if (dataUrl.includes('image/webp')) return 'WEBP';
  return 'PNG';
}

/**
 * Converte URL de imagem em data URL (útil para logo em http(s)).
 */
function loadImageAsDataUrl(src) {
  return new Promise((resolve) => {
    if (!src || typeof src !== 'string') {
      resolve(null);
      return;
    }
    if (src.startsWith('data:')) {
      resolve(src);
      return;
    }
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        resolve(canvas.toDataURL('image/png'));
      } catch {
        resolve(null);
      }
    };
    img.onerror = () => resolve(null);
    img.src = src;
  });
}

function addPageFooters(doc, fileStem) {
  const pageCount = doc.internal.getNumberOfPages();
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  for (let i = 1; i <= pageCount; i += 1) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(100, 100, 100);
    doc.text('Gerado pelo EditalFinder', MARGIN, pageH - 6);
    doc.text(`Página ${i} de ${pageCount}`, pageW - MARGIN, pageH - 6, { align: 'right' });
    doc.setTextColor(0, 0, 0);
  }
}

async function drawReportHeader(doc, {
  brandName,
  logoImage,
  reportTitle,
  totalExported,
  totalInDataset,
  filtersSummary,
  extraLines = [],
}) {
  const pageW = doc.internal.pageSize.getWidth();
  const maxTextW = pageW - 2 * MARGIN;
  let y = MARGIN;

  const logoDataUrl = await loadImageAsDataUrl(logoImage);
  if (logoDataUrl) {
    const fmt = detectImageFormat(logoDataUrl);
    const maxH = 18;
    try {
      doc.addImage(logoDataUrl, fmt, MARGIN, y, 40, maxH, undefined, 'FAST');
    } catch {
      doc.setFontSize(12);
      doc.setTextColor(30, 80, 180);
      doc.text(brandName || 'EditalFinder', MARGIN, y + 8);
    }
    y += maxH + 6;
  } else {
    doc.setFontSize(14);
    doc.setTextColor(30, 80, 180);
    doc.text(brandName || 'EditalFinder', MARGIN, y + 6);
    y += 12;
  }
  doc.setTextColor(0, 0, 0);

  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text(reportTitle, MARGIN, y);
  y += 8;

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.text(
    `Gerado em: ${new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}`,
    MARGIN,
    y,
  );
  y += 6;

  if (totalInDataset != null) {
    doc.text(`Total exportado: ${totalExported} de ${totalInDataset} registros.`, MARGIN, y);
  } else {
    doc.text(`Total exportado: ${totalExported}`, MARGIN, y);
  }
  y += 6;

  extraLines.forEach((line) => {
    doc.splitTextToSize(line, maxTextW).forEach((chunk) => {
      doc.text(chunk, MARGIN, y);
      y += 4;
    });
  });

  if (filtersSummary) {
    doc.setFontSize(9);
    doc.setTextColor(55, 55, 55);
    doc.splitTextToSize(filtersSummary, maxTextW).forEach((chunk) => {
      doc.text(chunk, MARGIN, y);
      y += 4;
    });
    doc.setTextColor(0, 0, 0);
  }

  return Math.min(y + 4, doc.internal.pageSize.getHeight() - 40);
}

/**
 * Texto legível dos filtros da dashboard (edit).
 */
export function formatDashboardFiltersForPdf(filters, globalSearch) {
  const lines = [];
  if (globalSearch?.trim()) lines.push(`Busca global: "${globalSearch.trim()}"`);

  if (filters?.resourceType || filters?.resourceTypeLegacy) {
    lines.push(`Tipo (legado compat): ${filters.resourceType ?? filters.resourceTypeLegacy}`);
  }
  if (filters?.tipoRecurso) lines.push(`Tipo recurso (tabela): ${filters.tipoRecurso}`);
  if (filters?.tipoOportunidade) lines.push(`Tipo de oportunidade: ${filters.tipoOportunidade}`);
  if (filters?.toggleIncluirEncerrados) lines.push('Incluir encerrados: sim');
  if (filters?.toggleIncluirSuspeitos) lines.push('Incluir suspeitos: sim');
  if (filters?.toggleMostrarInativos) lines.push('Mostrar inativos: sim');
  if (filters?.regiao || filters?.regiaoLegacy) {
    lines.push(`Região: ${filters.regiao ?? filters.regiaoLegacy}`);
  }
  if (filters?.pais) lines.push(`País: ${filters.pais}`);
  if (filters?.uf) lines.push(`UF: ${filters.uf}`);
  if (filters?.cidadeBusca) lines.push(`Cidade: ${filters.cidadeBusca}`);
  if (filters?.fonteBusca) lines.push(`Fonte (busca): ${filters.fonteBusca}`);
  if (filters?.perfil) lines.push(`Perfil (compatibilidade ≥ 70%): ${filters.perfil}`);

  if (filters?.valorPreset) lines.push(`Faixa preset valor: ${filters.valorPreset}`);
  if (filters?.valorMin !== '' && filters?.valorMin != null && !Number.isNaN(parseFloat(filters.valorMin))) {
    lines.push(`Valor mínimo (R$): ${filters.valorMin}`);
  }
  if (filters?.valorMax !== '' && filters?.valorMax != null && !Number.isNaN(parseFloat(filters.valorMax))) {
    lines.push(`Valor máximo (R$): ${filters.valorMax}`);
  }

  const activeAreas = Object.entries(filters?.areas || {})
    .filter(([, on]) => on)
    .map(([name]) => name);
  if (activeAreas.length) lines.push(`Áreas: ${activeAreas.join(', ')}`);

  const activeOrgs = Object.entries(filters?.orgs || {})
    .filter(([, on]) => on)
    .map(([name]) => name.toUpperCase());
  if (activeOrgs.length) lines.push(`Órgãos: ${activeOrgs.join(', ')}`);

  const fontesSel = Object.entries(filters?.fontesSelectedKeys || {})
    .filter(([, on]) => on)
    .map(([k]) => k);
  if (fontesSel.length) lines.push(`Fontes: ${fontesSel.join('; ')}`);

  const semanticStatus = Object.entries(filters?.semanticStatusSelections || {})
    .filter(([, on]) => on)
    .map(([k]) => k.replace(/_/g, ' '));
  if (semanticStatus.length) lines.push(`Status semântico: ${semanticStatus.join(', ')}`);

  if (lines.length === 0) lines.push('Nenhum filtro adicional (todos os registros visíveis após busca).');
  return lines;
}

export function formatFeedFiltersForPdf(sidebarFilters, globalSearch) {
  const lines = [];
  if (globalSearch?.trim()) lines.push(`Busca: "${globalSearch.trim()}"`);
  if (sidebarFilters?.somenteAtivos) lines.push('Somente registros ativos: sim');
  if (sidebarFilters?.fonte_recurso) lines.push(`Fonte recurso: ${sidebarFilters.fonte_recurso}`);
  if (sidebarFilters?.regiao) lines.push(`Região: ${sidebarFilters.regiao}`);
  if (sidebarFilters?.pais) lines.push(`País: ${sidebarFilters.pais}`);
  if (sidebarFilters?.validacao_status) lines.push(`Validação: ${sidebarFilters.validacao_status}`);
  if (sidebarFilters?.tipo_conteudo) lines.push(`Tipo / conteúdo: ${sidebarFilters.tipo_conteudo}`);
  if (sidebarFilters?.tag) lines.push(`Tag: ${sidebarFilters.tag}`);
  if (lines.length === 0) lines.push('Nenhum filtro adicional (lista completa carregada).');
  return lines;
}

/**
 * PDF tabular de editais — layout dedicado (FRONTEND 1.1D).
 * Não captura a UI; usa jsPDF + autoTable em paisagem com 9 colunas fixas.
 */
export async function exportEditaisToPdf(editais = [], options = {}) {
  const rows = buildEditaisPdfRows(editais);
  const columns = buildEditaisPdfColumns();
  const doc = new jsPDF('l', 'mm', 'a4');

  const filterLines = [
    ...(options.filterLinesExtra || []),
    ...formatDashboardFiltersForPdf(options.filters, options.globalSearch),
  ];

  const startY = await drawReportHeader(doc, {
    brandName: options.brandName,
    logoImage: options.logoImage,
    reportTitle: options.reportTitle || 'Relatório de editais',
    totalExported: rows.length,
    totalInDataset: options.totalInDataset ?? null,
    filtersSummary: buildPdfFiltersSummary(filterLines),
  });

  autoTable(doc, {
    columns,
    body: rows,
    startY,
    theme: 'grid',
    styles: {
      fontSize: 7,
      cellPadding: 1.5,
      overflow: 'linebreak',
      valign: 'top',
      minCellHeight: 4,
    },
    headStyles: {
      fillColor: [74, 108, 247],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      halign: 'center',
    },
    columnStyles: EDITAIS_PDF_COLUMN_STYLES,
    margin: { left: MARGIN, right: MARGIN, bottom: TABLE_BOTTOM_MARGIN },
    tableWidth: 'wrap',
    showHead: 'everyPage',
    rowPageBreak: 'auto',
  });

  const stem = options.fileNameStem || 'editais';
  addPageFooters(doc, stem);
  doc.save(`${stem}_${new Date().toISOString().split('T')[0]}.pdf`);
}

export { buildEditaisPdfRows, buildEditaisPdfColumns, buildPdfFiltersSummary };

/**
 * PDF paisagem genérico (notícias, feeds) — mantém assinatura pública.
 */
export async function exportLandscapeTablePdf({
  fileNameStem,
  reportTitle,
  brandName,
  logoImage,
  filterLines = [],
  totalExported,
  totalInDataset,
  tableHead,
  tableBody,
  autoTableOptions = {},
}) {
  const doc = new jsPDF('l', 'mm', 'a4');

  const safeStartY = await drawReportHeader(doc, {
    brandName,
    logoImage,
    reportTitle,
    totalExported,
    totalInDataset,
    filtersSummary: buildPdfFiltersSummary(filterLines),
  });

  const { styles: optsStyles, headStyles: optsHeadStyles, ...restAuto } = autoTableOptions;

  autoTable(doc, {
    head: tableHead,
    body: tableBody,
    startY: safeStartY,
    styles: {
      fontSize: 8,
      cellPadding: 2,
      overflow: 'linebreak',
      minCellHeight: 4,
      ...optsStyles,
    },
    headStyles: {
      fillColor: [74, 108, 247],
      textColor: [255, 255, 255],
      ...optsHeadStyles,
    },
    margin: { left: MARGIN, right: MARGIN, bottom: TABLE_BOTTOM_MARGIN },
    tableWidth: 'auto',
    ...restAuto,
  });

  addPageFooters(doc, fileNameStem);

  doc.save(`${fileNameStem}_${new Date().toISOString().split('T')[0]}.pdf`);
}
