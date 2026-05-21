import { memo, useMemo } from 'react';
import CardEditalRadar from './CardEditalRadar';
import { sanitizeRadarResults } from '../../utils/radar/radarResultShape';

/**
 * Grid não virtualizado — memoizado para evitar re-render em massa.
 */
function RadarResultsGrid({
  rows,
  staleOverlay,
  sectionTitle,
  showSectionTitle,
  favoritosRemote,
  favoritosCliente,
  favHook,
  onFavoritar,
}) {
  const safeRows = useMemo(
    () => sanitizeRadarResults(rows, { source: 'grid', logInvalid: false }),
    [rows],
  );

  if (!safeRows.length) return null;

  const resolveFavorito = (edital) => {
    if (!edital?.id) return false;
    return favoritosRemote
      ? favHook.isFavorite(edital)
      : favoritosCliente?.has?.(edital.id);
  };

  return (
    <section className={`radar-secao${staleOverlay ? ' radar-secao--stale' : ''}`}>
      {showSectionTitle && sectionTitle && (
        <h3 className="radar-secao-titulo">{sectionTitle}</h3>
      )}
      <div className="radar-grid">
        {safeRows.map((row) => (
          <CardEditalRadar
            key={String(row.edital.id)}
            edital={row.edital}
            score={row.score}
            compatibilidade={row.compatibilidade}
            razoes={row.razoes}
            razoesPositivas={row.razoesPositivas ?? row.razoes}
            detalhes={row.detalhes}
            criterioMeta={row.criterioMeta}
            matchLinha={row.matchLinha}
            fonteMatch={row.fonteMatch}
            radarBadges={row.radar_badges}
            radarAlertas={row.radar_alertas}
            radarDimensoes={row.radar_dimensoes}
            radarPenalidades={row.radar_penalidades}
            prazoInfo={row.prazoInfo}
            expirado={row.expirado}
            favorito={resolveFavorito(row.edital)}
            onFavoritar={onFavoritar}
          />
        ))}
      </div>
    </section>
  );
}

export default memo(RadarResultsGrid);
