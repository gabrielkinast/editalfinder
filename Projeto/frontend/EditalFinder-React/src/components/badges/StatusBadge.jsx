/**
 * Badge genérico para status / etiquetas (variantes discretas, compatível com o tema atual).
 */
const VARIANT_STYLES = {
  default: { background: '#e3f2fd', color: '#1565c0', border: '1px solid #90caf9' },
  success: { background: '#e8f5e9', color: '#2e7d32', border: '1px solid #a5d6a7' },
  warning: { background: '#fff3e0', color: '#e65100', border: '1px solid #ffcc80' },
  muted: { background: '#f5f5f5', color: '#616161', border: '1px solid #e0e0e0' },
  danger: { background: '#ffebee', color: '#c62828', border: '1px solid #ef9a9a' },
};

export default function StatusBadge({
  children,
  variant = 'default',
  title,
  className = '',
  style: extraStyle = {},
}) {
  const base = VARIANT_STYLES[variant] || VARIANT_STYLES.default;
  return (
    <span
      className={className}
      title={title}
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '6px',
        fontSize: '12px',
        fontWeight: 600,
        lineHeight: 1.4,
        ...base,
        ...extraStyle,
      }}
    >
      {children}
    </span>
  );
}
