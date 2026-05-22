export default function DashboardDataQualityPanel({ audit, metrics }) {
  if (!import.meta.env.DEV || !audit) return null;

  const prazo = audit.editais?.prazo || {};
  const total = audit.editais?.total || 0;
  const withPct = total ? Math.round(((prazo.withPrazo || 0) / total) * 100) : 0;
  const withoutPct = total ? Math.round(((prazo.withoutPrazo || 0) / total) * 100) : 0;

  return (
    <section className="home-dash-panel home-dash-dq-panel" aria-label="Qualidade dos dados (DEV)">
      <h3 className="home-dash-panel-title">Qualidade da base (DEV)</h3>
      <p className="home-dash-muted home-dash-dq-lead">
        Painel visível apenas em desenvolvimento. Use o console{' '}
        <code>[dashboard] data_quality_audit</code> para amostras.
      </p>
      <div className="home-dash-dq-grid">
        <div className="home-dash-dq-stat">
          <span className="home-dash-dq-value">{withPct}%</span>
          <span className="home-dash-dq-label">com prazo estruturado</span>
        </div>
        <div className="home-dash-dq-stat">
          <span className="home-dash-dq-value">{withoutPct}%</span>
          <span className="home-dash-dq-label">sem prazo / inválido</span>
        </div>
        <div className="home-dash-dq-stat">
          <span className="home-dash-dq-value">
            {(metrics?.prazoConfirmado ?? 0).toLocaleString('pt-BR')}
          </span>
          <span className="home-dash-dq-label">prazo confirmado (filtro ativo)</span>
        </div>
        <div className="home-dash-dq-stat">
          <span className="home-dash-dq-value">
            {(metrics?.semPrazoEstruturado ?? 0).toLocaleString('pt-BR')}
          </span>
          <span className="home-dash-dq-label">sem prazo estruturado</span>
        </div>
      </div>
      {prazo.fieldsDetected?.length > 0 && (
        <div className="home-dash-dq-block">
          <h4 className="home-dash-dq-subtitle">Campos de prazo detectados</h4>
          <ul className="home-dash-dq-list">
            {prazo.fieldsDetected.map((f) => (
              <li key={f.label}>
                {f.label} — {f.count}
              </li>
            ))}
          </ul>
        </div>
      )}
      {audit.editais?.tipo?.topRawValues?.length > 0 && (
        <div className="home-dash-dq-block">
          <h4 className="home-dash-dq-subtitle">Top categorias (raw)</h4>
          <ul className="home-dash-dq-list">
            {audit.editais.tipo.topRawValues.slice(0, 6).map((t) => (
              <li key={t.label}>
                {t.label} — {t.count}
              </li>
            ))}
          </ul>
        </div>
      )}
      {audit.editais?.fonte?.topFontes?.length > 0 && (
        <div className="home-dash-dq-block">
          <h4 className="home-dash-dq-subtitle">Top fontes</h4>
          <ul className="home-dash-dq-list">
            {audit.editais.fonte.topFontes.slice(0, 6).map((f) => (
              <li key={f.label}>
                {f.label} — {f.count}
              </li>
            ))}
          </ul>
        </div>
      )}
      {audit.warnings?.length > 0 && (
        <div className="home-dash-dq-warnings">
          <h4 className="home-dash-dq-subtitle">Avisos</h4>
          <ul>
            {audit.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
