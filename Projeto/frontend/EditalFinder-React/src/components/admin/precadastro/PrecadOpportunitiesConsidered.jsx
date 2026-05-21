import { formatOportunidadesConsideradasText } from '../../../utils/precadastro/multiOpportunityAutofill';
import { partitionSelectedOpportunities } from '../../../utils/consultor/opportunitySelection';

function parseOportunidadesJson(raw) {
  if (!raw || !String(raw).trim()) return null;
  try {
    const j = JSON.parse(raw);
    return Array.isArray(j) ? j : null;
  } catch {
    return null;
  }
}

function toNormalizedRow(p) {
  return {
    key: p.key,
    titulo: p.titulo,
    scorePct: p.score ?? p.scorePct,
    compatibilidade: p.compatibilidade,
    fonte_recurso: p.fonte_recurso,
    prazo_envio: p.prazo ?? p.prazo_envio,
    link: p.link,
    grupo: p.grupo,
  };
}

function OppCompactLine({ opp, highlight = false }) {
  const titulo = opp.titulo || '—';
  const score = opp.scorePct ?? opp.score ?? '—';
  const prazo = opp.prazo_envio ? ` · prazo ${opp.prazo_envio}` : '';
  const fonte = opp.fonte_recurso ? ` · ${opp.fonte_recurso}` : '';
  return (
    <div className={`precad-opp-line ${highlight ? 'precad-opp-line--principal' : ''}`}>
      <span className="precad-opp-line-score">[{score}%]</span>
      <span className="precad-opp-line-text" title={titulo}>
        {titulo}
        {fonte}
        {prazo}
      </span>
      {opp.link ? (
        <a
          className="precad-opp-line-link"
          href={opp.link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
        >
          Abrir
        </a>
      ) : null}
    </div>
  );
}

/**
 * Bloco “Oportunidades consideradas” (multi-seleção do Workspace).
 */
export default function PrecadOpportunitiesConsidered({ form, oportunidadesSelecionadas = null }) {
  const fromProp = Array.isArray(oportunidadesSelecionadas) ? oportunidadesSelecionadas : null;
  const parsed = fromProp ? null : parseOportunidadesJson(form?.bloco_estr_oportunidades_selecionadas);

  let rows = [];
  if (fromProp?.length) {
    rows = fromProp.map((o) => ({ ...toNormalizedRow(o), grupo: 'complementar' }));
    const primary = [...fromProp].sort((a, b) => (b.scorePct || 0) - (a.scorePct || 0))[0];
    if (primary?.key) {
      rows = rows.map((r) =>
        r.key === primary.key ? { ...r, grupo: 'principal' } : r,
      );
    }
  } else if (parsed?.length) {
    rows = parsed.map(toNormalizedRow);
  }

  if (!rows.length) return null;

  const normalizedForPartition = fromProp || rows;
  const primary =
    fromProp?.length
      ? [...fromProp].sort((a, b) => (b.scorePct || 0) - (a.scorePct || 0))[0]
      : rows.find((r) => r.grupo === 'principal') || rows[0];

  const part = partitionSelectedOpportunities(
    fromProp || rows.map((r) => ({
      key: r.key,
      titulo: r.titulo,
      scorePct: r.scorePct,
      compatibilidade: r.compatibilidade,
      fonte_recurso: r.fonte_recurso,
      prazo_envio: r.prazo_envio,
      link: r.link,
    })),
    primary,
  );

  const principalRow = part.primary
    ? {
        titulo: part.primary.titulo,
        scorePct: part.primary.scorePct,
        compatibilidade: part.primary.compatibilidade,
        fonte_recurso: part.primary.fonte_recurso,
        prazo_envio: part.primary.prazo_envio,
        link: part.primary.link,
      }
    : rows.find((r) => r.grupo === 'principal') || rows[0];

  const complementares =
    part.complementares.length > 0
      ? part.complementares.map((o) => ({
          titulo: o.titulo,
          scorePct: o.scorePct,
          compatibilidade: o.compatibilidade,
          fonte_recurso: o.fonte_recurso,
          prazo_envio: o.prazo_envio,
          link: o.link,
        }))
      : rows.filter((r) => r.grupo === 'complementar').slice(0, 5);

  const observacao =
    part.observacao.length > 0
      ? part.observacao.map((o) => ({
          titulo: o.titulo,
          scorePct: o.scorePct,
          fonte_recurso: o.fonte_recurso,
          prazo_envio: o.prazo_envio,
          link: o.link,
        }))
      : rows.filter((r) => r.grupo === 'observacao');

  const textoFallback = formatOportunidadesConsideradasText(fromProp || rows, principalRow);

  return (
    <section className="precad-opps-considered consultor-section--inline">
      <h3 className="precad-section-title">Oportunidades consideradas</h3>
      <p className="precad-section-hint precad-muted small">
        {rows.length} no conjunto — principal com maior compatibilidade; até 5 complementares no relatório.
      </p>

      <div className="precad-opps-compact">
        {principalRow ? (
          <div className="precad-opps-group precad-opps-group--principal">
            <h4 className="precad-opps-group-title">Principal</h4>
            <div className="precad-opp-card precad-opp-card--hero">
              <OppCompactLine opp={principalRow} highlight />
            </div>
          </div>
        ) : null}

        {complementares.length > 0 ? (
          <div className="precad-opps-group">
            <h4 className="precad-opps-group-title">Complementares</h4>
            {complementares.map((o, i) => (
              <OppCompactLine key={o.key || `comp-${i}`} opp={o} />
            ))}
          </div>
        ) : null}

        {observacao.length > 0 ? (
          <details className="precad-opps-details precad-opps-details--obs">
            <summary>Ver mais {observacao.length} oportunidade{observacao.length === 1 ? '' : 's'} em observação</summary>
            <div className="precad-opps-obs-list">
              {observacao.map((o, i) => (
                <OppCompactLine key={o.key || `obs-${i}`} opp={o} />
              ))}
            </div>
          </details>
        ) : null}
      </div>

      <details className="precad-opps-details">
        <summary>Ver resumo textual completo</summary>
        <pre className="precad-opps-considered-text">{textoFallback}</pre>
      </details>
    </section>
  );
}
