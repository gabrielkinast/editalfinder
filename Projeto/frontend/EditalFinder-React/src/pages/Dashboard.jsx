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

    // Filtro de tipo de recurso
    if (filters.resourceType) {
      const typeFilter = filters.resourceType.toLowerCase();
      result = result.filter(e => (e.tipoRecurso || '').toLowerCase() === typeFilter);
    }

    // Filtro de perfil (compatibilidade JSONB > threshold)
    if (filters.perfil) {
      result = result.filter(e => {
        const comp = e.compatibilidade || {};
        const val = parseFloat(comp[filters.perfil] ?? comp[filters.perfil?.toLowerCase()] ?? -1);
        return val >= 70;
      });
    }

    // Filtro de região
    if (filters.regiao) {
      result = result.filter(e => {
        const regiao = (e.regiao || e.localidade || '').toLowerCase();
        return regiao.includes(filters.regiao.toLowerCase());
      });
    }

    // Filtro de faixa de valor — compara com o valor real do edital
    if (filters.valorMin !== '' && filters.valorMin !== undefined) {
      const min = parseFloat(filters.valorMin);
      if (!isNaN(min)) result = result.filter(e => (e.valor || e.valorMaximo || 0) >= min);
    }
    if (filters.valorMax !== '' && filters.valorMax !== undefined) {
      const max = parseFloat(filters.valorMax);
      if (!isNaN(max)) result = result.filter(e => (e.valor || e.valorMaximo || 0) <= max);
    }

    // Filtro de área
    const activeAreas = Object.entries(filters.areas || {})
      .filter(([_, active]) => active)
      .map(([name]) => name.toLowerCase());

    if (activeAreas.length > 0) {
      result = result.filter(e => {
        const editalAreas = (e.area || '').split(/[,;]/).map(a => a.trim().toLowerCase());
        const hasDirectArea = activeAreas.some(a => editalAreas.includes(a));
        const hasInTitle = activeAreas.some(a => (e.titulo || '').toLowerCase().includes(a));
        return hasDirectArea || hasInTitle;
      });
    }

    // Filtro de órgão
    const activeOrgs = Object.entries(filters.orgs || {})
      .filter(([_, active]) => active)
      .map(([name]) => name.toUpperCase());

    if (activeOrgs.length > 0) {
      result = result.filter(e => {
        const orgaoUpper = (e.orgao || '').toUpperCase();
        return activeOrgs.some(org => orgaoUpper.includes(org));
      });
    }

    // Filtro global
    if (globalSearch) {
      const gs = globalSearch.toLowerCase();
      result = result.filter(e => 
        (e.titulo || '').toLowerCase().includes(gs) ||
        (e.orgao || '').toLowerCase().includes(gs) ||
        (e.area || '').toLowerCase().includes(gs)
      );
    }

    // Ordenar por score decrescente
    result.sort((a, b) => (b.score || 0) - (a.score || 0));

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

