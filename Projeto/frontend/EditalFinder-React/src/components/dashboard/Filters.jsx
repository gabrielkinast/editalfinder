import { useState, useEffect } from 'react';

export default function Filters({ onFilterChange }) {
  const [filters, setFilters] = useState({
    state: '',
    nacional: false,
    internacional: false,
    keyword: '',
    resourceType: '',
    creditMax: 100000000,
    startDate: '',
    endDate: '',
    area: '',
    orgs: {
      fapergs: false,
      finep: false,
      bndes: false,
      cordis: false,
    },
  });

  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  const handleChange = (e) => {
    const { id, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (id.includes('Filter')) {
        const orgKey = id.replace('Filter', '');
        if (orgsKeys.includes(orgKey)) {
          setFilters(prev => ({
            ...prev,
            orgs: { ...prev.orgs, [orgKey]: checked }
          }));
          return;
        }
      }
      setFilters(prev => ({ ...prev, [id.replace('Filter', '')]: checked }));
    } else {
      setFilters(prev => ({ ...prev, [id.replace('Filter', '')]: value }));
    }
  };

  const orgsKeys = ['fapergs', 'finep', 'bndes', 'cordis'];

  const clearFilters = () => {
    setFilters({
      state: '',
      nacional: false,
      internacional: false,
      keyword: '',
      resourceType: '',
      creditMax: 100000000,
      startDate: '',
      endDate: '',
      area: '',
      orgs: {
        fapergs: false,
        finep: false,
        bndes: false,
        cordis: false,
      },
    });
  };

  const formatCurrency = (value) => {
    if (value >= 1000000) return `R$ ${value / 1000000} mi`;
    return `R$ ${value.toLocaleString('pt-BR')}`;
  };

  return (
    <aside className="sidebar">
      <div className="filters-section">
        <h2 className="filter-title">Filtros</h2>

        {/* Localidade */}
        <div className="filter-group">
          <h3 className="filter-label">Localidade</h3>
          <select 
            id="stateFilter" 
            className="filter-select"
            value={filters.state}
            onChange={handleChange}
          >
            <option value="">Todos os estados</option>
            <option value="AC">Acre</option>
            <option value="AL">Alagoas</option>
            <option value="AP">Amapá</option>
            <option value="AM">Amazonas</option>
            <option value="BA">Bahia</option>
            <option value="CE">Ceará</option>
            <option value="DF">Distrito Federal</option>
            <option value="ES">Espírito Santo</option>
            <option value="GO">Goiás</option>
            <option value="MA">Maranhão</option>
            <option value="MT">Mato Grosso</option>
            <option value="MS">Mato Grosso do Sul</option>
            <option value="MG">Minas Gerais</option>
            <option value="PA">Pará</option>
            <option value="PB">Paraíba</option>
            <option value="PR">Paraná</option>
            <option value="PE">Pernambuco</option>
            <option value="PI">Piauí</option>
            <option value="RJ">Rio de Janeiro</option>
            <option value="RN">Rio Grande do Norte</option>
            <option value="RS">Rio Grande do Sul</option>
            <option value="RO">Rondônia</option>
            <option value="RR">Roraima</option>
            <option value="SC">Santa Catarina</option>
            <option value="SP">São Paulo</option>
            <option value="SE">Sergipe</option>
            <option value="TO">Tocantins</option>
          </select>

          <div className="checkbox-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                id="nacionalFilter" 
                checked={filters.nacional}
                onChange={handleChange}
              />
              <span>Nacional</span>
            </label>
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                id="internacionalFilter" 
                checked={filters.internacional}
                onChange={handleChange}
              />
              <span>Internacional</span>
            </label>
          </div>
        </div>

        {/* Pesquisa por Palavras */}
        <div className="filter-group">
          <h3 className="filter-label">Pesquisa</h3>
          <input 
            type="text" 
            id="keywordFilter" 
            placeholder="Ex: agro, saúde, energia"
            className="filter-input"
            value={filters.keyword}
            onChange={handleChange}
          />
        </div>

        {/* Tipo de Recurso */}
        <div className="filter-group">
          <h3 className="filter-label">Tipo de Recurso</h3>
          <select 
            id="resourceTypeFilter" 
            className="filter-select"
            value={filters.resourceType}
            onChange={handleChange}
          >
            <option value="">Todos os tipos</option>
            <option value="Subvenção econômica">Subvenção econômica</option>
            <option value="Linha de crédito">Linha de crédito</option>
            <option value="Investimento">Investimento</option>
            <option value="Fomento à inovação">Fomento à inovação</option>
            <option value="Bolsa pesquisa">Bolsa pesquisa</option>
          </select>
        </div>

        {/* Faixa de Crédito */}
        <div className="filter-group">
          <h3 className="filter-label">Faixa de Crédito</h3>
          <div className="range-container">
            <input 
              type="range" 
              id="creditMaxFilter" 
              min="100000" 
              max="100000000" 
              step="100000"
              value={filters.creditMax}
              onChange={handleChange}
              className="range-slider"
            />
            <div className="range-display">
              <span>Até: <strong>{formatCurrency(filters.creditMax)}</strong></span>
            </div>
          </div>
        </div>

        {/* Filtro por Datas */}
        <div className="filter-group">
          <h3 className="filter-label">Datas</h3>
          <input 
            type="date" 
            id="startDateFilter" 
            className="filter-input"
            value={filters.startDate}
            onChange={handleChange}
          />
          <input 
            type="date" 
            id="endDateFilter" 
            className="filter-input"
            value={filters.endDate}
            onChange={handleChange}
          />
        </div>

        {/* Área */}
        <div className="filter-group">
          <h3 className="filter-label">Área</h3>
          <select 
            id="areaFilter" 
            className="filter-select"
            value={filters.area}
            onChange={handleChange}
          >
            <option value="">Todas as áreas</option>
            <option value="Saúde">Saúde</option>
            <option value="Agro">Agro</option>
            <option value="Educação">Educação</option>
            <option value="Tecnologia">Tecnologia</option>
            <option value="Energia">Energia</option>
            <option value="Indústria">Indústria</option>
          </select>
        </div>

        {/* Órgão Financiador */}
        <div className="filter-group">
          <h3 className="filter-label">Órgão Financiador</h3>
          <div className="checkbox-group">
            {orgsKeys.map(org => (
              <label key={org} className="checkbox-label">
                <input 
                  type="checkbox" 
                  id={`${org}Filter`} 
                  checked={filters.orgs[org]}
                  onChange={handleChange}
                />
                <span style={{ textTransform: 'uppercase' }}>{org}</span>
              </label>
            ))}
          </div>
        </div>

        <button 
          id="clearFiltersBtn" 
          className="btn-clear-filters"
          onClick={clearFilters}
        >
          Limpar Filtros
        </button>
      </div>
    </aside>
  );
}
