import { SOURCE_AUTO, SOURCE_CLIENTE, SOURCE_EDITAL, SOURCE_MANUAL, SOURCE_RADAR } from '../../../utils/precadastro/preCadastroTypes';

const SRC_LABEL = {
  [SOURCE_MANUAL]: 'Editado manualmente',
  [SOURCE_AUTO]: 'Sugerido automaticamente',
  [SOURCE_CLIENTE]: 'Do cadastro',
  [SOURCE_EDITAL]: 'Do edital',
  [SOURCE_RADAR]: 'Do Radar',
};

/**
 * Badge + explicação da origem dos dados inteligentes.
 */
export default function PrecadFieldMeta({ fieldIntel, fieldKey }) {
  const m = fieldIntel?.[fieldKey];
  if (!m?.source) return null;
  const label = SRC_LABEL[m.source] || m.source;

  return (
    <div className="precad-field-meta">
      <div className="precad-intel-tags">
        <span className={`precad-chip precad-chip-intel precad-chip-src-${m.source}`}>{label}</span>
        {m.needsReview ? <span className="precad-chip precad-chip-alert">Revisar</span> : null}
        {m.confidence ? (
          <span className="precad-chip precad-chip-muted">{`Confiança: ${m.confidence}`}</span>
        ) : null}
      </div>
      {m.explanation ? <p className="precad-intel-expl">{m.explanation}</p> : null}
    </div>
  );
}
