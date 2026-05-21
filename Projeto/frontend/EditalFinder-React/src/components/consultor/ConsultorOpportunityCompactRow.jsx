import { useNavigate } from 'react-router-dom';
import { getOpportunitySelectionKey } from '../../utils/consultor/opportunitySelection';
import {
  compatClass,
  prazoBadgeClass,
  rowDisplayFields,
} from '../../utils/consultor/consultorOpportunityRowDisplay';

function alertasCurto(row) {
  const raw = row?.radar_alertas ?? row?.alertas;
  if (!Array.isArray(raw) || !raw.length) return null;
  const texts = raw.slice(0, 2).map((a) => {
    if (typeof a === 'string') return a;
    if (a?.text) return String(a.text);
    if (a?.label) return String(a.label);
    return '';
  });
  const joined = texts.filter(Boolean).join(' · ');
  return joined || null;
}

/**
 * Linha compacta de oportunidade (modal “todas” e listas densas).
 * @param {'default'|'sheet'} [variant] — sheet = layout planilha no modal da carteira
 */
export default function ConsultorOpportunityCompactRow({
  row,
  isSelected = false,
  onToggleSelect,
  showEditalLink = true,
  onOpenRadar,
  variant = 'default',
}) {
  const navigate = useNavigate();
  const selKey = getOpportunitySelectionKey(row);
  const d = rowDisplayFields(row);
  const alertas = alertasCurto(row);
  const motivoLine = d.motivo || alertas;
  const editalPath = d.id != null ? `/edital/${String(d.id).replace(/^manual-/, '')}` : null;

  if (variant === 'sheet') {
    return (
      <li
        className={`consultor-opp-sheet-row ${isSelected ? 'consultor-opp-sheet-row--selected' : ''}`}
        data-sel-key={selKey}
      >
        {onToggleSelect ? (
          <label className="consultor-opp-sheet-check" onClick={(e) => e.stopPropagation()}>
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => {
                e.stopPropagation();
                onToggleSelect(row, selKey, e.target.checked);
              }}
              onClick={(e) => e.stopPropagation()}
              aria-label={`Selecionar ${d.titulo}`}
            />
          </label>
        ) : null}
        <div className="consultor-opp-sheet-body">
          <div className="consultor-opp-sheet-line1">
            <button
              type="button"
              className="consultor-opp-sheet-title"
              onClick={() => editalPath && navigate(editalPath)}
              title={d.titulo}
              disabled={!editalPath}
            >
              {d.titulo}
            </button>
            <span className={`consultor-compat-badge ${compatClass(d.compatibilidade)}`}>
              {d.score}%
            </span>
          </div>
          <div className="consultor-opp-sheet-line2">
            <span className="consultor-opp-sheet-meta" title={`${d.fonte} · ${d.prazoLabel}`}>
              {d.fonte} · {d.prazoLabel}
              {d.tipoApoio && d.tipoApoio !== '—' ? ` · ${d.tipoApoio}` : ''}
            </span>
          </div>
          <div className="consultor-opp-sheet-line3">
            {motivoLine ? (
              <span className="consultor-opp-sheet-motivo" title={motivoLine}>
                {motivoLine}
              </span>
            ) : (
              <span className="consultor-opp-sheet-motivo consultor-opp-sheet-motivo--empty">—</span>
            )}
            <div className="consultor-opp-sheet-actions">
              {showEditalLink && editalPath ? (
                <button
                  type="button"
                  className="consultor-opp-sheet-btn"
                  onClick={() => navigate(editalPath)}
                >
                  Ver edital
                </button>
              ) : null}
              {onOpenRadar ? (
                <button type="button" className="consultor-opp-sheet-btn" onClick={() => onOpenRadar(row)}>
                  Radar
                </button>
              ) : null}
            </div>
          </div>
        </div>
      </li>
    );
  }

  return (
    <li
      className={`consultor-opp-grid-item consultor-opp-grid-item--modal ${isSelected ? 'consultor-opp-grid-item--selected' : ''}`}
      data-sel-key={selKey}
    >
      {onToggleSelect ? (
        <label className="consultor-opp-grid-check" onClick={(e) => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => {
              e.stopPropagation();
              onToggleSelect(row, selKey, e.target.checked);
            }}
            onClick={(e) => e.stopPropagation()}
            aria-label={`Selecionar ${d.titulo}`}
          />
        </label>
      ) : null}
      <div className="consultor-opp-grid-body">
        <div className="consultor-opp-grid-row1">
          <button
            type="button"
            className="consultor-opp-grid-title"
            onClick={() => editalPath && navigate(editalPath)}
            title={d.titulo}
          >
            {d.titulo}
          </button>
          <span className={`consultor-compat-badge ${compatClass(d.compatibilidade)}`}>
            {d.compatibilidade} · {d.score}%
          </span>
        </div>
        <div className="consultor-opp-grid-row2">
          <div className="consultor-opp-grid-meta">
            <span className="consultor-opp-grid-fonte" title={d.fonte}>
              {d.fonte}
            </span>
            <span className={`consultor-opp-grid-prazo ${prazoBadgeClass(d.prazoStatus)}`}>
              {d.prazoLabel}
            </span>
          </div>
          <div className="consultor-opp-grid-actions">
            {showEditalLink && editalPath ? (
              <button
                type="button"
                className="consultor-opp-sheet-btn consultor-opp-grid-link"
                onClick={() => navigate(editalPath)}
              >
                Ver edital
              </button>
            ) : null}
            {onOpenRadar ? (
              <button
                type="button"
                className="consultor-opp-sheet-btn consultor-opp-grid-link"
                onClick={() => onOpenRadar(row)}
              >
                Radar
              </button>
            ) : null}
          </div>
        </div>
        {motivoLine ? (
          <p className="consultor-opp-grid-motivo" title={motivoLine}>
            {motivoLine}
          </p>
        ) : null}
      </div>
    </li>
  );
}
