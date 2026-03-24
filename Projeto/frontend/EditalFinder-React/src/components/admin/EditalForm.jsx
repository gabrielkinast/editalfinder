import { useState, useEffect } from 'react';
import { formatCurrency } from '../../utils/formatters';
import { dataService } from '../../services/dataService';

export default function EditalForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    titulo: '',
    descricao: '',
    objetivo: '',
    temas: '',
    publico_alvo: '',
    fonte_recurso: '',
    valor_maximo: 0,
    data_publicacao: '',
    prazo_envio: '',
    situacao: 'Aberto',
    pdf_url: '',
    link: '',
    status: 'Ativo',
    id_organizacao: '',
    estado: '',
  });

  const [orgs, setOrgs] = useState([]);

  const estados = [
    { uf: 'AC', nome: 'Acre' },
    { uf: 'AL', nome: 'Alagoas' },
    { uf: 'AP', nome: 'Amapá' },
    { uf: 'AM', nome: 'Amazonas' },
    { uf: 'BA', nome: 'Bahia' },
    { uf: 'CE', nome: 'Ceará' },
    { uf: 'DF', nome: 'Distrito Federal' },
    { uf: 'ES', nome: 'Espírito Santo' },
    { uf: 'GO', nome: 'Goiás' },
    { uf: 'MA', nome: 'Maranhão' },
    { uf: 'MT', nome: 'Mato Grosso' },
    { uf: 'MS', nome: 'Mato Grosso do Sul' },
    { uf: 'MG', nome: 'Minas Gerais' },
    { uf: 'PA', nome: 'Pará' },
    { uf: 'PB', nome: 'Paraíba' },
    { uf: 'PR', nome: 'Paraná' },
    { uf: 'PE', nome: 'Pernambuco' },
    { uf: 'PI', nome: 'Piauí' },
    { uf: 'RJ', nome: 'Rio de Janeiro' },
    { uf: 'RN', nome: 'Rio Grande do Norte' },
    { uf: 'RS', nome: 'Rio Grande do Sul' },
    { uf: 'RO', nome: 'Rondônia' },
    { uf: 'RR', nome: 'Roraima' },
    { uf: 'SC', nome: 'Santa Catarina' },
    { uf: 'SP', nome: 'São Paulo' },
    { uf: 'SE', nome: 'Sergipe' },
    { uf: 'TO', nome: 'Tocantins' },
    { uf: 'EX', nome: 'Exterior' }
  ];

  useEffect(() => {
    dataService.getOrganizations().then(setOrgs);
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' || type === 'range' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Removemos o campo 'organizacao' que vem do Supabase via relacionamento,
    // pois ele causa erro ao tentar salvar (o Supabase espera apenas colunas reais da tabela).
    const { organizacao, ...dataToSave } = formData;
    
    onSave(dataToSave);
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-grid">
        <div className="form-section-title">Informações Principais</div>
        <div className="form-group full-width">
          <label>Título do Edital</label>
          <input type="text" name="titulo" value={formData.titulo} onChange={handleChange} required />
        </div>
        <div className="form-group full-width">
          <label>Descrição</label>
          <textarea name="descricao" rows="3" value={formData.descricao} onChange={handleChange}></textarea>
        </div>
        <div className="form-group full-width">
          <label>Objetivo</label>
          <textarea name="objetivo" rows="2" value={formData.objetivo} onChange={handleChange}></textarea>
        </div>

        <div className="form-section-title">Detalhes e Classificação</div>
        <div className="form-group">
          <label>Temas</label>
          <input type="text" name="temas" value={formData.temas} onChange={handleChange} placeholder="Ex: IA, Saúde, Sustentabilidade" />
        </div>
        <div className="form-group">
          <label>Público Alvo</label>
          <input type="text" name="publico_alvo" value={formData.publico_alvo} onChange={handleChange} placeholder="Ex: Startups, MEI, Indústrias" />
        </div>
        <div className="form-group">
          <label>Fonte de Recurso</label>
          <input type="text" name="fonte_recurso" value={formData.fonte_recurso} onChange={handleChange} placeholder="Ex: FINEP, BNDES, FAPESP" />
        </div>
        <div className="form-group">
          <label>Valor Máximo: <span>{formatCurrency(formData.valor_maximo)}</span></label>
          <input type="range" name="valor_maximo" min="0" max="50000000" step="100000" value={formData.valor_maximo} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Organização Responsável</label>
          <select name="id_organizacao" value={formData.id_organizacao} onChange={handleChange} required>
            <option value="">Selecione uma organização...</option>
            {orgs.map(org => (
              <option key={org.id_organizacao} value={org.id_organizacao}>{org.nome}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Estado (UF)</label>
          <select name="estado" value={formData.estado} onChange={handleChange}>
            <option value="">Selecione o estado...</option>
            {estados.map(est => (
              <option key={est.uf} value={est.nome}>{est.nome}</option>
            ))}
          </select>
        </div>

        <div className="form-section-title">Datas e Links</div>
        <div className="form-group">
          <label>Data de Publicação</label>
          <input type="date" name="data_publicacao" value={formData.data_publicacao} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Prazo de Envio</label>
          <input type="date" name="prazo_envio" value={formData.prazo_envio} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Situação</label>
          <select name="situacao" value={formData.situacao} onChange={handleChange}>
            <option value="Aberto">Aberto</option>
            <option value="Em análise">Em análise</option>
            <option value="Encerrado">Encerrado</option>
            <option value="Suspenso">Suspenso</option>
          </select>
        </div>
        <div className="form-group">
          <label>Status</label>
          <select name="status" value={formData.status} onChange={handleChange} required>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>
        <div className="form-group full-width">
          <label>URL do PDF</label>
          <input type="url" name="pdf_url" value={formData.pdf_url} onChange={handleChange} placeholder="https://exemplo.com/edital.pdf" />
        </div>
        <div className="form-group full-width">
          <label>Link do Edital</label>
          <input type="url" name="link" value={formData.link} onChange={handleChange} placeholder="https://exemplo.com/pagina-edital" />
        </div>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="btn-save">Salvar Edital</button>
      </div>
    </form>
  );
}
