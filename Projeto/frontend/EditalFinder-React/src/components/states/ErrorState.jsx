/**
 * Estado de erro — usa classe global `.empty-state` quando possível.
 */
export default function ErrorState({
  title = 'Não foi possível carregar',
  message,
  children = null,
  className = '',
}) {
  return (
    <div className={`empty-state ${className}`.trim()}>
      <h3>{title}</h3>
      {message ? (
        <p style={{ marginTop: '8px', maxWidth: '560px', marginLeft: 'auto', marginRight: 'auto' }}>{message}</p>
      ) : null}
      {children}
    </div>
  );
}
