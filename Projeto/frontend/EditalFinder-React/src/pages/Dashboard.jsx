import { useState, useEffect, useCallback } from 'react';
import Header from '../components/layout/Header';
import EditalCard from '../components/dashboard/EditalCard';
import { dataService } from '../services/dataService';
import Filters from '../components/dashboard/Filters';
import { formatCurrency, formatDate } from '../utils/formatters';

export default function Dashboard() {
  const [allEditais, setAllEditais] = useState([]);
  const [filteredEditais, setFilteredEditais] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalSearch, setGlobalSearch] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await dataService.getEditais();
        setAllEditais(data);
        setFilteredEditais(data);
      } catch (error) {
        console.error('Erro ao carregar editais:', error);
        alert('Não foi possível carregar os editais.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleFilterChange = useCallback((filters) => {
    let result = [...allEditais];

    // Filtro de estado
    if (filters.state) {
      result = result.filter(e => e.estado === filters.state);
    }

    // Filtro de localidade
    if (filters.nacional || filters.internacional) {
      result = result.filter(e => 
        (filters.nacional && e.localidade === 'Nacional') || 
        (filters.internacional && e.localidade === 'Internacional')
      );
    }

    // Filtro de palavras-chave
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      result = result.filter(e => 
        e.titulo.toLowerCase().includes(kw) || 
        e.area.toLowerCase().includes(kw) ||
        e.orgao.toLowerCase().includes(kw)
      );
    }

    // Filtro de tipo de recurso
    if (filters.resourceType) {
      result = result.filter(e => e.tipoRecurso === filters.resourceType);
    }

    // Filtro de crédito
    if (filters.creditMax) {
      result = result.filter(e => e.valor <= filters.creditMax);
    }

    // Filtro de datas
    if (filters.startDate || filters.endDate) {
      result = result.filter(e => {
        if (!e.dataLimite) return false;
        const editalDate = new Date(e.dataLimite);
        if (filters.startDate && new Date(filters.startDate) > editalDate) return false;
        if (filters.endDate && new Date(filters.endDate) < editalDate) return false;
        return true;
      });
    }

    // Filtro de área
    if (filters.area) {
      result = result.filter(e => e.area === filters.area);
    }

    // Filtro de órgão
    const activeOrgs = Object.entries(filters.orgs)
      .filter(([_, active]) => active)
      .map(([name]) => name.toUpperCase());

    if (activeOrgs.length > 0) {
      result = result.filter(e => {
        const orgaoUpper = e.orgao.toUpperCase();
        return activeOrgs.some(org => orgaoUpper.includes(org));
      });
    }

    // Filtro global
    if (globalSearch) {
      const gs = globalSearch.toLowerCase();
      result = result.filter(e => 
        e.titulo.toLowerCase().includes(gs) ||
        e.orgao.toLowerCase().includes(gs) ||
        e.area.toLowerCase().includes(gs)
      );
    }

    setFilteredEditais(result);
  }, [allEditais, globalSearch]);

  const handleExportCSV = () => {
    if (filteredEditais.length === 0) {
      alert('Nenhum edital para exportar.');
      return;
    }

    let csv = 'Título,Órgão,Área,Valor,Localidade,Data Limite,Tipo de Recurso\n';
    filteredEditais.forEach(e => {
      csv += `"${e.titulo}","${e.orgao}","${e.area}","${formatCurrency(e.valor)}","${e.localidade}","${e.dataLimite ? formatDate(e.dataLimite) : 'N/A'}","${e.tipoRecurso}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `editais_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <Header onSearch={setGlobalSearch} />
      <div className="dashboard-container">
        <Filters onFilterChange={handleFilterChange} />
        <main className="main-content">
          <div className="content-header">
            <h2>Editais Disponíveis</h2>
            <div className="content-actions">
              <span className="editals-count">Mostrando {filteredEditais.length} editais</span>
              <button onClick={handleExportCSV} className="btn-export">📥 Exportar CSV</button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '50px' }}>
              <h3>Carregando editais...</h3>
            </div>
          ) : (
            <div className="editais-grid">
              {filteredEditais.map(edital => (
                <EditalCard key={edital.id} edital={edital} />
              ))}
              {filteredEditais.length === 0 && (
                <div className="empty-state">
                  <h3>Nenhum edital encontrado</h3>
                  <p>Tente ajustar seus filtros para encontrar mais oportunidades.</p>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </>
  );
}

