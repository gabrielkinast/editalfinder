/**
 * Converte linha do Radar (match) em payload para pré-projeto / openPreProjetoFromOpportunity.
 * Não altera score — apenas repassa dados existentes.
 */
export function radarRowToPrecadPayload(row) {
  const ed = row?.edital || {};
  const idEdital = ed.id ?? ed.id_edital ?? row?.id;
  const scoreNum = Number(row?.score);
  const scorePct = Number.isFinite(Number(row?.scorePct))
    ? Math.round(Number(row.scorePct))
    : Number.isFinite(scoreNum)
      ? scoreNum
      : undefined;

  const edital = {
    id_edital: idEdital,
    id: idEdital,
    titulo: ed.titulo,
    fonte_recurso: ed.orgao || ed.fonte_recurso,
    origem: ed.orgao,
    tipo_oportunidade: ed.tipo_oportunidade,
    tipo_recurso: ed.tipo_recurso,
    prazo_envio: ed.prazo_envio ?? ed.dataLimite ?? ed.prazo_envio_raw,
    valor_maximo: ed.valor_maximo,
    link: ed.linkOriginal || ed.link || ed.linkInscricao || ed.link_edital,
    descricao: ed.descricao,
  };

  const radarMatch = {
    tituloEdital: ed.titulo,
    scorePct,
    compatibilidade: row?.compatibilidade,
    razoes: row?.razoes,
    razoesPositivas: row?.razoesPositivas,
    matchLinha: row?.matchLinha,
    idEdital,
    radar_penalidades: row?.radar_penalidades ?? row?.penalidades,
    alertaPrazo: row?.alertaPrazo,
    diasAtePrazo: row?.diasAtePrazo,
  };

  return { edital, radarMatch };
}
