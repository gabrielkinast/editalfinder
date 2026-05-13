import { useNavigate } from 'react-router-dom';
import { CRITERIOS } from '../../services/matchService';
import { getDisplayTitle } from '../../utils/displayTitle';

export default function CardEditalRadar({
  edital,
  score,
  compatibilidade,
  razoes = [],
  detalhes = {},
  criterioMeta = {},
  matchLinha,
  fonteMatch,
  radarBadges = [],
  prazoInfo,
  expirado,
  favorito,
  onFavoritar,
}) {
  const navigate    = useNavigate();
  const idNumerico  = String(edital.id).replace('manual-', '');
  const tituloCard = getDisplayTitle({
    titulo: edital.titulo,
    link: edital.linkOriginal || edital.linkInscricao,
    descricao: edital.descricao,
    objetivo: edital.objetivo,
    temas: edital.area || edital.temas,
    fonte_recurso: edital.orgao,
  });

  const badgeClass =
    compatibilidade === 'Alta'  ? 'radar-badge-alta'  :
    compatibilidade === 'Média' ? 'radar-badge-media' :
                                   'radar-badge-baixa';

  const scoreBarClass =
    compatibilidade === 'Alta'  ? 'radar-score-bar--alta'  :
    compatibilidade === 'Média' ? 'radar-score-bar--media' :
                                   'radar-score-bar--baixa';

  const siteLink = edital.linkInscricao || edital.linkOriginal || edital.orgSite || null;
  const pdfLink  = edital.pdfUrl || null;
  const scorePct = Number.isFinite(Number(score)) ? Math.min(100, Math.max(0, Math.round(Number(score)))) : 0;

  const mostraCriterios = detalhes && CRITERIOS.some(c => Number.isFinite(detalhes[c.key]));
  const rotuloPrazo = prazoInfo?.rotulo;

  return (
    <div className={`radar-card ${compatibilidade === 'Alta' ? 'radar-card-destaque' : ''} ${expirado ? 'radar-card-expirado' : ''}`}>
      {/* Cabeçalho: título → fonte/órgão → score (destaque) */}
      <div className="radar-card-header">
        <div className="radar-card-titulo-wrap">
          <h3 className="radar-card-titulo">{tituloCard}</h3>
          {edital.orgao && (
            <p className="radar-card-orgao" title="Órgão ou fonte">
              {edital.orgao}
            </p>
          )}
        </div>
        <button
          className={`radar-btn-fav ${favorito ? 'ativo' : ''}`}
          onClick={() => onFavoritar(edital)}
          aria-pressed={favorito}
          title={favorito ? 'Remover favorito' : 'Favoritar'}
        >
          {favorito ? '★' : '☆'}
        </button>
      </div>

      {/* Linha de badges de situação temporal */}
      {(expirado || rotuloPrazo === 'curto' || radarBadges.length > 0) && (
        <div className="radar-card-flags">
          {expirado && (
            <span
              className="radar-badge radar-badge-expirado"
              title="Edital com prazo expirado ou status inativo"
            >
              ⏳ Expirado
            </span>
          )}
          {!expirado && rotuloPrazo === 'curto' && (
            <span
              className="radar-badge radar-badge-prazo-curto"
              title={`Faltam ${prazoInfo?.dias ?? '?'} dia(s) para o prazo de envio`}
            >
              ⚡ Prazo curto
            </span>
          )}
          {radarBadges.map((b) => (
            <span key={b.key} className="radar-badge radar-badge-aviso" title={b.label}>
              {b.label}
            </span>
          ))}
        </div>
      )}

      <div className="radar-score-block">
        <div className="radar-score-block-head">
          <span className="radar-score-label">Compatibilidade</span>
          <span className={`radar-badge radar-badge-compat ${badgeClass}`}>{compatibilidade}</span>
        </div>
        <div className="radar-score-row">
          <div className="radar-score-bar-wrap">
            <div className={`radar-score-bar ${scoreBarClass}`} style={{ width: `${scorePct}%` }} />
          </div>
          <span className="radar-score-pct">{scorePct}%</span>
        </div>
      </div>

      {matchLinha && (
        <p
          className="radar-match-linha"
          title={
            fonteMatch === 'radar_v2'
              ? 'Radar v2 — dimensões de afinidade, perfil, tipo, localização, prazo, qualidade e valor; com penalidades quando aplicável.'
              : 'Estimativa a partir dos critérios do cadastro.'
          }
        >
          {matchLinha}
        </p>
      )}

      {mostraCriterios && (
        <details className="radar-criterios-details">
          <summary className="radar-criterios-summary">Detalhe por dimensão ({CRITERIOS.length}) — opcional</summary>
          <div className="radar-criterios">
            {CRITERIOS.map((c) => {
              const ausente = !!(criterioMeta && criterioMeta[c.key]?.ausente);
              const pts = Number.isFinite(detalhes[c.key]) ? detalhes[c.key] : 0;
              const pct = ausente
                ? 0
                : c.max > 0
                  ? Math.min(100, Math.max(0, Math.round((pts / c.max) * 100)))
                  : 0;
              const nivel = ausente ? 'ausente' : pct >= 75 ? 'alto' : pct >= 40 ? 'medio' : 'baixo';
              return (
                <div
                  key={c.key}
                  className={`radar-criterio-row${ausente ? ' radar-criterio-row-ausente' : ''}`}
                  title={
                    ausente
                      ? `${c.label}: dado não informado ou não avaliado — não conta como match pleno`
                      : `${c.label}: ${pts}/${c.max}`
                  }
                >
                  <span className="radar-criterio-nome">{c.label}</span>
                  <div className="radar-criterio-barra-wrap">
                    <div
                      className={`radar-criterio-barra radar-criterio-barra-${nivel}${ausente ? ' radar-criterio-barra-ausente' : ''}`}
                      style={{ width: ausente ? '6%' : `${pct}%` }}
                    />
                  </div>
                  <span className="radar-criterio-pts">{ausente ? 'n/d' : `${pts}/${c.max}`}</span>
                </div>
              );
            })}
          </div>
        </details>
      )}

      {/* Razões (tags curtas) */}
      {razoes.length > 0 && (
        <div className="radar-razoes">
          {razoes.slice(0, 6).map((r, i) => (
            <span key={i} className="radar-razao-tag">✓ {r}</span>
          ))}
        </div>
      )}

      {/* Meta */}
      <div className="radar-card-meta">
        <span><strong>Tipo:</strong> {edital.tipoRecurso}</span>
        <span><strong>Área:</strong> {edital.area}</span>
        {edital.estado && <span><strong>Estado:</strong> {edital.estado}</span>}
      </div>

      {/* Ações */}
      <div className="radar-card-acoes">
        {siteLink ? (
          <a href={siteLink} target="_blank" rel="noopener noreferrer" className="radar-btn-site">
            {edital.linkInscricao ? '✅ Inscrição' : '🌐 Site'}
          </a>
        ) : (
          <span className="radar-btn-site disabled">🌐 Site</span>
        )}
        {pdfLink ? (
          <a href={pdfLink} target="_blank" rel="noopener noreferrer" className="radar-btn-pdf">📄 PDF</a>
        ) : (
          <span className="radar-btn-pdf disabled">📄 PDF</span>
        )}
        {edital.isManual && edital.temAnexos && (
          <button
            className="radar-btn-anexos"
            onClick={() => navigate(`/edital/${idNumerico}`)}
            title="Ver documentos e detalhes completos"
          >
            📋 Detalhes
          </button>
        )}
      </div>
    </div>
  );
}
