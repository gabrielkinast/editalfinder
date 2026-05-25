import { useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';

const SECTIONS = [
  { id: 'scientific-route', label: 'Rota' },
  { id: 'scientific-interests', label: 'Interesses' },
  { id: 'scientific-projects', label: 'Projetos' },
  { id: 'scientific-study-path', label: 'Trilha' },
  { id: 'scientific-notebook', label: 'Caderno' },
  { id: 'scientific-feed', label: 'Feed' },
];

export default function ScientificSectionNav() {
  const [active, setActive] = useState('scientific-route');
  const { scrollToSection } = useScientificWorkspace() || {};

  const handleClick = (id, label) => {
    setActive(id);
    scrollToSection?.(id, 'section_nav', label);
  };

  return (
    <nav className="scientific-section-nav" aria-label="Navegação do workspace científico">
      {SECTIONS.map((s) => (
        <button
          key={s.id}
          type="button"
          className={`scientific-section-nav-btn ${active === s.id ? 'scientific-section-nav-btn--active' : ''}`}
          onClick={() => handleClick(s.id, s.label)}
        >
          {s.label}
        </button>
      ))}
    </nav>
  );
}
