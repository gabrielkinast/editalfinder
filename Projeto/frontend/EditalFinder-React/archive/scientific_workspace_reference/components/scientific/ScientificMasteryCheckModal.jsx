import { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import { POWER_IDEA_TYPE_LABELS } from '../../utils/scientific/scientificPowerIdeasHelpers';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

const KIND_LABELS = {
  theory: 'Tópico de teoria',
  powerIdea: 'Ideia poderosa',
  book: 'Livro',
  project: 'Projeto',
  question: 'Pergunta',
  route_step: 'Passo da rota',
};

export default function ScientificMasteryCheckModal({
  open,
  pending,
  onConfirmMastery,
  onMarkStudying,
  onDefer,
  onClose,
}) {
  const [answers, setAnswers] = useState(['', '', '']);

  useEffect(() => {
    if (open && pending) {
      setAnswers(['', '', '']);
      logScientificWorkspace('mastery_check_opened', {
        progressKey: pending.progressKey,
        kind: pending.kind,
      });
    }
  }, [open, pending?.progressKey]);

  if (!open || !pending) return null;

  const questions = pending.questions || [];
  const typeLabel =
    pending.itemType && POWER_IDEA_TYPE_LABELS[pending.itemType]
      ? POWER_IDEA_TYPE_LABELS[pending.itemType]
      : KIND_LABELS[pending.kind] || pending.kind;

  const handleClose = () => {
    onClose?.();
  };

  return (
    <Modal onClose={handleClose} className="scientific-mastery-modal" portal zIndex={1200}>
      <div className="scientific-mastery-modal-inner">
        <header className="scientific-mastery-modal-header">
          <h2>Verificar domínio</h2>
          <p className="scientific-muted scientific-mastery-disclaimer">
            Isso não corrige automaticamente suas respostas. A ideia é forçar uma checagem ativa
            antes de você marcar como dominado.
          </p>
        </header>

        <div className="scientific-mastery-item-meta">
          <p>
            <strong>{pending.title}</strong>
          </p>
          <p className="scientific-muted">
            {pending.areaLabel || pending.canonicalKey} · {typeLabel}
            {pending.level ? ` · ${pending.level}` : ''}
          </p>
        </div>

        <ol className="scientific-mastery-questions">
          {questions.map((q, idx) => (
            <li key={q.id} className="scientific-mastery-question">
              <p className="scientific-mastery-question-text">{q.question}</p>
              <span className="scientific-muted scientific-mastery-skill">{q.expectedSkill}</span>
              <label className="scientific-mastery-answer-label">
                Sua resposta (opcional, autoavaliação)
                <textarea
                  className="scientific-note-textarea"
                  rows={3}
                  value={answers[idx] || ''}
                  onChange={(e) => {
                    const next = [...answers];
                    next[idx] = e.target.value;
                    setAnswers(next);
                  }}
                  placeholder="Escreva em suas palavras…"
                />
              </label>
            </li>
          ))}
        </ol>

        <div className="scientific-mastery-actions">
          <button
            type="button"
            className="scientific-btn scientific-btn-primary"
            onClick={() => onConfirmMastery?.(answers)}
          >
            Confirmar domínio
          </button>
          <button
            type="button"
            className="scientific-btn scientific-btn-secondary"
            onClick={() => onMarkStudying?.()}
          >
            Marcar como estudando
          </button>
          <button type="button" className="scientific-btn scientific-btn-ghost" onClick={() => onDefer?.()}>
            Responder depois
          </button>
        </div>
      </div>
    </Modal>
  );
}
