import { useNavigate } from 'react-router-dom';
import { CRITERIOS } from '../../services/matchService';

const COR = {
  Alta:  '#22c55e',
  Média: '#f59e0b',
  Baixa: '#ef4444',
};

export default function CardEditalRadar({
  edital,
  score,
  compatibilidade,
  razoes = [],
  detalhes = {},
  matchLinha,
  fonteMatch,
  prazoInfo,
  expirado,
  favorito,
  onFavoritar,
}) {
  const navigate    = useNavigate();
  const idNumerico  = String(edital.id).replace('manual-', '');

  const badgeClass =
    compatibilidade === 'Alta'  ? 'radar-badge-alta'  :
    compatibilidade === 'Média' ? 'radar-badge-media' :
                                   'radar-badge-baixa';

  const cor      = COR[compatibilidade] || COR.Baixa;
  const siteLink = edital.linkInscricao || edital.linkOriginal || edital.orgSite || null;
  const pdfLink  = edital.pdfUrl || null;
  const scorePct = Number.isFinite(Number(score)) ? Math.min(100, Math.max(0, Math.round(Number(score)))) : 0;

  const mostraCriterios = detalhes && CRITERIOS.some(c => Number.isFinite(detalhes[c.key]));
  const rotuloPrazo = prazoInfo?.rotulo;

  return (
    <div className={`radar-card ${compatibilidade === 'Alta' ? 'radar-card-destaque' : ''} ${expirado ? 'radar-card-expirado' : ''}`}>
      {/* Cabeçalho */}
      <div className="radar-card-header">
        <div className="radar-card-titulo-wrap">
          <h3 className="radar-card-titulo">{edital.titulo}</h3>
          <span className="radar-card-orgao">{edital.orgao}</span>
        </div>
        <button
          className={`radar-btn-fav ${favorito ? 'ativo' : ''}`}
          onClick={() => onFavoritar(edital.id)}
          aria-pressed={favorito}
          title={favorito ? 'Remover favorito' : 'Favoritar'}
        >
          {favorito ? '★' : '☆'}
        </button>
      </div>

      {/* Linha de badges de situação temporal */}
      {(expirado || rotuloPrazo === 'curto') && (
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
        </div>
      )}

      {/* Barra de score geral */}
      <div className="radar-score-row">
        <div className="radar-score-bar-wrap">
          <div className="radar-score-bar" style={{ width: `${scorePct}%`, background: cor }} />
        </div>
        <span className="radar-score-pct">{scorePct}%</span>
        <span className={`radar-badge ${badgeClass}`}>{compatibilidade}</span>
      </div>

      {matchLinha && (
        <p
          className="radar-match-linha"
          title={
            fonteMatch === 'hibrido'
              ? 'Índice combina o JSON compatibilidade do edital (perfil que bate no cliente) com o cálculo dos 8 critérios do cadastro'
              : fonteMatch === 'json'
                ? 'Percentual vindo do JSON compatibilidade do edital'
                : 'Estimativa pelos 8 critérios do cadastro (sem JSON aplicável)'
          }
        >
          {matchLinha}
        </p>
      )}

      {/* Mini-barras por critério (8 critérios do novo índice) */}
      {mostraCriterios && (
        <div className="radar-criterios">
          {CRITERIOS.map(c => {
            const pts = Number.isFinite(detalhes[c.key]) ? detalhes[c.key] : 0;
            const pct = c.max > 0 ? Math.min(100, Math.max(0, Math.round((pts / c.max) * 100))) : 0;
            const nivel = pct >= 75 ? 'alto' : pct >= 40 ? 'medio' : 'baixo';
            return (
              <div key={c.key} className="radar-criterio-row" title={`${c.label}: ${pts}/${c.max} pts`}>
                <span className="radar-criterio-nome">{c.label}</span>
                <div className="radar-criterio-barra-wrap">
                  <div
                    className={`radar-criterio-barra radar-criterio-barra-${nivel}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="radar-criterio-pts">{pts}/{c.max}</span>
              </div>
            );
          })}
        </div>
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
