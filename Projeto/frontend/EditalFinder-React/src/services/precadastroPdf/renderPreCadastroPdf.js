import autoTable from 'jspdf-autotable';
import { IMP_ECO, IMP_SOC, IMP_AMB } from '../precadastroProjetoPdfConstants.js';
import { checkAscii } from './pdfFormatters';

const M = 14;
const BOTTOM = 26;

/** Aplicado depois que todo conteudo existir — ver precadastroProjetoPdf */
export function stampFooters(doc, clientNameShort) {
  const n = doc.internal.getNumberOfPages();
  const pw = doc.internal.pageSize.getWidth();
  const ph = doc.internal.pageSize.getHeight();
  const d = new Date().toLocaleDateString('pt-BR');
  const line = `Pre-cadastro de projeto · ${clientNameShort || 'Cliente'} · ${d}`;
  for (let i = 1; i <= n; i++) {
    doc.setPage(i);
    doc.setDrawColor(...[226, 232, 240]);
    doc.setLineWidth(0.25);
    doc.line(M, ph - BOTTOM + 10, pw - M, ph - BOTTOM + 10);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.setTextColor(...[100, 116, 139]);
    doc.text(line.slice(0, 132), M, ph - BOTTOM + 17);
    doc.text(`Pagina ${i} de ${n}`, pw - M, ph - BOTTOM + 17, { align: 'right' });
    doc.setTextColor(...[15, 23, 42]);
  }
}

function luminanceRgb([r, g, b]) {
  return r * 0.299 + g * 0.587 + b * 0.114;
}

function banner(doc, theme, topY, title, subtitle = null) {
  const pw = doc.internal.pageSize.getWidth();
  const P = theme.primaryColor;
  const h = subtitle ? 13 : 7;
  doc.setFillColor(...P);
  doc.rect(M, topY, pw - 2 * M, h, 'F');
  const lite = luminanceRgb(P);
  doc.setTextColor(...(lite > 170 ? [17, 24, 39] : [255, 255, 255]));
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(subtitle ? 10 : 9);
  doc.text(title.slice(0, 120), M + 2, topY + 5);
  if (subtitle && subtitle.trim()) {
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.8);
    doc.text(doc.splitTextToSize(subtitle, pw - 2 * M - 6)[0] || subtitle, M + 2, topY + 10);
  }
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...theme.textColor);
  doc.setFontSize(10);
  return topY + h + 4;
}

