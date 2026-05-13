/**
 * Badge genérico para status / etiquetas (variantes discretas, compatível com tema claro/escuro).
 * Estilos: `global.css` (`.status-badge`, `.status-badge--*`).
 */
const VARIANT_CLASS = {
  default: 'status-badge--default',
  success: 'status-badge--success',
  warning: 'status-badge--warning',
  muted: 'status-badge--muted',
  danger: 'status-badge--danger',
};

export default function StatusBadge({
  children,
  variant = 'default',
  title,
  className = '',
  style: extraStyle = {},
}) {
  const mod = VARIANT_CLASS[variant] || VARIANT_CLASS.default;
  return (
    <span
      className={['status-badge', mod, className].filter(Boolean).join(' ')}
      title={title}
      style={extraStyle}
    >
      {children}
    </span>
  );
}
