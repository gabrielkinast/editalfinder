/** Chips derivados do estado atual da sidebar para remoção rápida. */
export default function ActiveFiltersChips({ chips = [], onClearAll }) {
  if (!chips?.length && !onClearAll) return null;

  return (
    <div className="active-filters-chips" aria-label="Filtros ativos">
      <div className="active-filters-inner">
        {chips.map((c) => (
          <button
            key={c.key}
            type="button"
            className="filter-chip"
            onClick={c.onRemove}
            title="Remover este filtro"
          >
            {c.label}{' '}
            <span className="filter-chip-x" aria-hidden>
              ✕
            </span>
          </button>
        ))}
        {(chips.length > 2 || chips.length >= 1) && onClearAll && (
          <button type="button" className="filter-chip-clear" onClick={onClearAll}>
            Limpar filtros
          </button>
        )}
      </div>
    </div>
  );
}