function drawCover(doc, model, theme) {
  const pw = doc.internal.pageSize.getWidth();
  const ph = doc.internal.pageSize.getHeight();
  const P = theme.primaryColor;
  const mc = model.cover;

  doc.setFillColor(...P);
  doc.rect(0, 0, pw, 64, 'F');
  const lite = luminanceRgb(P);
  doc.setTextColor(...(lite > 170 ? [17, 24, 39] : [255, 255, 255]));

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text(mc.tituloPrincipal.toUpperCase(), M, 24);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.text(doc.splitTextToSize(mc.subtituloDoc, pw - 2 * M - 48), M, 36);

  doc.setFontSize(7.8);
  doc.text(mc.dataGeracao, M, 56);
  doc.setFont('helvetica', 'bold');
  doc.text(`Completude: ${mc.statusCompletude}`, pw - M - 2, 44, { align: 'right' });
  doc.setFont('helvetica', 'normal');
  if (mc.radarBadge) doc.text(mc.radarBadge.slice(0, 64), pw - M - 2, 54, { align: 'right' });

  if (theme.logoDataUrl) {
    try {
      const fmt = theme.logoDataUrl.toLowerCase().includes('png') ? 'PNG' : 'JPEG';
      doc.addImage(theme.logoDataUrl, fmt, pw - M - 44, 6, 42, 20);
    } catch {
      /* */
    }
  }

  doc.setTextColor(...[15, 23, 42]);
  doc.setFillColor(...theme.surfaceColor);
  doc.rect(0, 64, pw, ph - 64, 'F');

  doc.setFontSize(22);
  doc.setFont('helvetica', 'bold');
  doc.text(mc.empresa, M, 86);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.setTextColor(...[71, 85, 105]);
  doc.text(doc.splitTextToSize(mc.editalOuLinha, pw - 2 * M), M, 96);

  doc.setTextColor(...[15, 23, 42]);
  doc.setFillColor(...[238, 242, 255]);
  doc.setDrawColor(...P);
  doc.setLineWidth(0.45);
  doc.rect(M, 112, pw - 2 * M, 36, 'S');

  doc.setFillColor(...[238, 242, 255]);
  doc.rect(M, 112, pw - 2 * M, 36, 'F');

  doc.setDrawColor(...P);
  doc.setLineWidth(0.35);
  doc.rect(M, 112, pw - 2 * M, 36, 'S');

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(10);
  doc.setTextColor(...P);
  doc.text('Resumo executivo (auto-texto)', M + 3, 120);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.4);
  doc.setTextColor(...[71, 85, 105]);
  doc.text(doc.splitTextToSize(mc.intro, pw - 2 * M - 8), M + 3, 128);

  autoTable(doc, {
    startY: 112 + 42,
    margin: { left: M, right: M },
    styles: {
      font: 'helvetica',
      fontSize: 8,
      overflow: 'linebreak',
      lineColor: theme.borderColor,
      lineWidth: 0.08,
      textColor: theme.textColor,
      cellPadding: 2,
    },
    theme: 'plain',
    columnStyles: {
      0: { cellWidth: 58, fillColor: [253, 253, 254], fontStyle: 'bold' },
      1: { cellWidth: 'auto' },
    },
    body: model.executiveCard.linhas.map((r) => [`${r.label}:`, `${r.value}`]),
    didParseCell: ({ section, column, cell }) => {
      if (section !== 'body' || column.index !== 1) return;
      const v = `${cell.raw ?? ''}`;
      if (v === 'Nao informado') cell.styles.textColor = [148, 163, 184];
    },
  });

  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 8,
    margin: { left: M, right: M },
    headStyles: {
      fillColor: [253, 230, 138],
      fontStyle: 'bold',
      textColor: [120, 53, 15],
    },
    styles: {
      fillColor: [255, 255, 251],
      lineColor: [253, 224, 71],
      fontSize: 7.9,
      cellPadding: 2,
    },
    theme: 'plain',
    body: [['Pendencias / alertas internos automatizados']].concat((model.alertasEssenciais || []).length ? model.alertasEssenciais.map((a) => [a]) : [['Nenhum alerta critico automatizado despontado nesta versao.']]),
    columnStyles: { 0: { cellWidth: 'auto' } },
  });

  doc.addPage();
}

function tableTwoCol(doc, theme, title, subtitle, pairs, extraY = M + 10) {
  let yStart = banner(doc, theme, extraY, title, subtitle);
  autoTable(doc, {
    startY: yStart,
    margin: { left: M, right: M },
    styles: {
      font: 'helvetica',
      fontSize: 8.3,
      lineColor: theme.borderColor,
      overflow: 'linebreak',
    },
    columnStyles: {
      0: { cellWidth: 58, fontStyle: 'bold', fillColor: [253, 253, 254] },
      1: { cellWidth: 'auto', minCellHeight: 14 },
    },
    body: pairs,
    theme: 'plain',
    didParseCell: ({ section, column, cell }) => {
      if (section !== 'body' || column.index !== 1) return;
      const v = `${cell.raw ?? ''}`;
      if (v === 'Nao informado') cell.styles.textColor = [148, 163, 184];
    },
  });
  return doc.lastAutoTable.finalY + 12;
}

/**
 * @param {import('jspdf').jsPDF} doc
 */
