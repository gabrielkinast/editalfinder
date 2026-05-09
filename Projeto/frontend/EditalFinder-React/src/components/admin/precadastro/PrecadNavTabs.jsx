const TABS = [
  { id: 'visao', label: 'Visão geral' },
  { id: 'contexto', label: 'Contexto e projeto' },
  { id: 'completo', label: 'Formulário completo' },
];

export default function PrecadNavTabs({ active, onChange }) {
  return (
    <nav className="precad-nav-tabs" aria-label="Seções do pré-cadastro">
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
