/** Skeleton de cards enquanto o radar calcula (cliente sem cache). */
export default function RadarResultsSkeleton({ rows = 6 }) {
  const n = Math.max(3, Math.min(rows, 12));
  return (
    <div className="radar-skeleton-grid" role="status" aria-live="polite" aria-busy="true">
      <p className="radar-skeleton-hint">Carregando oportunidades compatíveis…</p>
      {Array.from({ length: n }, (_, i) => (
        <div key={i} className="radar-skeleton-card" />
      ))}
    </div>
  );
}
