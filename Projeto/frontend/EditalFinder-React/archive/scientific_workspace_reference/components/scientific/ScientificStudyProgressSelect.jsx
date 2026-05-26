import { useRef } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import {
  STUDY_PROGRESS_STATUSES,
  STUDY_PROGRESS_STATUS_LABELS,
} from '../../utils/scientific/scientificStudyProgressConstants';

/**
 * @param {object} props
 * @param {string} props.progressKey
 * @param {object} [props.itemMeta] — metadados para verificação de domínio
 */
export default function ScientificStudyProgressSelect({ progressKey, itemMeta, className = '' }) {
  const ctx = useScientificWorkspace();
  const status = ctx?.getStudyProgressStatus?.(progressKey) || 'a_estudar';
  const selectRef = useRef(null);

  const handleChange = (e) => {
    const next = e.target.value;
    if (next === 'dominado' && itemMeta && ctx?.requestStudyStatusChange) {
      ctx.requestStudyStatusChange(progressKey, next, itemMeta);
      const prev = status;
      if (selectRef.current) selectRef.current.value = prev;
      return;
    }
    if (ctx?.requestStudyStatusChange) {
      ctx.requestStudyStatusChange(progressKey, next, itemMeta);
    } else {
      ctx?.setStudyProgressStatus?.(progressKey, next, itemMeta);
    }
  };

  return (
    <select
      ref={selectRef}
      className={`scientific-progress-select scientific-progress-select--${status} ${className}`.trim()}
      value={status}
      disabled={!ctx?.setStudyProgressStatus}
      aria-label="Status de estudo"
      onChange={handleChange}
      onClick={(e) => e.stopPropagation()}
    >
      {STUDY_PROGRESS_STATUSES.map((id) => (
        <option key={id} value={id}>
          {STUDY_PROGRESS_STATUS_LABELS[id]}
        </option>
      ))}
    </select>
  );
}
