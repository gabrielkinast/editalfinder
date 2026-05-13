import { useMemo, useState, useEffect, useCallback } from 'react';

const DEFAULT_FILTERS = {
  fonte_recurso: '',
  regiao: '',
  pais: '',
  validacao_status: '',
  tipo_conteudo: '',
  tag: '',
  somenteAtivos: false,
};

function uniqStrings(rows, accessor) {
  const s = new Set();
  rows.forEach((r) => {
    const v = accessor(r);
    if (v != null && String(v).trim() !== '') s.add(String(v).trim());
  });
  return Array.from(s).sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

function allTags(rows) {
  const s = new Set();
  rows.forEach((r) => {
    (r.tags || []).forEach((t) => {
      if (t && String(t).trim()) s.add(String(t).trim());
    });
  });
  return Array.from(s).sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

export default function FeedSidebarFilters({ items, onFilterChange }) {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);

  const fontes = useMemo(() => uniqStrings(items, (r) => r.fonte_recurso), [items]);
  const regioes = useMemo(() => uniqStrings(items, (r) => r.regiao), [items]);
  const paises = useMemo(() => uniqStrings(items, (r) => r.pais), [items]);
  const validacoes = useMemo(() => uniqStrings(items, (r) => r.validacao_status), [items]);
  const tipos = useMemo(() => uniqStrings(items, (r) => r.tipo_conteudo || r.content_type), [items]);
  const tags = useMemo(() => allTags(items), [items]);

  const emit = useCallback(
    (f) => {
      onFilterChange(f);
    },
    [onFilterChange]
  );

  useEffect(() => {
    emit(filters);
  }, [filters, emit]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const clearFilters = () => setFilters(DEFAULT_FILTERS);

  return (
    <div className="filters-section">
      <div className="filters-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '-10px' }}>
        <h2 className="filter-title" style={{ margin: 0 }}>Filtros</h2>
        <button
          type="button"
          className="btn-clear-filters"
          onClick={clearFilters}
          style={{ width: 'auto', marginTop: 0, padding: '6px 12px', fontSize: '11px' }}
        >
          Limpar Filtros
        </button>
      </div>

      <div className="filter-group">
        <label className="checkbox-label">
          <input type="checkbox" name="somenteAtivos" checked={filters.somenteAtivos} onChange={handleChange} />
          <span>Somente registros ativos</span>
        </label>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Fonte recurso</h3>
        <select name="fonte_recurso" className="filter-select" value={filters.fonte_recurso} onChange={handleChange}>
          <option value="">Todas</option>
          {fontes.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Região</h3>
        <select name="regiao" className="filter-select" value={filters.regiao} onChange={handleChange}>
          <option value="">Todas</option>
          {regioes.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">País</h3>
        <select name="pais" className="filter-select" value={filters.pais} onChange={handleChange}>
          <option value="">Todos</option>
          {paises.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Validação</h3>
        <select name="validacao_status" className="filter-select" value={filters.validacao_status} onChange={handleChange}>
          <option value="">Todos os status</option>
          {validacoes.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Tipo / conteúdo</h3>
        <select name="tipo_conteudo" className="filter-select" value={filters.tipo_conteudo} onChange={handleChange}>
          <option value="">Todos</option>
          {tipos.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Tag</h3>
        <select name="tag" className="filter-select" value={filters.tag} onChange={handleChange}>
          <option value="">Qualquer tag</option>
          {tags.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
