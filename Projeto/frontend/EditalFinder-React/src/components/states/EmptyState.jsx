/**
 * Estado vazio — lista ou resultado sem itens.
 */
export default function EmptyState({
  title = 'Nenhum item encontrado',
  hint = null,
  children = null,
  className = '',
}) {
  return (
    <div className={`empty-state ${className}`.trim()}>
      <h3>{title}</h3>
      {hint ? (
        <p style={{ marginTop: '8px', maxWidth: '520px', marginLeft: 'auto', marginRight: 'auto' }}>{hint}</p>
      ) : null}
      {children}
    </div>
  );
}
