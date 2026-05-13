/** Parse datas ISO ou yyyy-mm-dd. */
export function parseDateLoose(raw) {
  if (raw == null || raw === '') return null;
  const s = String(raw).trim();
  if (/^\d{10,13}$/.test(s)) {
    const n = Number(s);
    const d = new Date(n < 1e11 ? n * 1000 : n);
    if (!Number.isNaN(d.getTime())) return d;
  }
  const d = s.includes('T') ? new Date(s) : new Date(`${s.slice(0, 10)}T12:00:00`);
  if (Number.isNaN(d.getTime())) return null;
  return d;
}

export function startOfTodayLocal() {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return now.getTime();
}

export function prazoVencido(prazo_envio, nowMs = Date.now()) {
  const d = parseDateLoose(prazo_envio);
  if (!d) return false;
  return d.getTime() < startOfTodayLocal();
}

/**
 * Prazo nulo → não vencido.
 * Usa prazo_envio, fim_inscricao ou dataLimite já normalizada no mapper.
 */
export function isPrazoVencidoEdital(edital) {
  if (!edital) return false;
  const raw =
    edital.prazo_envio_raw ??
    edital.fim_inscricao_raw ??
    edital.dataLimite ??
    edital.prazo_envio ??
    null;
  if (raw == null || raw === '') return false;
  const d = parseDateLoose(raw);
  if (!d || Number.isNaN(d.getTime())) return false;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return d < hoje;
}

export function diasAtePrazoDashboard(prazo_envio, nowMs = Date.now()) {
  const d = parseDateLoose(prazo_envio);
  if (!d) return null;
  const end = startOfTodayLocal();
  return Math.ceil((d.getTime() - end) / 86400000);
}
