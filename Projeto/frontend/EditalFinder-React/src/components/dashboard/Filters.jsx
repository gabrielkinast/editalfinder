import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';

export default function Filters({ onFilterChange }) {
  const [orgsFromDb, setOrgsFromDb] = useState([]);
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
    orgs: {}, // Inicialmente vazio, será preenchido dinamicamente
  });

  // Carregar organizações do banco
  useEffect(() => {
    const loadOrgs = async () => {
      try {
        const data = await dataService.getOrganizations();
        setOrgsFromDb(data);
        
        // Inicializa o estado dos filtros com as orgs do banco
        const initialOrgsState = {};
        data.forEach(org => {
          initialOrgsState[org.nome.toLowerCase()] = false;
        });
        
        setFilters(prev => ({
          ...prev,
          orgs: {
            ...initialOrgsState,
            cnpq: false,
            fapergs: false,
            finep: false,
            bndes: false,
            cordis: false,
          }
        }));
      } catch (error) {
        console.error('Erro ao carregar organizações para filtros:', error);
      }
    };
    loadOrgs();
  }, []);

  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  const handleChange = (e) => {
    const { id, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (id.startsWith('org-')) {
        const orgKey = id.replace('org-', '');
        setFilters(prev => ({
          ...prev,
          orgs: { ...prev.orgs, [orgKey]: checked }
        }));
      } else {
        setFilters(prev => ({ ...prev, [id.replace('Filter', '')]: checked }));
      }
    } else {
      setFilters(prev => ({ ...prev, [id.replace('Filter', '')]: value }));
    }
  };

  const clearFilters = () => {
    const resetOrgs = {};
    Object.keys(filters.orgs).forEach(key => {
      resetOrgs[key] = false;
    });

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
      orgs: resetOrgs,
    });
  };

  const formatCurrency = (value) => {
    if (value >= 1000000) return `R$ ${value / 1000000} mi`;
    return `R$ ${value.toLocaleString('pt-BR')}`;
  };

  return (
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
          <option value="Acre">Acre</option>
          <option value="Alagoas">Alagoas</option>
          <option value="Amapá">Amapá</option>
          <option value="Amazonas">Amazonas</option>
          <option value="Bahia">Bahia</option>
          <option value="Ceará">Ceará</option>
          <option value="Distrito Federal">Distrito Federal</option>
          <option value="Espírito Santo">Espírito Santo</option>
          <option value="Goiás">Goiás</option>
          <option value="Maranhão">Maranhão</option>
          <option value="Mato Grosso">Mato Grosso</option>
          <option value="Mato Grosso do Sul">Mato Grosso do Sul</option>
          <option value="Minas Gerais">Minas Gerais</option>
          <option value="Pará">Pará</option>
          <option value="Paraíba">Paraíba</option>
          <option value="Paraná">Paraná</option>
          <option value="Pernambuco">Pernambuco</option>
          <option value="Piauí">Piauí</option>
          <option value="Rio de Janeiro">Rio de Janeiro</option>
          <option value="Rio Grande do Norte">Rio Grande do Norte</option>
          <option value="Rio Grande do Sul">Rio Grande do Sul</option>
          <option value="Rondônia">Rondônia</option>
          <option value="Roraima">Roraima</option>
          <option value="Santa Catarina">Santa Catarina</option>
          <option value="São Paulo">São Paulo</option>
          <option value="Sergipe">Sergipe</option>
          <option value="Tocantins">Tocantins</option>
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
          <option value="Agro">Agro</option>
          <option value="Saúde">Saúde</option>
          <option value="Energia">Energia</option>
          <option value="Tecnologia">Tecnologia</option>
          <option value="Educação">Educação</option>
        </select>
      </div>

      {/* Órgão Financiador */}
      <div className="filter-group">
        <h3 className="filter-label">Órgão Financiador</h3>
        <div className="checkbox-list">
          {/* Órgãos Estáticos */}
          {['CNPQ', 'FAPERGS', 'FINEP', 'BNDES', 'CORDIS'].map(org => (
            <label key={org} className="checkbox-label">
              <input 
                type="checkbox" 
                id={`org-${org.toLowerCase()}`}
                checked={filters.orgs[org.toLowerCase()] || false}
                onChange={handleChange}
              />
              <span>{org}</span>
            </label>
          ))}
          
          {/* Órgãos Dinâmicos do Banco */}
          {orgsFromDb.map(org => (
            // Evita duplicar se já estiver na lista estática
            !['CNPQ', 'FAPERGS', 'FINEP', 'BNDES', 'CORDIS'].includes(org.nome.toUpperCase()) && (
              <label key={org.id_organizacao} className="checkbox-label">
                <input 
                  type="checkbox" 
                  id={`org-${org.nome.toLowerCase()}`}
                  checked={filters.orgs[org.nome.toLowerCase()] || false}
                  onChange={handleChange}
                />
                <span>{org.nome}</span>
              </label>
            )
          ))}
        </div>
      </div>

      <button className="btn-clear-filters" onClick={clearFilters}>
        Limpar Filtros
      </button>
    </div>
  );
}
