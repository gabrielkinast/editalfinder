import { useMemo } from 'react';
import Modal from '../ui/Modal';
import { buildTriageReportModel } from '../../utils/consultor/buildTriageReportModel';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';

function formatGeneratedAt(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return '';
  }
}

/**
 * Relatório de triagem — visualização em tela (PDF export em breve).
 */
export default function ConsultorTriageReportModal({
  isOpen = false,
  onClose,
  cliente = null,
  totalMatches = 0,
  allMatches = [],
  selectedOpportunities = [],
  deadlineSummary = null,
  onGerarPreProjetoConsultivo,
}) {
  const report = useMemo(() => {
    if (!isOpen || !cliente) return null;
    return buildTriageReportModel({
      cliente,
      totalMatches,
      allMatches,
      selectedOpportunities,
      deadlineSummary,
    });
  }, [isOpen, cliente, totalMatches, allMatches, selectedOpportunities, deadlineSummary]);

  if (!isOpen || !report) return null;

  const handleClose = () => {
    logConsultorWorkspace('triage_report_close', { id_cliente: cliente?.id_cliente });
    onClose?.();
  };

  const { cliente: cl, carteira, tableRows, recommendations, proximosPassos, aberturaExecutiva } =
    report;

  return (
    <Modal onClose={handleClose} className="modal-large modal-consultor-triage-report">
      <div className="consultor-triage-report-shell">
        <header className="consultor-triage-report-header">
          <div>
            <h2 className="consultor-triage-report-title">Relatório de triagem</h2>
            <p className="consultor-triage-report-meta">
              {cl.nome}
              {formatGeneratedAt(report.generatedAt) ? ` · ${formatGeneratedAt(report.generatedAt)}` : ''}
            </p>
          </div>
          <button
            type="button"
            className="consultor-all-opps-close-x"
            onClick={handleClose}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>

        <div className="consultor-triage-report-scroll">
          {aberturaExecutiva ? (
            <p className="consultor-triage-report-executive">{aberturaExecutiva}</p>
          ) : null}

          <section className="consultor-triage-report-block">
            <h3 className="consultor-triage-report-h3">Resumo do cliente</h3>
            <dl className="consultor-triage-report-dl">
              <div>
                <dt>Cliente</dt>
                <dd>{cl.nome}</dd>
              </div>
              {cl.razaoSocial ? (
                <div>
                  <dt>Razão social</dt>
                  <dd>{cl.razaoSocial}</dd>
                </div>
              ) : null}
              <div>
                <dt>Perfil / segmento</dt>
                <dd>{cl.segmento}</dd>
              </div>
              <div>
                <dt>Cadastro consultivo</dt>
                <dd>
                  <span className={`consultor-profile-pct consultor-profile-pct--${cl.completudeLevel}`}>
                    {cl.completudePct}% completo
                  </span>
                </dd>
              </div>
            </dl>
          </section>

          <section className="consultor-triage-report-block">
            <h3 className="consultor-triage-report-h3">Resumo da carteira</h3>
            <p className="consultor-triage-report-line">{carteira.resumoLinha}</p>
            {carteira.venceCritico > 0 ? (
              <p className="consultor-triage-report-line consultor-triage-report-line--urgent">
                <strong>{carteira.venceCritico}</strong> vencem em até 7 dias
              </p>
            ) : null}
            {carteira.principalTitulo ? (
              <p className="consultor-triage-report-line consultor-triage-report-line--primary">
                Principal sugerida: <strong>{carteira.principalTitulo}</strong>
                {carteira.principalScore != null ? ` (${carteira.principalScore}% compat.)` : ''}
              </p>
            ) : null}
          </section>

          <section className="consultor-triage-report-block">
            <h3 className="consultor-triage-report-h3">Oportunidades selecionadas</h3>
            <div className="consultor-triage-report-table-wrap">
              <table className="consultor-triage-report-table">
                <thead>
                  <tr>
                    <th>Programa / Edital</th>
                    <th>Fonte</th>
                    <th>Prazo</th>
                    <th>Tipo de apoio</th>
                    <th>Compat.</th>
                    <th>Observação</th>
                    <th>Link</th>
                  </tr>
                </thead>
                <tbody>
                  {tableRows.map((row) => (
                    <tr
                      key={row.key}
                      className={row.isPrimary ? 'consultor-triage-report-row--primary' : ''}
                    >
                      <td className="consultor-triage-report-col-titulo" title={row.titulo}>
                        {row.isPrimary ? <span className="consultor-triage-tag">Principal</span> : null}
                        {row.titulo}
                      </td>
                      <td title={row.fonte}>{row.fonte}</td>
                      <td>{row.prazo}</td>
                      <td title={row.tipoApoio}>{row.tipoApoio}</td>
                      <td>
                        <span className="consultor-compat-badge consultor-compat-badge--table">
                          {row.scorePct}%
                        </span>
                      </td>
                      <td className="consultor-triage-report-col-obs" title={row.observacao}>
                        {row.observacao}
                      </td>
                      <td>
                        {row.link ? (
                          <a
                            href={row.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="consultor-opps-table-link"
                          >
                            Abrir
                          </a>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {recommendations.length > 0 ? (
            <section className="consultor-triage-report-block">
              <h3 className="consultor-triage-report-h3">Recomendação</h3>
              <div className="consultor-triage-rec-groups">
                {recommendations.map((group) => (
                  <div key={group.id} className="consultor-triage-rec-group">
                    <h4 className="consultor-triage-rec-group-title">{group.label}</h4>
                    <ul className="consultor-triage-rec-list">
                      {group.items.map((item) => (
                        <li key={item.key}>
                          <span className="consultor-triage-rec-titulo" title={item.titulo}>
                            {item.titulo}
                          </span>
                          <span className="consultor-triage-rec-meta">
                            {item.compatibilidade} · {item.scorePct}% · {item.prazoLabel}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          ) : null}

          <section className="consultor-triage-report-block">
            <h3 className="consultor-triage-report-h3">Próximos passos</h3>
            <ol className="consultor-triage-steps">
              {proximosPassos.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </section>
        </div>

        <footer className="consultor-triage-report-footer">
          <button
            type="button"
            className="btn-detalhes dash-action-outline consultor-triage-btn-pdf-soon"
            disabled
            title="Em breve: exportação em PDF do relatório de triagem."
          >
            Exportar PDF — Em breve
          </button>
          <button
            type="button"
            className="btn-view"
            onClick={() => {
              logConsultorWorkspace('triage_report_preproject_click', {
                id_cliente: cliente?.id_cliente,
                count: selectedOpportunities.length,
              });
              onGerarPreProjetoConsultivo?.();
            }}
          >
            Gerar pré-projeto consultivo
          </button>
        </footer>
      </div>
    </Modal>
  );
}
