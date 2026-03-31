import { formatCurrency, formatDate } from '../../utils/formatters';
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

export default function EditalCard({ edital }) {
  const { settings } = useSettings();
  
  // Define o link do site: link do edital -> site da organização no banco -> fallback manual -> null
  const siteLink = edital.linkOriginal || edital.orgSite || ORG_WEBSITES[edital.orgao?.toUpperCase()] || null;
  const pdfLink = edital.pdfUrl || null;

  return (
    <div className={`edital-card ${edital.isManual ? 'edital-card-manual' : ''}`}>
      <h3 className="edital-title">{edital.titulo}</h3>
      <span className="edital-badge">{edital.orgao}</span>

      <div className="edital-meta">
        <div className="edital-meta-row">
          <span className="edital-meta-label">Área:</span>
          <span>{edital.area}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Valor:</span>
          <span className="edital-value">{formatCurrency(edital.valor)}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Estado:</span>
          <span>{edital.estado || 'Nacional'}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Tipo:</span>
          <span>{edital.tipoRecurso}</span>
        </div>
      </div>

      <div className="edital-date">
        📅 Limite: {edital.dataLimite ? formatDate(edital.dataLimite) : 'Não informado'}
      </div>

      <div className="edital-actions" style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
        {siteLink ? (
          <a href={siteLink} target="_blank" className="btn-view" style={{ textDecoration: 'none', textAlign: 'center', flex: 1, gap: '6px' }}>
            {settings.logoImage ? (
              <img src={settings.logoImage} alt="Logo" style={{ maxHeight: '22px', width: 'auto' }} />
            ) : (
              <span>🌐</span>
            )}
            Site
          </a>
        ) : (
          <span className="btn-view disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1, gap: '6px' }}>
            {settings.logoImage ? (
              <img src={settings.logoImage} alt="Logo" style={{ maxHeight: '22px', width: 'auto', filter: 'grayscale(100%)' }} />
            ) : (
              <span>🌐</span>
            )}
            Site
          </span>
        )}
        
        {pdfLink ? (
          <a href={pdfLink} target="_blank" className="btn-pdf" style={{ textDecoration: 'none', textAlign: 'center', flex: 1, gap: '6px' }}>
            📄 PDF
          </a>
        ) : (
          <span className="btn-pdf disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1 }}>
            📄 PDF
          </span>
        )}
      </div>
    </div>
  );
}
