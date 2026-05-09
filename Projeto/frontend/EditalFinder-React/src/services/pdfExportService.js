import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const MARGIN = 14;
const TABLE_BOTTOM_MARGIN = 16;

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
  const dateStr = new Date().toISOString().slice(0, 10);
  for (let i = 1; i <= pageCount; i += 1) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    doc.text(`${fileStem} · ${dateStr}`, MARGIN, pageH - 8);
    doc.text(`Página ${i} de ${pageCount}`, pageW - MARGIN, pageH - 8, { align: 'right' });
    doc.setTextColor(0, 0, 0);
  }
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
 * PDF paisagem: logo/marca, título, parâmetros, tabela, rodapé com páginas.
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
  const pageW = doc.internal.pageSize.getWidth();
  const maxTextW = pageW - 2 * MARGIN;

  let y = MARGIN;

  const logoDataUrl = await loadImageAsDataUrl(logoImage);
  if (logoDataUrl) {
    const fmt = detectImageFormat(logoDataUrl);
    const maxH = 18;
    const imgW = 40;
    const imgH = maxH;
    try {
      doc.addImage(logoDataUrl, fmt, MARGIN, y, imgW, imgH, undefined, 'FAST');
    } catch {
      doc.setFontSize(12);
      doc.setTextColor(30, 80, 180);
      doc.text(brandName || 'Edital Finder', MARGIN, y + 8);
    }
    y += maxH + 6;
  } else {
    doc.setFontSize(14);
    doc.setTextColor(30, 80, 180);
    doc.text(brandName || 'Edital Finder', MARGIN, y + 6);
    y += 12;
  }
  doc.setTextColor(0, 0, 0);

  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text(reportTitle, MARGIN, y);
  y += 8;

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}`, MARGIN, y);
  y += 6;

  if (totalInDataset != null) {
    doc.text(`Exportando ${totalExported} de ${totalInDataset} registros carregados do banco.`, MARGIN, y);
    y += 6;
  } else {
    doc.text(`Registros no relatório: ${totalExported}`, MARGIN, y);
    y += 6;
  }

  doc.setFontSize(9);
  doc.setTextColor(55, 55, 55);
  doc.text('Parâmetros do relatório:', MARGIN, y);
  y += 5;
  filterLines.forEach((line) => {
    doc.splitTextToSize(line, maxTextW).forEach((chunk) => {
      doc.text(chunk, MARGIN, y);
      y += 4;
    });
  });
  doc.setTextColor(0, 0, 0);
  y += 4;

  const safeStartY = Math.min(y + 2, doc.internal.pageSize.getHeight() - 40);

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
