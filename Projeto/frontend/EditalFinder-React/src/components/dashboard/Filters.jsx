import { useState, useEffect, useMemo } from 'react';
import { dataService } from '../../services/dataService';

export default function Filters({ onFilterChange, allEditais = [] }) {
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

  // Extrair todas as áreas únicas dos editais carregados
  const availableAreas = useMemo(() => {
    const areas = new Set();
    
    // Adiciona áreas padrão
    ['Agro', 'Saúde', 'Energia', 'Tecnologia', 'Educação'].forEach(a => areas.add(a));
    
    // Adiciona todas as áreas encontradas nos editais
    allEditais.forEach(edital => {
      if (edital.area) {
        // Suporta vírgula (,) e ponto e vírgula (;) como separadores
        const parts = edital.area.split(/[,;]/).map(p => p.trim());
        parts.forEach(p => {
          // Ignora textos vazios, muito longos (provavelmente descrições) ou que contenham "manual" (provavelmente erro de cadastro)
          if (p && p.length < 50 && !p.toLowerCase().includes('manual')) {
            // Capitaliza a primeira letra para manter o padrão
            const capitalized = p.charAt(0).toUpperCase() + p.slice(1).toLowerCase();
            areas.add(capitalized);
          }
        });
      }
    });
    
    return Array.from(areas).sort();
  }, [allEditais]);

  // Extrair todos os tipos de recursos únicos dos editais carregados
  const availableResourceTypes = useMemo(() => {
    const types = new Set();
    
    // Adiciona tipos padrão que sempre devem aparecer
    ['Subvenção econômica', 'Linha de crédito', 'Investimento', 'Fomento à inovação', 'Bolsa pesquisa'].forEach(t => types.add(t));
    
    // Adiciona todos os tipos encontrados nos editais
    allEditais.forEach(edital => {
      if (edital.tipoRecurso) {
        // Normaliza para manter o padrão (primeira letra maiúscula)
        const tr = edital.tipoRecurso.trim();
        const formatted = tr.charAt(0).toUpperCase() + tr.slice(1).toLowerCase();
        types.add(formatted);
      }
    });
    
    return Array.from(types).sort();
  }, [allEditais]);

  // Extrair todos os órgãos financiadores únicos dos editais carregados
  const availableOrgs = useMemo(() => {
    const orgs = new Set();
    
    // Adiciona órgãos padrão que sempre devem aparecer
    ['CNPQ', 'FAPERGS', 'FINEP', 'BNDES', 'CORDIS'].forEach(o => orgs.add(o));
    
    // Adiciona todos os órgãos encontrados nos editais
    allEditais.forEach(edital => {
      if (edital.orgao && edital.orgao !== 'Manual') {
        // Normaliza para maiúsculas para evitar duplicatas (ex: cnpq e CNPq)
        orgs.add(edital.orgao.toUpperCase());
      }
    });
    
    return Array.from(orgs).sort();
  }, [allEditais]);

  // Atualiza o estado dos filtros quando novos órgãos são descobertos
  useEffect(() => {
    setFilters(prev => {
      const newOrgsState = { ...prev.orgs };
      let changed = false;
      
      availableOrgs.forEach(org => {
        const key = org.toLowerCase();
        if (newOrgsState[key] === undefined) {
          newOrgsState[key] = false;
          changed = true;
        }
      });
      
      if (changed) {
        return { ...prev, orgs: newOrgsState };
      }
      return prev;
    });
  }, [availableOrgs]);

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
    return `R$ ${Number(value).toLocaleString('pt-BR')}`;
  };

  return (
    <div className="filters-section">
      <div className="filters-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '-10px' }}>
        <h2 className="filter-title" style={{ margin: 0 }}>Filtros</h2>
        <button 
          className="btn-clear-filters" 
          onClick={clearFilters}
          style={{ width: 'auto', marginTop: 0, padding: '6px 12px', fontSize: '11px' }}
        >
          Limpar Filtros
        </button>
      </div>

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
          {availableResourceTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
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
            step="5000"
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-light)', marginBottom: '4px', display: 'block' }}>Data Início</label>
            <input 
              type="date" 
              id="startDateFilter" 
              className="filter-input"
              value={filters.startDate}
              onChange={handleChange}
            />
          </div>
          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-light)', marginBottom: '4px', display: 'block' }}>Data Fim</label>
            <input 
              type="date" 
              id="endDateFilter" 
              className="filter-input"
              value={filters.endDate}
              onChange={handleChange}
            />
          </div>
        </div>
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
          {availableAreas.map(area => (
            <option key={area} value={area}>{area}</option>
          ))}
        </select>
      </div>

      {/* Órgão Financiador */}
      <div className="filter-group">
        <h3 className="filter-label">Órgão Financiador</h3>
        <div className="checkbox-list">
          {availableOrgs.map(org => (
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
        </div>
      </div>
    </div>
  );
}
