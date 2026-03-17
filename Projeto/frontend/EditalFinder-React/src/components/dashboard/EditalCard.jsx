import { formatCurrency, formatDate } from '../../utils/formatters';

export default function EditalCard({ edital }) {
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
          <span className="edital-meta-label">Localidade:</span>
          <span>{edital.localidade}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Tipo:</span>
          <span>{edital.tipoRecurso}</span>
        </div>
      </div>

      <div className="edital-date">
        📅 Limite: {edital.dataLimite ? formatDate(edital.dataLimite) : 'Não informado'}
      </div>

      <div className="edital-actions">
        <a href={edital.linkOriginal || edital.pdfUrl} target="_blank" className="btn-view" style={{ textDecoration: 'none', textAlign: 'center' }}>
          Ver Edital
        </a>
      </div>
    </div>
  );
}
