import { memo } from 'react';
import { useNavigate } from 'react-router-dom';
import ExternalActionButton, { EXTERNAL_ACTION_TYPES } from '../../utils/externalActions';
import { resolveActionLinks } from '../../utils/edital/linkHealth';
import { CRITERIOS } from '../../services/matchService';
import { getDisplayTitle } from '../../utils/displayTitle';
import { normalizeRadarCardEdital } from '../../utils/radar/radarResultShape';
import EditalStatusBadges from '../editais/EditalStatusBadges';

function CardEditalRadar({
  edital: editalIn,
  score,
  compatibilidade,
  razoes = [],
  razoesPositivas,
  detalhes = {},
  criterioMeta = {},
  matchLinha,
  fonteMatch,
  radarBadges = [],
  radarAlertas,
  radarDimensoes,
  prazoInfo,
  expirado,
  favorito,
  onFavoritar,
}) {
  const edital = normalizeRadarCardEdital(editalIn);
  const navigate = useNavigate();
  const idNumerico = String(edital.id ?? 'unknown').replace('manual-', '');
  const positivos = Array.isArray(razoesPositivas)
    ? razoesPositivas
    : Array.isArray(razoes)
      ? razoes.filter((r) => !String(r).startsWith('Atenção'))
      : [];
  const alertas = Array.isArray(radarAlertas) ? radarAlertas : [];
  const dimensoes = Array.isArray(radarDimensoes) ? radarDimensoes : [];
  const safeDetalhes = detalhes && typeof detalhes === 'object' ? detalhes : {};
  const safeCriterioMeta =
    criterioMeta && typeof criterioMeta === 'object' ? criterioMeta : {};
  const safeBadges = Array.isArray(radarBadges) ? radarBadges : [];
  const compatLabel = compatibilidade || 'Baixa';
  const tituloCard = getDisplayTitle({
    titulo: edital.titulo,
    link: edital.linkOriginal || edital.linkInscricao,
    descricao: edital.descricao,
    objetivo: edital.objetivo,
    temas: edital.area || edital.temas,
    fonte_recurso: edital.orgao,
  });

  const badgeClass =
    compatLabel === 'Alta' ? 'radar-badge-alta' :
    compatLabel === 'Média' ? 'radar-badge-media' :
    'radar-badge-baixa';

  const scoreBarClass =
    compatLabel === 'Alta' ? 'radar-score-bar--alta' :
    compatLabel === 'Média' ? 'radar-score-bar--media' :
    'radar-score-bar--baixa';

  const actions = resolveActionLinks(edital);
  const inscricaoLink = actions.inscricao;
  const siteLink = actions.site;
  const pdfLink = actions.pdf;
  const scorePct = Number.isFinite(Number(score)) ? Math.min(100, Math.max(0, Math.round(Number(score)))) : 0;

  const mostraCriterios = CRITERIOS.some((c) => Number.isFinite(safeDetalhes[c.key]));
  const rotuloPrazo = prazoInfo?.rotulo;
  const temExplicacao = positivos.length > 0 || alertas.length > 0 || dimensoes.length > 0;

  return (
    <div className={`radar-card ${compatLabel === 'Alta' ? 'radar-card-destaque' : ''} ${expirado ? 'radar-card-expirado' : ''}`} data-testid="radar-card">
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

      <div className="radar-card-status-badges">
        <EditalStatusBadges edital={editalIn} maxVisible={2} compact />
      </div>

      {(expirado || rotuloPrazo === 'curto' || safeBadges.length > 0) && (
        <div className="radar-card-flags">
          {expirado && (
            <span className="radar-badge radar-badge-expirado" title="Prazo expirado ou inativo">
              ⏳ Expirado
            </span>
          )}
          {!expirado && rotuloPrazo === 'curto' && (
            <span
              className="radar-badge radar-badge-prazo-curto"
              title={`Faltam ${prazoInfo?.dias ?? '?'} dia(s) para o prazo`}
            >
              ⚡ Prazo curto
            </span>
          )}
          {safeBadges
            .filter((b) => !['prazo_curto', 'encerrado'].includes(b.key))
            .slice(0, 3)
            .map((b) => (
              <span key={b.key} className="radar-badge radar-badge-aviso" title={b.label}>
                {b.label}
              </span>
            ))}
        </div>
      )}

      <div className="radar-score-block">
        <div className="radar-score-block-head">
          <span className="radar-score-label">Compatibilidade</span>
          <span className={`radar-badge radar-badge-compat ${badgeClass}`}>{compatLabel}</span>
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
              ? 'Score calculado por dimensões (afinidade, perfil, tipo, localização, prazo, qualidade, valor). Estes textos ajudam a explicar o resultado ao consultor.'
              : undefined
          }
        >
          {matchLinha}
        </p>
      )}

      {temExplicacao && (
        <section className="radar-explica-secao" aria-label="Por que combina com este cliente">
          <h4 className="radar-explica-titulo">Por que combina com este cliente?</h4>

          {positivos.length > 0 && (
            <div className="radar-explica-bloco radar-explica-bloco--positivo">
              <p className="radar-explica-subtitulo">Motivos positivos</p>
              <ul className="radar-explica-lista">
                {positivos.slice(0, 5).map((text, i) => (
                  <li key={`p-${i}`}>{text}</li>
                ))}
              </ul>
            </div>
          )}

          {alertas.length > 0 && (
            <div className="radar-explica-bloco radar-explica-bloco--alerta">
              <p className="radar-explica-subtitulo">Alertas</p>
              <ul className="radar-explica-lista radar-explica-lista--alerta">
                {alertas.map((a) => (
                  <li key={a.key}>
                    <strong>{a.label}:</strong> {a.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {dimensoes.length > 0 && (
            <div className="radar-explica-dimensoes">
              <p className="radar-explica-subtitulo">Dimensões avaliadas</p>
              <ul className="radar-dim-lista">
                {dimensoes.map((d) => (
                  <li
                    key={d.key}
                    className={`radar-dim-item radar-dim-item--${d.nivel}`}
                    title={d.ausente ? 'Dado insuficiente nesta dimensão' : `${d.pontos}/${d.max} pontos`}
                  >
                    <span className="radar-dim-label">{d.label}</span>
                    <span className={`radar-dim-nivel radar-dim-nivel--${d.nivel}`}>
                      {d.ausente ? 'n/d' : d.nivel === 'alto' ? 'Forte' : d.nivel === 'medio' ? 'Média' : 'Fraca'}
                    </span>
                    <p className="radar-dim-texto">{d.texto}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {mostraCriterios && (
        <details className="radar-criterios-details">
          <summary className="radar-criterios-summary">Pontuação técnica por dimensão</summary>
          <div className="radar-criterios">
            {CRITERIOS.map((c) => {
              const ausente = !!(safeCriterioMeta[c.key]?.ausente);
              const pts = Number.isFinite(safeDetalhes[c.key]) ? safeDetalhes[c.key] : 0;
              const pctDim =
                c.max > 0
                  ? Math.min(100, Math.max(0, Math.round((pts / c.max) * 100)))
                  : 0;
              const nivel = ausente ? 'ausente' : pctDim >= 75 ? 'alto' : pctDim >= 40 ? 'medio' : 'baixo';
              return (
                <div
                  key={c.key}
                  className={`radar-criterio-row${ausente ? ' radar-criterio-row-ausente' : ''}`}
                >
                  <span className="radar-criterio-nome">{c.label}</span>
                  <div className="radar-criterio-barra-wrap">
                    <div
                      className={`radar-criterio-barra radar-criterio-barra-${nivel}${ausente ? ' radar-criterio-barra-ausente' : ''}`}
                      style={{ width: ausente ? '6%' : `${pctDim}%` }}
                    />
                  </div>
                  <span className="radar-criterio-pts">{ausente ? 'n/d' : `${pts}/${c.max}`}</span>
                </div>
              );
            })}
          </div>
        </details>
      )}

      <div className="radar-card-meta">
        <span><strong>Tipo:</strong> {edital.tipoRecurso || '—'}</span>
        <span><strong>Área:</strong> {edital.area || '—'}</span>
        {edital.estado && <span><strong>Estado:</strong> {edital.estado}</span>}
      </div>

      <div className="radar-card-acoes">
        {inscricaoLink ? (
          <ExternalActionButton
            item={edital}
            actionType={EXTERNAL_ACTION_TYPES.EDITAL_INSCRICAO}
            url={inscricaoLink}
            label="✅ Inscrição"
            className="radar-btn-site"
            logEdital
            logCampo="link_inscricao"
          />
        ) : siteLink ? (
          <ExternalActionButton
            item={edital}
            actionType={EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY}
            url={siteLink}
            label="🌐 Site"
            className="radar-btn-site"
            logEdital
            logCampo="link"
          />
        ) : (
          <span className="radar-btn-site disabled">🌐 Site</span>
        )}
        {pdfLink ? (
          <ExternalActionButton
            item={edital}
            actionType={EXTERNAL_ACTION_TYPES.EDITAL_PDF}
            url={pdfLink}
            label="📄 PDF"
            className="radar-btn-pdf"
            logEdital
            logCampo="pdf_url"
          />
        ) : (
          <span className="radar-btn-pdf disabled">📄 PDF</span>
        )}
        {edital.isManual && edital.temAnexos && (
          <button
            type="button"
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

function cardPropsAreEqual(prev, next) {
  const pe = prev.edital;
  const ne = next.edital;
  if (pe?.id !== ne?.id) return false;
  if (prev.score !== next.score) return false;
  if (prev.compatibilidade !== next.compatibilidade) return false;
  if (prev.favorito !== next.favorito) return false;
  if (prev.expirado !== next.expirado) return false;
  if (prev.matchLinha !== next.matchLinha) return false;
  if (prev.radarAlertas !== next.radarAlertas) return false;
  if (prev.radarDimensoes !== next.radarDimensoes) return false;
  if (prev.onFavoritar !== next.onFavoritar) return false;
  return true;
}

export default memo(CardEditalRadar, cardPropsAreEqual);
