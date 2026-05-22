import { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import { BOOK_READ_STATUSES } from '../../utils/scientific/scientificBookProgressStorage';

export default function ScientificBookProgressModal({
  open,
  book,
  bookKey,
  canonicalKey,
  areaLabel,
  initial,
  onSave,
  onClose,
}) {
  const [status, setStatus] = useState('quero_ler');
  const [progressPercent, setProgressPercent] = useState(0);
  const [currentChapter, setCurrentChapter] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (open && initial) {
      setStatus(initial.status || 'quero_ler');
      setProgressPercent(initial.progressPercent ?? 0);
      setCurrentChapter(initial.currentChapter || '');
      setNotes(initial.notes || '');
    }
  }, [open, initial]);

  if (!open || !book) return null;

  const label = book.author ? `${book.author} — ${book.title}` : book.title;

  const handleSave = () => {
    onSave?.({
      bookKey,
      title: label,
      area: canonicalKey,
      areaLabel,
      status,
      progressPercent: Number(progressPercent) || 0,
      currentChapter,
      notes,
    });
  };

  return (
    <Modal onClose={onClose} className="scientific-book-progress-modal" portal zIndex={1190}>
      <div className="scientific-book-progress-modal-inner">
        <h2>Progresso de leitura</h2>
        <p className="scientific-muted">
          <strong>{label}</strong>
          {areaLabel ? ` · ${areaLabel}` : ''}
        </p>

        <label className="scientific-trail-filter-label">
          Status
          <select
            className="scientific-search-input"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            {BOOK_READ_STATUSES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </label>

        <label className="scientific-trail-filter-label">
          Progresso ({progressPercent}%)
          <input
            type="range"
            min={0}
            max={100}
            value={progressPercent}
            onChange={(e) => setProgressPercent(Number(e.target.value))}
          />
        </label>

        <label className="scientific-trail-filter-label">
          Capítulo atual
          <input
            type="text"
            className="scientific-search-input"
            value={currentChapter}
            onChange={(e) => setCurrentChapter(e.target.value)}
            placeholder="Ex.: Cap. 3 — Decaimento"
          />
        </label>

        <label className="scientific-note-label">
          Notas rápidas
          <textarea
            className="scientific-note-textarea"
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>

        <div className="scientific-mastery-actions">
          <button type="button" className="scientific-btn scientific-btn-primary" onClick={handleSave}>
            Salvar progresso
          </button>
          <button type="button" className="scientific-btn scientific-btn-ghost" onClick={onClose}>
            Cancelar
          </button>
        </div>
        {status === 'lido' && (
          <p className="scientific-muted scientific-book-lido-hint">
            Ao salvar como <strong>Lido</strong>, você poderá passar pela verificação de domínio e ganhar XP
            de livro (uma vez por livro).
          </p>
        )}
      </div>
    </Modal>
  );
}
