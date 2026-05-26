import { useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import {
  SESSION_FOCUS_OPTIONS,
  getStudySessionStats,
} from '../../utils/scientific/scientificStudySessionStorage';
import { interestLabelById } from '../../utils/scientific/scientificInterestsConfig';

const PERIOD_OPTIONS = [
  { id: 'all', label: 'Todo o período' },
  { id: '7d', label: 'Últimos 7 dias' },
  { id: '30d', label: 'Últimos 30 dias' },
];

function inPeriod(iso, periodId) {
  if (!iso || periodId === 'all') return true;
  const t = new Date(iso).getTime();
  const now = Date.now();
  const days = periodId === '7d' ? 7 : 30;
  return now - t <= days * 24 * 60 * 60 * 1000;
}

export default function ScientificStudySessionsModal({ open, onClose }) {
  const { studySessions = [] } = useScientificWorkspace();
  const [areaFilter, setAreaFilter] = useState('');
  const [periodFilter, setPeriodFilter] = useState('all');
  const [focusFilter, setFocusFilter] = useState('');

  const areas = useMemo(() => {
    const keys = new Set(studySessions.map((s) => s.canonicalKey).filter(Boolean));
    return [...keys];
  }, [studySessions]);

  const filtered = useMemo(() => {
    return studySessions.filter((s) => {
      if (areaFilter && s.canonicalKey !== areaFilter) return false;
      if (focusFilter && s.focus !== focusFilter) return false;
      if (!inPeriod(s.finishedAt || s.startedAt, periodFilter)) return false;
      return true;
    });
  }, [studySessions, areaFilter, focusFilter, periodFilter]);

  const stats = useMemo(() => getStudySessionStats(filtered), [filtered]);

  if (!open) return null;

  return (
    <Modal onClose={onClose} className="scientific-sessions-modal" portal zIndex={1210}>
      <div className="scientific-sessions-modal-inner">
        <h2>Histórico de sessões</h2>

        <div className="scientific-sessions-filters">
          <label className="scientific-trail-filter-label">
            Área
            <select
              className="scientific-search-input"
              value={areaFilter}
              onChange={(e) => setAreaFilter(e.target.value)}
            >
              <option value="">Todas</option>
              {areas.map((k) => (
                <option key={k} value={k}>
                  {interestLabelById(k) || k}
                </option>
              ))}
            </select>
          </label>
          <label className="scientific-trail-filter-label">
            Período
            <select
              className="scientific-search-input"
              value={periodFilter}
              onChange={(e) => setPeriodFilter(e.target.value)}
            >
              {PERIOD_OPTIONS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </label>
          <label className="scientific-trail-filter-label">
            Foco
            <select
              className="scientific-search-input"
              value={focusFilter}
              onChange={(e) => setFocusFilter(e.target.value)}
            >
              <option value="">Todos</option>
              {SESSION_FOCUS_OPTIONS.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <p className="scientific-muted">
          {stats.sessionCount} sessões · {stats.totalMinutes} min · {stats.totalXp} XP
        </p>

        <ul className="scientific-sessions-history-list">
          {filtered.length === 0 && <li className="scientific-muted">Nenhuma sessão neste filtro.</li>}
          {filtered.map((s) => {
            const focusLabel =
              SESSION_FOCUS_OPTIONS.find((f) => f.id === s.focus)?.label || s.focus;
            return (
              <li key={s.id} className="scientific-sessions-history-item">
                <strong>{s.title}</strong>
                <span className="scientific-muted">
                  {' '}
                  — {s.durationMinutes} min · {focusLabel} · +{s.xpAwarded || 0} XP
                </span>
                {s.reflection?.learned && (
                  <p className="scientific-sessions-reflection-snippet">{s.reflection.learned}</p>
                )}
                {s.reflection?.nextAction && (
                  <p className="scientific-muted">
                    Próxima ação: {s.reflection.nextAction}
                  </p>
                )}
              </li>
            );
          })}
        </ul>

        <button type="button" className="scientific-btn scientific-btn-ghost" onClick={onClose}>
          Fechar
        </button>
      </div>
    </Modal>
  );
}
