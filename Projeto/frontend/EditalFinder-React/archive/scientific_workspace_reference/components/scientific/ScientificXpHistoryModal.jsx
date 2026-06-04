import { useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { interestLabelById } from '../../utils/scientific/scientificInterestsConfig';

const KIND_FILTER = [
  { id: '', label: 'Todos os tipos' },
  { id: 'theory', label: 'Teoria' },
  { id: 'powerIdea', label: 'Ideia poderosa' },
  { id: 'book', label: 'Livro' },
  { id: 'project', label: 'Projeto' },
  { id: 'question', label: 'Pergunta' },
  { id: 'route_step', label: 'Rota' },
];

export default function ScientificXpHistoryModal({ open, onClose, events = [] }) {
  const [areaFilter, setAreaFilter] = useState('');
  const [kindFilter, setKindFilter] = useState('');
  const [search, setSearch] = useState('');

  const areas = useMemo(
    () => [...new Set(events.map((e) => e.canonicalKey).filter(Boolean))],
    [events],
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return events.filter((e) => {
      if (areaFilter && e.canonicalKey !== areaFilter) return false;
      if (kindFilter && e.kind !== kindFilter) return false;
      if (q) {
        const blob = `${e.title} ${e.reason} ${e.kind}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });
  }, [events, areaFilter, kindFilter, search]);

  if (!open) return null;

  return (
    <Modal onClose={onClose} className="scientific-xp-history-modal" portal zIndex={1210}>
      <div className="scientific-xp-history-inner">
        <h2>Histórico de XP</h2>
        <p className="scientific-muted">{filtered.length} evento(s)</p>

        <div className="scientific-notebook-filters scientific-notebook-filters--modal">
          <label>
            Buscar
            <input
              type="search"
              className="scientific-search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
          <label>
            Área
            <select
              className="scientific-search-input"
              value={areaFilter}
              onChange={(e) => setAreaFilter(e.target.value)}
            >
              <option value="">Todas</option>
              {areas.map((id) => (
                <option key={id} value={id}>
                  {interestLabelById(id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tipo
            <select
              className="scientific-search-input"
              value={kindFilter}
              onChange={(e) => setKindFilter(e.target.value)}
            >
              {KIND_FILTER.map((k) => (
                <option key={k.id || 'all'} value={k.id}>
                  {k.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <ul className="scientific-xp-history-list">
          {filtered.length === 0 && <li className="scientific-muted">Nenhum evento.</li>}
          {filtered.map((e) => (
            <li key={e.id} className="scientific-xp-history-item">
              <span className="scientific-xp-history-amount">+{e.xp} XP</span>
              <span>{e.title}</span>
              <span className="scientific-muted">
                {new Date(e.date).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
                {e.canonicalKey ? ` · ${interestLabelById(e.canonicalKey)}` : ''}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </Modal>
  );
}
