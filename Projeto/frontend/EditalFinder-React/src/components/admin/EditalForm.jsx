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
  });

  const [orgs, setOrgs] = useState([]);

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
    onSave(formData);
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
