/**
 * XP de sessões de estudo (Fase 2L) — sem duplicar por sessionId.
 */

export function reflectionIsFilled(reflection = {}) {
  const fields = [
    reflection.learned,
    reflection.understood,
    reflection.confused,
    reflection.nextAction,
    reflection.professorQuestion,
  ];
  return fields.filter((f) => String(f || '').trim().length >= 8).length >= 2;
}

/**
 * @param {object} params
 */
export function calculateSessionXp({ durationMinutes = 0, reflection = {}, hasProfessorQuestion = false }) {
  let xp = 0;
  const mins = Number(durationMinutes) || 0;
  if (mins >= 45) xp += 15;
  else if (mins >= 30) xp += 10;
  else if (mins >= 15) xp += 5;

  if (reflectionIsFilled(reflection)) xp += 5;
  if (hasProfessorQuestion || String(reflection.professorQuestion || '').trim().length >= 10) {
    xp += 5;
  }
  return xp;
}

export function sessionXpProgressKey(sessionId) {
  return `session::${sessionId}`;
}
