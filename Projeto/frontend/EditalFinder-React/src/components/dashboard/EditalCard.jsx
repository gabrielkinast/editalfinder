import { useNavigate } from 'react-router-dom';
import { formatDate, formatCurrency } from '../../utils/formatters';
import { useSettings } from '../../contexts/SettingsContext';

const ORG_WEBSITES = {
  'FINEP': 'https://www.finep.gov.br',
  'BNDES': 'https://www.bndes.gov.br',
  'CNPQ': 'https://www.cnpq.br',
  'FAPERGS': 'https://fapergs.rs.gov.br',
  'FAPESP': 'https://fapesp.br',
  'CORDIS': 'https://cordis.europa.eu',
  'MCTI': 'https://www.gov.br/mcti',
  'MAPA': 'https://www.gov.br/agricultura',
  'MEC': 'https://www.gov.br/mec',
  'MINISTÉRIO DA SAÚDE': 'https://www.gov.br/saude',
};

function scoreColor(score) {
  if (score >= 80) return 'score-alta';
  if (score >= 50) return 'score-media';
  return 'score-baixa';
}

export default function EditalCard({ edital }) {
  const { settings } = useSettings();
  const navigate = useNavigate();

  const siteLink      = edital.linkOriginal || edital.orgSite || ORG_WEBSITES[edital.orgao?.toUpperCase()] || null;
  const pdfLink       = edital.pdfUrl || null;
  const inscricaoLink = edital.linkInscricao || null;
  const score         = edital.score || 0;
  const deadlineScore = edital.scoreDetalhado?.deadline ?? edital.scoreDetalhado?.prazo ?? 0;
  const isPrazoCurto  = deadlineScore >= 70;
  // Extrai o ID numérico do banco (formato: "manual-123" ou número puro)
  const idNumerico    = String(edital.id).replace('manual-', '');

  const tagsPerfil = edital.recomendacao
    ? edital.recomendacao.split(/[,;]/).map(t => t.trim()).filter(Boolean)
    : [];

  return (
    <div className={`edital-card ${edital.isManual ? 'edital-card-manual' : ''}`}>

      {/* Cabeçalho: título */}
      <div className="edital-title-wrap">
        <h3 className="edital-title">{edital.titulo}</h3>
        {isPrazoCurto && (
          <span className="edital-badge-urgencia">⏰ Prazo Curto</span>
        )}
      </div>

      <span className="edital-badge">{edital.orgao}</span>

      <div className="edital-meta">
        <div className="edital-meta-row">
          <span className="edital-meta-label">Área:</span>
          <span>{edital.area}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Estado:</span>
          <span>{edital.estado || 'Nacional'}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Tipo:</span>
          <span>{edital.tipoRecurso}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Valor:</span>
          <span>{edital.valor ? formatCurrency(edital.valor) : 'Não informado'}</span>
        </div>
        {edital.elegibilidade && (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Elegível:</span>
            <span>{edital.elegibilidade}</span>
          </div>
        )}
      </div>

      {/* Tags de perfis recomendados */}
      {tagsPerfil.length > 0 && (
        <div className="edital-tags-perfil">
          {tagsPerfil.slice(0, 4).map(tag => (
            <span key={tag} className="edital-tag-recomendacao">{tag}</span>
          ))}
        </div>
      )}

      <div className="edital-date">
        📅 Limite: {edital.dataLimite ? formatDate(edital.dataLimite) : 'Não informado'}
      </div>

      <div className="edital-actions" style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
        {/* Botão Inscrição (prioridade se disponível) */}
        {inscricaoLink ? (
          <a href={inscricaoLink} target="_blank" className="btn-inscricao" style={{ textDecoration: 'none', textAlign: 'center', flex: 1 }}>
            Inscrição
          </a>
        ) : siteLink ? (
          <a href={siteLink} target="_blank" className="btn-view" style={{ textDecoration: 'none', textAlign: 'center', flex: 1 }}>
            Site
          </a>
        ) : (
          <span className="btn-view disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1 }}>
            Site
          </span>
        )}

        {pdfLink ? (
          <a href={pdfLink} target="_blank" className="btn-pdf" style={{ textDecoration: 'none', textAlign: 'center', flex: 1 }}>
            📄 PDF
          </a>
        ) : (
          <span className="btn-pdf disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1 }}>
            📄 PDF
          </span>
        )}

        {/* Botão Ver Detalhes — só para editais do banco (com ID numérico) */}
        {edital.isManual && (
          <button
            className="btn-detalhes"
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
