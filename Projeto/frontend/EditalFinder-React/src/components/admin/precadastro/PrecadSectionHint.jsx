/** Bloco de ajuda curta por seção consultiva. */
export default function PrecadSectionHint({ children }) {
  if (!children) return null;
  return <p className="precad-section-hint precad-muted small">{children}</p>;
}
