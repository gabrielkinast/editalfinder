import { useState, useEffect, useMemo } from 'react';
import { dataService } from '../../services/dataService';

const PERFIS = ['Startup', 'ONG', 'Universidade', 'Empresa Industrial', 'Pesquisador', 'MEI', 'Cooperativa', 'Escola', 'Hospital', 'Governo'];
const REGIOES = ['Nacional', 'Sul', 'Sudeste', 'Nordeste', 'Centro-Oeste', 'Norte'];
const COMPAT_THRESHOLD = 70;

export default function Filters({ onFilterChange, allEditais = [] }) {
  const [filters, setFilters] = useState({
    resourceType: '',
    areas: {},
    orgs: {},
    perfil: '',
    regiao: '',
    valorMin: '',
    valorMax: '',
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

  // Tipos de recurso fixos
  const availableResourceTypes = ['Linha de crédito', 'Subvenção econômica'];

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

  // Atualiza o estado das áreas quando novas áreas são descobertas
  useEffect(() => {
    setFilters(prev => {
      const newAreasState = { ...prev.areas };
      let changed = false;

      availableAreas.forEach(area => {
        const key = area.toLowerCase();
        if (newAreasState[key] === undefined) {
          newAreasState[key] = false;
          changed = true;
        }
      });

      if (changed) {
        return { ...prev, areas: newAreasState };
      }
      return prev;
    });
  }, [availableAreas]);

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
      } else if (id.startsWith('area-')) {
        const areaKey = id.replace('area-', '');
        setFilters(prev => ({
          ...prev,
          areas: { ...prev.areas, [areaKey]: checked }
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
    Object.keys(filters.orgs).forEach(key => { resetOrgs[key] = false; });

    const resetAreas = {};
    Object.keys(filters.areas).forEach(key => { resetAreas[key] = false; });

    setFilters({
      resourceType: '',
      areas: resetAreas,
      orgs: resetOrgs,
      perfil: '',
      regiao: '',
      valorMin: '',
      valorMax: '',
    });
  };

  const togglePerfil = (perfil) => {
    setFilters(prev => ({ ...prev, perfil: prev.perfil === perfil ? '' : perfil }));
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

      {/* Região */}
      <div className="filter-group">
        <h3 className="filter-label">Região</h3>
        <select
          id="regiaoFilter"
          className="filter-select"
          value={filters.regiao}
          onChange={handleChange}
        >
          <option value="">Todas as regiões</option>
          {REGIOES.map(r => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </div>

      {/* Faixa de Valor */}
      <div className="filter-group">
        <h3 className="filter-label">Faixa de Valor (R$)</h3>
        <div className="valor-range">
          <input
            type="number"
            id="valorMinFilter"
            className="filter-input-valor"
            placeholder="Mínimo"
            value={filters.valorMin}
            onChange={handleChange}
            min="0"
          />
          <span className="valor-range-sep">até</span>
          <input
            type="number"
            id="valorMaxFilter"
            className="filter-input-valor"
            placeholder="Máximo"
            value={filters.valorMax}
            onChange={handleChange}
            min="0"
          />
        </div>
      </div>

      {/* Área */}
      <div className="filter-group">
        <h3 className="filter-label">Área</h3>
        <div className="checkbox-list">
          {availableAreas.map(area => (
            <label key={area} className="checkbox-label">
              <input
                type="checkbox"
                id={`area-${area.toLowerCase()}`}
                checked={filters.areas[area.toLowerCase()] || false}
                onChange={handleChange}
              />
              <span>{area}</span>
            </label>
          ))}
        </div>
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
