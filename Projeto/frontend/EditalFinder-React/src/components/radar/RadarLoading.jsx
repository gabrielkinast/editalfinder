export default function RadarLoading({
  nomeCliente = '',
  processed = 0,
  total = 0,
  originalTotal = 0,
  excludedPreScore = 0,
  progressPct = 0,
}) {
  const mostrarBarra = total > 0;
  let subtitulo = 'Preparando análise…';
  if (total > 0) {
    const quem = nomeCliente ? ` para ${nomeCliente}` : '';
    subtitulo = `Analisando ${processed} de ${total} editais${quem}`;
    if (originalTotal > 0 && (originalTotal > total || excludedPreScore > 0)) {
      subtitulo += `\n(${originalTotal} no catálogo; ${excludedPreScore} excluídos em filtros rápidos antes do score)`;
    }
  }

  return (
    <div className="radar-loading" role="status" aria-live="polite">
      <div className="radar-loading-spinner" aria-hidden />
      <h3 className="radar-loading-titulo">Calculando melhores oportunidades…</h3>
      <p className="radar-loading-sub" style={{ whiteSpace: 'pre-line' }}>
        {subtitulo}
      </p>
      {mostrarBarra && (
        <>
          <div className="radar-loading-bar-wrap">
            <div className="radar-loading-bar" style={{ width: `${Math.min(100, progressPct)}%` }} />
          </div>
          <p className="radar-loading-pct">{progressPct}% concluído</p>
        </>
      )}
    </div>
  );
}
