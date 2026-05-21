/** Rótulos humanos para tipo_selecao (CHECK na tabela). */
const TIPO_SELECAO_LABELS = {
  concurso_publico: 'Concurso público',
  processo_seletivo: 'Processo seletivo',
  professor: 'Professor',
  coordenador: 'Coordenador',
  tecnico_administrativo: 'Técnico administrativo',
  estagio: 'Estágio',
  residencia: 'Residência',
  vestibular: 'Vestibular',
  bolsa_estudo: 'Bolsa',
  programa_ingresso: 'Programa de ingresso',
};

/** Rótulos para status do certame. */
const STATUS_LABELS = {
  ativo: 'Ativo',
  inscricoes_abertas: 'Inscrições abertas',
  inscricoes_encerradas: 'Inscrições encerradas',
  prova_proxima: 'Prova próxima',
  encerrado: 'Encerrado',
  suspenso: 'Suspenso',
  cancelado: 'Cancelado',
};

export function labelTipoSelecao(tipo) {
  if (tipo == null || tipo === '') return '—';
  const k = String(tipo).trim();
  return TIPO_SELECAO_LABELS[k] || k;
}

export function labelStatus(status) {
  if (status == null || status === '') return '—';
  const k = String(status).trim();
  return STATUS_LABELS[k] || k;
}

/**
 * Badges semânticos para o card (UI).
 * @param {Record<string, unknown>} row
 * @returns {{ id: string, label: string, variant: 'ok'|'warn'|'bad'|'muted'|'info' }[]}
 */
export function getConcursoBadges(row) {
  const out = [];
  if (!row) return out;

  if (row.inscricoes_abertas) {
    out.push({ id: 'insc', label: 'Inscrições abertas', variant: 'ok' });
  }
  if (row.prova_proxima) {
    out.push({ id: 'prova', label: 'Prova próxima', variant: 'warn' });
  }

  const st = String(row.status || '').toLowerCase();
  if (st === 'encerrado') {
    out.push({ id: 'enc', label: 'Encerrado', variant: 'muted' });
  }
  if (st === 'suspenso' || st === 'cancelado') {
    out.push({ id: 'st', label: labelStatus(st), variant: 'bad' });
  }

  const val = String(row.validacao_status || '').toLowerCase();
  if (val === 'incompleto') {
    out.push({ id: 'partial', label: 'Dados parciais', variant: 'warn' });
    out.push({ id: 'val', label: 'Prazos não confirmados no resumo', variant: 'muted' });
  }

  return out;
}

export function listTipoSelecaoOptions() {
  return Object.entries(TIPO_SELECAO_LABELS).map(([value, label]) => ({ value, label }));
}
