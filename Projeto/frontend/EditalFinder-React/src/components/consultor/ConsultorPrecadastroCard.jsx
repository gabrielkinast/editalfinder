import { precadStatusLabel } from '../../utils/precadastro/getClientPrecadSummary';

/**
 * Card de resumo do pré-projeto (sem formulário — edição no overlay full-screen).
 */
export default function ConsultorPrecadastroCard({
  summary,
  canOpen = true,
  onAbrir,
  hasBriefing = false,
  profileScore = 0,
  onBriefingRapido,
}) {
  const { label, tone } = precadStatusLabel(summary);
  const score = summary?.score ?? 0;
  const pend = summary?.pendenciesCount ?? 0;
  const profileLow = profileScore < 50;
  const updated = summary?.ultimaEdicao
    ? new Date(summary.ultimaEdicao).toLocaleString('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short',
      })
    : null;

  return (
    <section className="consultor-section consultor-section--precad">
      <div className="consultor-section-head">
        <div>
          <h3 className="consultor-section-title">Pré-projeto consultivo</h3>
          <p className="consultor-section-sub">
            Rascunho local neste navegador. Use o botão abaixo para editar em tela ampla.
          </p>
        </div>
      </div>

      {hasBriefing ? (
        <p className="consultor-precad-briefing-hint consultor-precad-briefing-hint--ok">
          Dados do briefing disponíveis para sugestões no rascunho.
        </p>
      ) : profileLow && onBriefingRapido ? (
        <p className="consultor-precad-briefing-hint consultor-precad-briefing-hint--warn">
          Faça um{' '}
          <button type="button" className="consultor-precad-briefing-link" onClick={() => onBriefingRapido('precad_card')}>
            briefing rápido
          </button>{' '}
          para reduzir pendências no pré-projeto.
        </p>
      ) : null}

      <div className="consultor-precad-stats">
        <span className={`consultor-precad-badge consultor-precad-badge--${tone}`}>{label}</span>
        <span className="consultor-precad-metric">
          Completude: <strong>{score}%</strong>
        </span>
        {pend > 0 ? (
          <span className="consultor-precad-metric consultor-precad-metric--warn">
            {pend} pendência{pend === 1 ? '' : 's'}
          </span>
        ) : (
          <span className="consultor-precad-metric consultor-precad-metric--ok">Sem pendências críticas</span>
        )}
        {updated ? (
          <span className="consultor-precad-metric consultor-precad-metric--muted">
            Atualizado: {updated}
          </span>
        ) : null}
      </div>

      {summary?.consultivePendencies?.length ? (
        <ul className="consultor-precad-pend-list">
          {summary.consultivePendencies.slice(0, 4).map((t) => (
            <li key={t}>{t}</li>
          ))}
          {summary.consultivePendencies.length > 4 ? (
            <li className="consultor-precad-pend-more">…e outras no formulário completo.</li>
          ) : null}
        </ul>
      ) : !summary?.hadDraft ? (
        <p className="consultor-muted-hint">
          Nenhum rascunho ainda. Gere a partir de oportunidades selecionadas ou abra para começar.
        </p>
      ) : null}

      {canOpen ? (
        <button type="button" className="consultor-btn-abrir-preprojeto" onClick={onAbrir}>
          Abrir pré-projeto consultivo
        </button>
      ) : null}
    </section>
  );
}
