import { logScientificWorkspace } from './scientificWorkspaceLog';

export const SCIENTIFIC_STUDY_SESSIONS_STORAGE_KEY = 'scientific_workspace_study_sessions';

export {
  SESSION_FOCUS_OPTIONS,
  SESSION_LEVEL_OPTIONS,
  SESSION_STATUS_OPTIONS,
  SESSION_QUANTITY_OPTIONS,
  KIND_DISPLAY_LABELS,
  SOURCE_DISPLAY_LABELS,
} from './scientificStudySessionConstants';

export const SESSION_DURATION_OPTIONS = [
  { minutes: 15, label: '15 min' },
  { minutes: 30, label: '30 min' },
  { minutes: 45, label: '45 min' },
  { minutes: 60, label: '60 min' },
];

/**
 * @returns {{ sessions: Array<object> }}
 */
export function loadStudySessions() {
  try {
    const raw = localStorage.getItem(SCIENTIFIC_STUDY_SESSIONS_STORAGE_KEY);
    if (!raw) return { sessions: [] };
    const parsed = JSON.parse(raw);
    return {
      sessions: Array.isArray(parsed?.sessions) ? parsed.sessions : [],
    };
  } catch {
    return { sessions: [] };
  }
}

export function saveStudySessions(data) {
  try {
    localStorage.setItem(SCIENTIFIC_STUDY_SESSIONS_STORAGE_KEY, JSON.stringify(data));
  } catch {
    /* ignore */
  }
}

/**
 * @param {object} session
 */
export function addStudySession(session) {
  const data = loadStudySessions();
  const sessions = [session, ...data.sessions].slice(0, 100);
  saveStudySessions({ sessions });
  logScientificWorkspace('study_session_saved', { id: session.id, canonicalKey: session.canonicalKey });
  return { sessions };
}

export function getStudySessionStats(sessions = []) {
  const totalMinutes = sessions.reduce((n, s) => n + (s.durationMinutes || 0), 0);
  const totalXp = sessions.reduce((n, s) => n + (s.xpAwarded || 0), 0);
  const byArea = {};
  for (const s of sessions) {
    const k = s.canonicalKey || 'geral';
    byArea[k] = (byArea[k] || 0) + (s.durationMinutes || 0);
  }
  const topAreas = Object.entries(byArea)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  return { totalMinutes, totalXp, sessionCount: sessions.length, byArea, topAreas };
}
