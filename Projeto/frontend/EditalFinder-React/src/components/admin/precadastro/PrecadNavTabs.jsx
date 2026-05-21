const TABS = [
  { id: 'visao', label: 'Visão geral' },
  { id: 'resumo', label: 'Resumo' },
  { id: 'aderencia', label: 'Aderência' },
  { id: 'escopo', label: 'Escopo e plano' },
  { id: 'orcamento', label: 'Orçamento' },
  { id: 'riscos', label: 'Riscos e passos' },
  { id: 'completo', label: 'Formulário completo' },
];

export default function PrecadNavTabs({ active, onChange, compact = false }) {
  return (
    <nav
      className={`precad-nav-tabs${compact ? ' precad-nav-tabs--compact' : ''}`}
      aria-label="Seções do pré-projeto consultivo"
    >
      {TABS.map((t) => (
        <button
          key={t.id}
          type="button"
          className={`precad-nav-tab ${active === t.id ? 'is-active' : ''}`}
          onClick={() => onChange(t.id)}
        >
          {t.label}
        </button>
      ))}
    </nav>
  );
}
