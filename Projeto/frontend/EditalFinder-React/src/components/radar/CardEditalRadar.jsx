import { useNavigate } from 'react-router-dom';

const COR = {
  Alta:  '#22c55e',
  Média: '#f59e0b',
  Baixa: '#ef4444',
};

const CRITERIO_LABEL = {
  area:         'Área/Temas',
  localizacao:  'Localização',
  porte:        'Porte',
  valor:        'Faixa de Valor',
  regularidade: 'Regularidade',
};

const CRITERIO_MAX = {
  area: 35, localizacao: 20, porte: 20, valor: 15, regularidade: 10,
};

export default function CardEditalRadar({ edital, score, compatibilidade, razoes = [], detalhes = {}, favorito, onFavoritar }) {
  const navigate    = useNavigate();
  const idNumerico  = String(edital.id).replace('manual-', '');

  const badgeClass =
    compatibilidade === 'Alta'  ? 'radar-badge-alta'  :
    compatibilidade === 'Média' ? 'radar-badge-media' :
                                   'radar-badge-baixa';

  const cor      = COR[compatibilidade] || COR.Baixa;
  const siteLink = edital.linkInscricao || edital.linkOriginal || edital.orgSite || null;
  const pdfLink  = edital.pdfUrl || null;

  return (
    <div className={`radar-card ${compatibilidade === 'Alta' ? 'radar-card-destaque' : ''}`}>
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

      {/* Barra de score geral */}
      <div className="radar-score-row">
        <div className="radar-score-bar-wrap">
          <div className="radar-score-bar" style={{ width: `${score}%`, background: cor }} />
        </div>
        <span className="radar-score-pct">{score}%</span>
        <span className={`radar-badge ${badgeClass}`}>{compatibilidade}</span>
      </div>

      {/* Detalhamento por critério */}
      {Object.keys(detalhes).length > 0 && (
        <div className="radar-criterios">
          {Object.entries(detalhes).map(([chave, pts]) => {
            const max = CRITERIO_MAX[chave] || 10;
            const pct = Math.round((pts / max) * 100);
            return (
              <div key={chave} className="radar-criterio-row">
                <span className="radar-criterio-nome">{CRITERIO_LABEL[chave]}</span>
                <div className="radar-criterio-barra-wrap">
                  <div
                    className="radar-criterio-barra"
                    style={{ width: `${pct}%`, background: pct >= 75 ? '#22c55e' : pct >= 45 ? '#f59e0b' : '#ef4444' }}
                  />
                </div>
                <span className="radar-criterio-pts">{pts}/{max}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Motivos do match */}
      {razoes.length > 0 && (
        <div className="radar-razoes">
          {razoes.map((r, i) => (
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
        {edital.isManual && (
          <button
            className="radar-btn-anexos"
            onClick={() => navigate(`/edital/${idNumerico}`)}
            title="Ver documentos e detalhes completos"
          >
            📋 Anexos
          </button>
        )}
      </div>
    </div>
  );
}
