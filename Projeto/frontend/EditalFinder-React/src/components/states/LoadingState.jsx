/**
 * Estado de carregamento reutilizável — visual alinhado ao restante do app (padding central).
 */
export default function LoadingState({ title = 'Carregando…', subtitle = null, className = '' }) {
  return (
    <div
      className={className}
      style={{
        textAlign: 'center',
        padding: '48px 20px',
        color: 'var(--color-text, #333)',
      }}
    >
      <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: subtitle ? '8px' : 0, color: 'var(--color-text)' }}>{title}</h3>
      {subtitle ? (
        <p style={{ fontSize: '14px', color: 'var(--color-muted)', margin: 0 }}>{subtitle}</p>
      ) : null}
    </div>
  );
}
