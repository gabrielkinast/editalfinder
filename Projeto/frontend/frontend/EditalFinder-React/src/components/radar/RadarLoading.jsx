export default function RadarLoading({
  nomeCliente = '',
  processed = 0,
  total = 0,
  originalTotal = 0,
  excludedPreScore = 0,
  progressPct = 0,
}) {
  const mostrarBarra = total > 0;
  const pct = Math.min(100, Math.max(0, progressPct));

  return (
    <div className="radar-loading" role="status" aria-live="polite">
      <div className="radar-loading-spinner" aria-hidden />
      <h3 className="radar-loading-titulo">
        Medindo a compatibilidade entre o perfil e cada edital
      </h3>
      <p className="radar-loading-lead">
        {nomeCliente ? (
          <>
            Cliente: <strong>{nomeCliente}</strong>. Isso pode levar alguns segundos — evite fechar a página.
          </>
        ) : (
          <>Isso pode levar alguns segundos — evite fechar a página.</>
        )}
      </p>

      {mostrarBarra && (
        <>
          <p className="radar-loading-progress-main">
            <strong>{processed}</strong> de <strong>{total}</strong> editais analisados com o score completo
          </p>
          <div className="radar-loading-bar-wrap">
            <div className="radar-loading-bar" style={{ width: `${pct}%` }} />
          </div>
          <p className="radar-loading-pct" aria-label={`Progresso ${pct} por cento`}>
            {pct}% concluído
          </p>
        </>
      )}

      {!mostrarBarra && originalTotal > 0 && (
        <p className="radar-loading-progress-main">
          Preparando a lista a partir de <strong>{originalTotal}</strong> editais no catálogo…
        </p>
      )}

      {(originalTotal > 0 || excludedPreScore > 0) && (
        <div className="radar-loading-tech" aria-label="Detalhes numéricos">
          {originalTotal > 0 && (
            <span>
              Catálogo total: <strong>{originalTotal}</strong>
            </span>
          )}
          {total > 0 && (
            <>
              {' · '}
              <span>
                Elegíveis após filtros rápidos: <strong>{total}</strong>
              </span>
            </>
          )}
          {excludedPreScore > 0 && (
            <>
              {' · '}
              <span>
                Excluídos antes do score: <strong>{excludedPreScore}</strong>
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