export function renderPreCadastroDocument(doc, model, theme, rawForm) {
  const P = theme.primaryColor;
  const S = theme.secondaryColor || theme.primaryColor;

  drawCover(doc, model, theme);

  let cursorY = banner(doc, theme, M + 12, 'Enquadramento em linhas / produtos');

  autoTable(doc, {
    startY: cursorY + 6,
    margin: { left: M, right: M },
    head: [['?', 'Linha / produto', 'Class.', '']],
    headStyles: { fillColor: P, textColor: [255, 255, 255] },
    body: model.enquadramento.linhas.map((ln) => [
      ln.sel ? '[x]' : '[ ]',
      ln.nome,
      ln.badge,
      ln.sel ? 'SELECIONADA' : '',
    ]),
    columnStyles: {
      0: { cellWidth: 16 },
      1: { cellWidth: 'auto' },
      2: { cellWidth: 28 },
      3: { cellWidth: 28, fontStyle: 'bold' },
    },
    styles: { fontSize: 8 },
    alternateRowStyles: { fillColor: [252, 252, 254] },
    didParseCell: (d) => {
      const r = `${d.cell.raw}`;
      if (d.section === 'body' && d.column.index === 3 && r.includes('SELECIONADA'))
        Object.assign(d.cell.styles, { fillColor: [236, 253, 245] });
    },
    theme: 'plain',
    lineWidth: 0,
  });

  cursorY = tableTwoCol(doc, theme, 'Contexto de aderencia (referencial)', '', [
    ['Edital relacionado', model.enquadramento.editalTitulo ? model.cover.editalOuLinha : 'Nenhum edital especifico associado'],
    ['Fonte / orgao ref.', model.enquadramento.fonteOrgao],
    ['Tipo de oportunidade', model.enquadramento.tipoOportunidade],
    ['Tipo de recurso', model.enquadramento.tipoRecurso],
    ['Perfil / temas', model.enquadramento.perfilIdeal],
    ['Requisitos declarados', model.enquadramento.requisitosResumo],
    ['Aderencia estimada', model.enquadramento.aderenciaEstimada],
    ['Motivo da recomendacao', model.enquadramento.motivoRecomendacao],
    ['Proximos passos sugeridos', model.enquadramento.proximosPassos],
  ], doc.lastAutoTable.finalY + 10);

  if (model.enquadramento.autoBullets?.length) {
    banner(doc, theme, cursorY + 10, 'Leituras automatizadas complementares');
    autoTable(doc, {
      startY: cursorY + 24,
      margin: { left: M, right: M },
      body: model.enquadramento.autoBullets.map((b) => [`- ${b}`]),
      columnStyles: { 0: { cellWidth: 'auto' } },
      styles: {
        fillColor: [252, 252, 253],
      },
      theme: 'plain',
      lineWidth: 0,
    });
  }

  doc.addPage();
  const e = model.empresa;
  const sedeCorrida = [
    e.sede?.logradouro,
    e.sede?.numero ? `n. ${e.sede.numero}` : '',
    e.sede?.complemento ? `Comp. ${e.sede.complemento}` : '',
    e.sede?.bairro ? `${e.sede.bairro}` : '',
    `${e.sede?.municipio || ''} / ${e.sede?.uf || ''}`,
    e.sede?.cep ? `CEP ${e.sede.cep}` : '',
  ]
    .map((x) => String(x).trim())
    .filter(Boolean)
    .join(', ');

  banner(doc, theme, M + 12, 'Bloco 1 — Dados da empresa / dados cadastrais');
  cursorY = tableTwoCol(doc, theme, '', '', [
    ['CNPJ', e.cnpj],
    ['Razao social', e.razao],
    ['Nome fantasia', e.fantasia],
    ['Data constituicao', e.dataConst],
    ['Inicio operacao', e.inicioOp],
    ['Sede (consolidado)', sedeCorrida || e.sede?.logradouro || 'Nao informado'],
    ['Site', e.site !== 'Nao informado' ? e.site : 'Nao informado'],
    ['Contato nome', e.contato.nome],
    ['CPF contato', e.contato.cpf || 'Nao informado'],
    ['Cargo', e.contato.cargo || 'Nao informado'],
    ['E-mail', e.contato.email],
    ['Telefone', e.contato.telefone || 'Nao informado'],
  ], M + 22);

  banner(doc, theme, cursorY + 4, 'Dados economicos da empresa');

  autoTable(doc, {
    startY: cursorY + 18,
    margin: { left: M, right: M },
    head: [['Indicador', 'Valor observado']],
    headStyles: { fillColor: S, textColor: [255, 255, 255] },
    body: model.economicoLinhas,
    alternateRowStyles: { fillColor: [252, 252, 254] },
    columnStyles: { 0: { cellWidth: 72, fontStyle: 'bold' }, 1: { cellWidth: 'auto' } },
    styles: { fontSize: 8.2 },
    theme: 'plain',
    lineWidth: 0,
    didParseCell: ({ section, column, cell }) => {
      if (section !== 'body' || column.index !== 1) return;
      if (`${cell.raw}` === 'Nao informado') cell.styles.textColor = [148, 163, 184];
    },
  });

  doc.addPage();
  const p = model.projeto;
  banner(doc, theme, M + 12, 'Bloco 2 — Informacoes do projeto / descricao da proposta');

  doc.setFillColor(...[239, 246, 255]);
  doc.setDrawColor(...P);
  doc.setLineWidth(0.4);
  doc.rect(M, M + 28, doc.internal.pageSize.getWidth() - 2 * M, 34, 'FD');

  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...P);
  doc.setFontSize(10);
  doc.text('Resumo publicavel (destaque)', M + 4, M + 36);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.4);
  doc.setTextColor(...[51, 65, 85]);
  doc.text(doc.splitTextToSize(p.resumoPublicavel, doc.internal.pageSize.getWidth() - 2 * M - 10), M + 4, M + 44);

  autoTable(doc, {
    startY: M + 70,
    margin: { left: M, right: M },
    body: [
      ['Titulo do projeto', p.titulo],
      ['Problema / oportunidade', p.problema],
      ['Objetivo geral', p.objetivo],
      ['Solucao proposta', p.solucao],
      ['Aplicacao', p.aplicacao],
      ['Desafios tecnologicos', p.desafiosTec],
      ['ICT / parcerias tecnicas', p.ict],
      ['Resultados socioeconomicos esperados', p.resultados],
      ['Concorrentes / substitutos', p.concorrentes],
      ['Diferencial inovador', p.diferencial],
      ['Produto, processo ou servico esperado', p.produtoProcessoServico],
      ['Comentarios adicionais', p.comentarios || 'Nao informado'],
      ['CNAE do projeto', p.cnaeProjeto || 'Nao informado'],
      ['UF de execucao', p.ufProjeto || 'Nao informado'],
    ],
    columnStyles: {
      0: { cellWidth: 66, fontStyle: 'bold', fillColor: [253, 253, 254] },
      1: { cellWidth: 'auto', minCellHeight: 16 },
    },
    styles: { fontSize: 8, overflow: 'linebreak' },
    theme: 'plain',
    lineWidth: 0,
    didParseCell: ({ section, column, cell }) => {
      if (section !== 'body' || column.index !== 1) return;
      if (`${cell.raw}` === 'Nao informado') cell.styles.textColor = [148, 163, 184];
    },
  });

  doc.addPage();

  banner(doc, theme, M + 14, 'Estrutura de PD&I e checklist de tipo de inovacao');

  const corp = model.innovacion.rowsOpcional.map((pair) => pair);
  autoTable(doc, {
    startY: M + 24,
    margin: { left: M, right: M },
    body: corp.length
      ? corp
      : [
          [
            'PD&I corporativo (texto)',
            rawForm?.bloco1_principais_atividades ||
              rawForm?.bloco1_pdi_infraestrutura ||
              'Nao informado',
          ],
        ],
    theme: 'plain',
    styles: {
      overflow: 'linebreak',
      fontSize: 8,
    },
    columnStyles: {
      0: {
        fillColor: [253, 253, 254],
        cellWidth: 68,
      },
      1: { cellWidth: 'auto' },
    },
  });

  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 10,
    margin: { left: M, right: M },
    headStyles: {
      fillColor: S,
      textColor: [255, 255, 255],
    },
    head: [['', 'Declaracao marcada']],
    body: model.innovacion.checks.map(([lab, ck]) => [checkAscii(ck), lab]),
    columnStyles: { 0: { cellWidth: 18 }, 1: { cellWidth: 'auto' } },
    styles: { fontSize: 8 },
    theme: 'plain',
    lineWidth: 0,
  });

  const ufs = model.usosFontes;
  banner(doc, theme, doc.lastAutoTable.finalY + 14, 'Quadro de usos / fontes (planejamento)');

  if (ufs.empty) {
    autoTable(doc, {
      startY: doc.lastAutoTable.finalY + 6,
      margin: { left: M, right: M },
      body: ufs.rows.map((r) => [{ content: ufs.message || 'Quadro ainda pendente.', colSpan: 6, styles: { fontStyle: 'italic' } }]),
    });
  } else {
    autoTable(doc, {
      startY: doc.lastAutoTable.finalY + 6,
      margin: { left: M, right: M },
      theme: 'striped',
      headStyles: { fillColor: P, fontSize: 8, textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [252, 252, 254] },
      head: [['Item financiavel', '1 lib.', '2 lib.', 'N-a lib.', 'Total fin.', 'Contrapartida']],
      body: ufs.rows.map((r) => [r.item, r.lib1 || ' ', r.lib2 || ' ', r.libN || ' ', r.totalFin || ' ', r.contrapartida || ' ']),
      columnStyles: {
        1: { cellWidth: 24 },
        2: { cellWidth: 24 },
        3: { cellWidth: 26 },
        4: { cellWidth: 28 },
        5: { cellWidth: 32, fillColor: [242, 248, 255] },
      },
      styles: { fontSize: 7.4 },
    });
  }

  doc.addPage();
  banner(doc, theme, M + 12, 'Impactos esperados (declarativos)');
  [['Impactos economicos:', IMP_ECO], ['Impactos sociais:', IMP_SOC], ['Impactos ambientais:', IMP_AMB]].forEach(([title, list], idx) => {
    const yy = idx === 0 ? M + 24 : doc.lastAutoTable.finalY + 12;
    autoTable(doc, {
      startY: yy,
      margin: { left: M, right: M },
      head: [[`${title}`, '']],
      headStyles: {
        fillColor: [247, 250, 252],
      },
      body: list.map(([k, lab]) => [checkAscii(!!rawForm[k]), lab]),
      columnStyles: { 0: { cellWidth: 18 }, 1: { cellWidth: 'auto' } },
      styles: { fontSize: 7.9 },
      theme: 'plain',
      lineWidth: 0,
    });
  });

  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 6,
    margin: { left: M, right: M },
    body: [['Outros econ.', rawForm?.bloco2_imp_eco_outros_txt || 'Nao informado'], ['Outros sociais', rawForm?.bloco2_imp_soc_outros_txt || 'Nao informado'], ['Outros amb.', rawForm?.bloco2_imp_amb_outros_txt || 'Nao informado']],
    columnStyles: { 0: { cellWidth: 36, fillColor: [253, 253, 254], fontStyle: 'bold' }, 1: { cellWidth: 'auto' } },
  });

  doc.addPage();

  banner(doc, theme, M + 12, 'Licencas condicoes financiamento e declaracao');
  banner(doc, theme, M + 28, 'Licencas e autorizacoes');
  autoTable(doc, {
    startY: M + 42,
    margin: { left: M, right: M },
    styles: {
      overflow: 'linebreak',
      fontSize: 8,
    },
    body: [['Texto oficial', `${model.licencas.texto}`], ['Aspectos declarados', `${model.licencas.aspectos}`]],
    columnStyles: { 0: { cellWidth: 46, fontStyle: 'bold', fillColor: [253, 253, 254] }, 1: { cellWidth: 'auto' } },
  });

  const condBody = [];
  condBody.push(['Percentual com ICT declarado no projeto', `${rawForm?.bloco2_pct_icts ?? model.condiciones?.pctIcts ?? ''}`.trim() || 'Nao informado']);
  condBody.push([
    `Recursos adicionais / montantes informados`,
    `${rawForm?.bloco2_recursos_adicionais_sim || ''} ${rawForm?.bloco2_recursos_adicionais_valor || ''}`.trim() || 'Nao informado',
  ]);
  model.condiciones.importacaoChecks.forEach(([lbl, on]) => {
    condBody.push([lbl, on ? '[x] marcado' : '[ ] nao marcado']);
  });

  banner(doc, theme, doc.lastAutoTable.finalY + 14, 'Condicoes complementares');

  autoTable(doc, {
    startY: doc.lastAutoTable.finalY + 6,
    margin: { left: M, right: M },
    body: condBody.concat([['Cronograma resumido (metas)', model.condiciones.cronogramaResumo || 'Nao informado']]),
    styles: {
      overflow: 'linebreak',
      fontSize: 8,
    },
    theme: 'plain',
    columnStyles: { 0: { cellWidth: 68, fillColor: [253, 253, 254], fontStyle: 'bold' }, 1: { cellWidth: 'auto' } },
    lineWidth: 0,
  });

  banner(doc, theme, doc.lastAutoTable.finalY + 10, 'Declaracao e assinatura');
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.text(doc.splitTextToSize(`${model.declaracao.texto}`, doc.internal.pageSize.getWidth() - 24), M + 2, doc.lastAutoTable.finalY + 18);

  const ph = doc.internal.pageSize.getHeight();
  const boxTop = Math.max(doc.lastAutoTable.finalY + 36, ph - 90);
  doc.setDrawColor(...theme.borderColor);
  doc.rect(M + 12, boxTop - 68, doc.internal.pageSize.getWidth() - 2 * M - 24, 64);
  doc.setFont('helvetica', 'bold');
  doc.text(`Espaco para assinatura / carimbo`, M + 16, boxTop - 58);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.5);
  doc.text(`${model.declaracao.localData}`, M + 16, boxTop - 44);
  doc.text(`Nome: ${model.declaracao.responsavel}`, M + 16, boxTop - 34);
  doc.text(`Cargo: ${model.declaracao.cargo}`, M + 16, boxTop - 24);
}
