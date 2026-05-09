/**
 * Sugestões de impactos conforme setor — não marca checkboxes; orienta o usuário.
 */

export default function PrecadImpactHints({ hints }) {
  if (!hints || (!hints.economicos?.length && !hints.sociais?.length && !hints.ambientais?.length))
    return null;

  const block = (title, items) =>
    items?.length ? (
      <div className="precad-impact-hint-col">
        <h4>{title}</h4>
        <ul>
          {items.map((x, i) => (
            <li key={i}>{x}</li>
          ))}
        </ul>
      </div>
    ) : null;

  return (
    <div className="precad-impact-hints">
      <h3 className="precad-subtitle">Possíveis impactos (somente orientação)</h3>
      <p className="precad-muted small">
        Com base no setor inferido, estes são <strong>tópicos típicos</strong> para considerar nos checkboxes —
        você escolhe o que faz sentido para o caso real e complementa observações onde precisar.
      </p>
      <div className="precad-impact-hint-grid">
        {block('Econômicos', hints.economicos)}
        {block('Sociais', hints.sociais)}
        {block('Ambientais', hints.ambientais)}
      </div>
    </div>
  );
}
