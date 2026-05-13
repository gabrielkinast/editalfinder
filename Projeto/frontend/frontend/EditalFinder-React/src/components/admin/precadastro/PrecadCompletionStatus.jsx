import { calculatePreCadastroCompleteness } from '../../../utils/precadastro/calculatePreCadastroCompleteness';

const LABELS = {
  incompleto: 'Incompleto',
  basico: 'Básico',
  bom: 'Bom',
  pronto_pdf: 'Pronto para PDF',
};

/**
 * Barra principal de completude (novo modelo) + checklist resumido.
 */
export default function PrecadCompletionStatus({ form, completeness }) {
  const calc = completeness || calculatePreCadastroCompleteness(form);
  const score = calc.score;
  const statusKey = LABELS[calc.status] ? calc.status : 'incompleto';
  const badgeClass = statusKey === 'pronto_pdf' ? 'pronto' : statusKey;
  const { checks } = calc;

  return (
    <div className="precad-completion" aria-label="Completude do pré-cadastro">
      <div className="precad-completion-head">
        <span className="precad-completion-title">Completude inteligente</span>
        <span className={`precad-completion-badge level-${badgeClass}`}>{LABELS[statusKey]}</span>
        <span className="precad-completion-pct">{score}%</span>
      </div>
      <p className="precad-muted small precad-complete-summary">
        {calc.requiredMissing.length} obrigatória(s), {calc.recommendedMissing.length} recomendada(s)
      </p>
      <div className="precad-completion-bar">
        <div className="precad-completion-fill" style={{ width: `${score}%` }} />
      </div>
      <ul className="precad-completion-list">
        <li className={checks.dadosEmpresa ? 'ok' : 'pendente'}>
          Dados cadastrais principais do formulário
          {!checks.dadosEmpresa ? <span className="hint">pendente</span> : null}
        </li>
        <li className={checks.linha ? 'ok' : 'pendente'}>
          Linha / produto selecionado
          {!checks.linha ? <span className="hint">pendente</span> : null}
        </li>
        <li className={checks.titulo ? 'ok' : 'pendente'}>
          Título do projeto
          {!checks.titulo ? <span className="hint">pendente</span> : null}
        </li>
        <li className={checks.resumo ? 'ok' : 'pendente'}>
          Resumo publicável ou executivo
          {!checks.resumo ? <span className="hint">pendente</span> : null}
        </li>
        <li className={checks.objetivo ? 'ok' : 'pendente'}>
          Objetivo / diretriz
          {!checks.objetivo ? <span className="hint">pendente</span> : null}
        </li>
        <li className={checks.escopo ? 'ok' : 'pendente'}>
          Problema / escopo (finalidade)
          {!checks.escopo ? <span className="hint">pendente</span> : null}
        </li>
      </ul>
    </div>
  );
}
