import { useState, useEffect, useCallback } from 'react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
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
  const [showFiltersMobile, setShowFiltersMobile] = useState(false);

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

    const stateMap = {
      'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
      'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
      'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
      'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
      'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
      'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
      'SE': 'Sergipe', 'TO': 'Tocantins'
    };

    // Filtro de estado
    if (filters.state) {
      result = result.filter(e => {
        const editalState = e.estado || '';
        const editalStateFull = stateMap[editalState.toUpperCase()] || editalState;
        
        const stateMatch = editalStateFull === filters.state || editalState.toUpperCase() === filters.state.toUpperCase();
        
        // Se o filtro for Rio Grande do Sul, também mostra editais da FAPERGS
        if (filters.state === 'Rio Grande do Sul') {
          return stateMatch || e.orgao.toUpperCase().includes('FAPERGS');
        }
        return stateMatch;
      });
    }

    // Filtro de localidade (Nacional / Internacional)
    if (filters.nacional || filters.internacional) {
      result = result.filter(e => {
        const locality = (e.localidade || '').toLowerCase();
        const state = (e.estado || '').toLowerCase();
        
        // Internacional: Se a localidade for internacional OR o estado for internacional OR o estado for 'Exterior'
        const isActuallyInternacional = locality === 'internacional' || state === 'internacional' || state === 'exterior' || state === 'ex';

        // Nacional: Se não for internacional, e tiver localidade nacional ou um estado brasileiro preenchido
        const isActuallyNacional = !isActuallyInternacional && (locality === 'nacional' || state !== '');
        
        const matchesNacional = filters.nacional && isActuallyNacional;
        const matchesInternacional = filters.internacional && isActuallyInternacional;
        
        return matchesNacional || matchesInternacional;
      });
    }

    // Filtro de palavras-chave
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      result = result.filter(e => 
        (e.titulo || '').toLowerCase().includes(kw) || 
        (e.area || '').toLowerCase().includes(kw) ||
        (e.orgao || '').toLowerCase().includes(kw)
      );
    }

    // Filtro de tipo de recurso
    if (filters.resourceType) {
      const typeFilter = filters.resourceType.toLowerCase();
      result = result.filter(e => (e.tipoRecurso || '').toLowerCase() === typeFilter);
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
      const areaFilter = filters.area.toLowerCase();
      result = result.filter(e => {
        // Verifica se a área está explicitamente listada no campo de área
        const editalAreas = (e.area || '').split(/[,;]/).map(a => a.trim().toLowerCase());
        const hasDirectArea = editalAreas.includes(areaFilter);
        
        // Verifica se o termo da área está presente no título (sincronizando com a busca por texto)
        const hasInTitle = (e.titulo || '').toLowerCase().includes(areaFilter);
        
        return hasDirectArea || hasInTitle;
      });
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

  const handleExportPDF = () => {
    try {
      console.log('Iniciando exportação PDF...');
      if (filteredEditais.length === 0) {
        alert('Nenhum edital para exportar.');
        return;
      }

      const doc = new jsPDF('l', 'mm', 'a4');
      
      doc.setFontSize(18);
      doc.text('Relatório de Editais Encontrados', 14, 20);
      doc.setFontSize(11);
      doc.text(`Data de geração: ${new Date().toLocaleDateString('pt-BR')}`, 14, 30);
      doc.text(`Total de editais: ${filteredEditais.length}`, 14, 36);

      const tableColumn = ["Nome do Edital", "Órgão Financiador", "Área", "Valor", "Estado", "Tipo", "Limite"];
      const tableRows = [];

      filteredEditais.forEach(e => {
        tableRows.push([
          e.titulo,
          e.orgao,
          e.area,
          formatCurrency(e.valor),
          e.estado || 'Nacional',
          e.tipoRecurso,
          e.dataLimite ? formatDate(e.dataLimite) : 'N/A'
        ]);
      });

      autoTable(doc, {
        head: [tableColumn],
        body: tableRows,
        startY: 45,
        styles: { fontSize: 8, cellPadding: 2 },
        headStyles: { fillColor: [74, 108, 247], textColor: [255, 255, 255] },
        columnStyles: {
          0: { cellWidth: 70 },
          1: { cellWidth: 40 },
          2: { cellWidth: 35 },
          3: { cellWidth: 30 },
          4: { cellWidth: 25 },
          5: { cellWidth: 35 },
          6: { cellWidth: 25 },
        }
      });

      console.log('Salvando PDF...');
      doc.save(`editais_encontrados_${new Date().toISOString().split('T')[0]}.pdf`);
      console.log('PDF salvo com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      alert('Erro ao gerar PDF. Verifique o console para mais detalhes.');
    }
  };

  const handleExportExcel = () => {
    try {
      if (filteredEditais.length === 0) {
        alert('Nenhum edital para exportar.');
        return;
      }

      // Preparar os dados para a planilha
      const data = filteredEditais.map(e => ({
        "Nome do Edital": e.titulo,
        "Órgão Financiador": e.orgao,
        "Área": e.area,
        "Valor": formatCurrency(e.valor),
        "Estado": e.estado || 'Nacional',
        "Tipo": e.tipoRecurso,
        "Limite": e.dataLimite ? formatDate(e.dataLimite) : 'N/A'
      }));

      // Criar a planilha
      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Editais");

      // Ajustar a largura das colunas automaticamente
      const wscols = [
        { wch: 50 }, // Nome
        { wch: 25 }, // Órgão
        { wch: 20 }, // Área
        { wch: 15 }, // Valor
        { wch: 15 }, // Estado
        { wch: 20 }, // Tipo
        { wch: 12 }, // Limite
      ];
      worksheet['!cols'] = wscols;

      // Gerar o arquivo Excel e disparar o download
      XLSX.writeFile(workbook, `editais_encontrados_${new Date().toISOString().split('T')[0]}.xlsx`);
    } catch (error) {
      console.error('Erro ao gerar Excel:', error);
      alert('Erro ao gerar planilha. Verifique o console para mais detalhes.');
    }
  };

  return (
    <>
      <Header onSearch={setGlobalSearch} />
      <div className="dashboard-container">
        <button 
          className="filter-toggle-mobile" 
          onClick={() => setShowFiltersMobile(!showFiltersMobile)}
        >
          {showFiltersMobile ? '✕ Fechar Filtros' : '🔍 Abrir Filtros'}
        </button>
        
        <div className={`sidebar ${!showFiltersMobile ? 'mobile-hidden' : ''}`}>
          <Filters onFilterChange={handleFilterChange} allEditais={allEditais} />
        </div>
        
        <main className="main-content">
          <div className="content-header">
            <h2>Editais Disponíveis</h2>
            <div className="content-actions" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span className="editals-count">Mostrando {filteredEditais.length} editais</span>
              <button onClick={handleExportPDF} className="btn-export">📄 PDF</button>
              <button onClick={handleExportExcel} className="btn-export" style={{ backgroundColor: '#27ae60' }}>📊 Planilha</button>
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

