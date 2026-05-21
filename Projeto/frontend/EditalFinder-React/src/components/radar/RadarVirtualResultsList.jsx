import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { VariableSizeList as List } from 'react-window';
import CardEditalRadar from './CardEditalRadar';
import {
  RADAR_VIRTUAL_OVERSCAN,
  RADAR_VIRTUAL_ROW_HEIGHT,
  RADAR_VIRTUAL_SECTION_HEIGHT,
} from '../../constants/radarVirtual';
import { radarRenderPerfCycle, radarRenderPerfEvent } from '../../utils/radarRenderPerfLog';

function useGridColumnCount() {
  const [cols, setCols] = useState(1);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mqLg = window.matchMedia('(min-width: 1100px)');
    const mqMd = window.matchMedia('(min-width: 700px)');
    const update = () => {
      if (mqLg.matches) setCols(3);
      else if (mqMd.matches) setCols(2);
      else setCols(1);
    };
    update();
    mqLg.addEventListener('change', update);
    mqMd.addEventListener('change', update);
    return () => {
      mqLg.removeEventListener('change', update);
      mqMd.removeEventListener('change', update);
    };
  }, []);

  return cols;
}

function useContainerSize(ref) {
  const [size, setSize] = useState({ width: 0, height: 480 });

  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver((entries) => {
      const cr = entries[0]?.contentRect;
      if (!cr) return;
      const h = Math.max(320, Math.min(cr.height, window.innerHeight - 120));
      setSize({ width: Math.floor(cr.width), height: Math.floor(h) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [ref]);

  return size;
}

/**
 * Converte listas “Melhores” + “Demais” em linhas virtualizáveis (seção + grid row).
 */
export function buildRadarVirtualEntries(melhores, demais, columnCount) {
  const entries = [];
  const pushRows = (rows, prefix) => {
    for (let i = 0; i < rows.length; i += columnCount) {
      const slice = rows.slice(i, i + columnCount);
      const id = slice.map((r) => r.edital?.id ?? i).join('-');
      entries.push({ type: 'row', id: `${prefix}-${id}`, items: slice });
    }
  };

  if (melhores.length > 0) {
    entries.push({ type: 'section', id: 'sec-melhores', title: '⭐ Melhores Oportunidades' });
    pushRows(melhores, 'm');
  }
  if (demais.length > 0) {
    if (melhores.length > 0) {
      entries.push({ type: 'section', id: 'sec-demais', title: 'Outros Editais' });
    }
    pushRows(demais, 'd');
  }
  return entries;
}

export default function RadarVirtualResultsList({
  melhoresOportunidades,
  demais,
  staleOverlay,
  clienteId,
  isPartial,
  isFull,
  favoritosRemote,
  favoritosCliente,
  favHook,
  onFavoritar,
}) {
  const wrapRef = useRef(null);
  const listRef = useRef(null);
  const columnCount = useGridColumnCount();
  const { width: listWidth, height: listHeight } = useContainerSize(wrapRef);

  const itemsTotal = melhoresOportunidades.length + demais.length;

  const entries = useMemo(
    () => buildRadarVirtualEntries(melhoresOportunidades, demais, columnCount),
    [melhoresOportunidades, demais, columnCount],
  );

  const getItemSize = useCallback(
    (index) => {
      const e = entries[index];
      if (!e) return RADAR_VIRTUAL_ROW_HEIGHT;
      return e.type === 'section' ? RADAR_VIRTUAL_SECTION_HEIGHT : RADAR_VIRTUAL_ROW_HEIGHT;
    },
    [entries],
  );

  useEffect(() => {
    listRef.current?.resetAfterIndex(0);
  }, [entries, columnCount]);

  useEffect(() => {
    radarRenderPerfCycle(
      {
        virtual_enabled: true,
        items_total: itemsTotal,
        render_items_count: entries.length,
        cliente_id: clienteId ?? null,
        partial: !!isPartial,
        full: !!isFull,
        column_count: columnCount,
      },
      (end) => {
        radarRenderPerfEvent('virtual_enabled', {
          cliente_id: clienteId,
          items_total: itemsTotal,
          virtual_rows: entries.length,
          render_ms: end.render_ms,
        });
      },
    );
  }, [entries.length, itemsTotal, clienteId, isPartial, isFull, columnCount]);

  const resolveFavorito = useCallback(
    (edital) =>
      favoritosRemote ? favHook.isFavorite(edital) : favoritosCliente.has(edital.id),
    [favoritosRemote, favHook, favoritosCliente],
  );

  const Row = useCallback(
    ({ index, style }) => {
      const entry = entries[index];
      if (!entry) return null;

      if (entry.type === 'section') {
        return (
          <div style={style} className="radar-virtual-section-wrap">
            <h3 className="radar-secao-titulo radar-virtual-section-title">{entry.title}</h3>
          </div>
        );
      }

      return (
        <div style={style} className="radar-virtual-row-wrap">
          <div
            className="radar-grid radar-grid--virtual-row"
            style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}
          >
            {entry.items.map((row) => (
              <CardEditalRadar
                key={row.edital.id}
                edital={row.edital}
                score={row.score}
                compatibilidade={row.compatibilidade}
                razoes={row.razoes}
                detalhes={row.detalhes}
                criterioMeta={row.criterioMeta}
                matchLinha={row.matchLinha}
                fonteMatch={row.fonteMatch}
                radarBadges={row.radar_badges}
                radarPenalidades={row.radar_penalidades}
                prazoInfo={row.prazoInfo}
                expirado={row.expirado}
                favorito={resolveFavorito(row.edital)}
                onFavoritar={onFavoritar}
              />
            ))}
          </div>
        </div>
      );
    },
    [entries, columnCount, resolveFavorito, onFavoritar],
  );

  const handleItemsRendered = useCallback(
    ({ visibleStartIndex, visibleStopIndex }) => {
      const visibleCount =
        visibleStartIndex >= 0 && visibleStopIndex >= visibleStartIndex
          ? visibleStopIndex - visibleStartIndex + 1
          : 0;
      radarRenderPerfEvent('visible_range', {
        cliente_id: clienteId,
        visible_start: visibleStartIndex,
        visible_stop: visibleStopIndex,
        visible_items_count: visibleCount,
        render_items_count: entries.length,
        items_total: itemsTotal,
      });
    },
    [clienteId, entries.length, itemsTotal],
  );

  if (entries.length === 0) return null;

  const listW = listWidth > 0 ? listWidth : undefined;

  return (
    <section
      className={`radar-secao radar-secao--virtual${staleOverlay ? ' radar-secao--stale' : ''}`}
      aria-label="Oportunidades do radar"
    >
      <div ref={wrapRef} className="radar-virtual-list-wrap">
        {listW != null && listW > 0 && (
          <List
            ref={listRef}
            height={listHeight}
            width={listW}
            itemCount={entries.length}
            itemSize={getItemSize}
            overscanCount={RADAR_VIRTUAL_OVERSCAN}
            onItemsRendered={handleItemsRendered}
          >
            {Row}
          </List>
        )}
      </div>
    </section>
  );
}
