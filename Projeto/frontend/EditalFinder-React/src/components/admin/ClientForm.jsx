import { useState, useEffect } from 'react';
import { formatCurrency } from '../../utils/formatters';

export default function ClientForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    nome_empresa: '',
    razao_social: '',
    cnpj: '',
    data_abertura: '',
    natureza_juridica: '',
    porte_empresa: 'MEI',
    setor: '',
    cnae_principal: '',
    pais: 'Brasil',
    estado: '',
    cidade: '',
    regiao: '',
    faturamento_anual: 0,
    numero_funcionarios: 0,
    capital_social: 0,
    area_inovacao: '',
    tem_projeto_inovacao: false,
    descricao_projeto: '',
    nivel_maturidade: 'Ideação',
    possui_certidao_negativa: false,
    regular_fiscal: false,
    regular_trabalhista: false,
    interesse_temas: '',
    interesse_valor_min: 0,
    interesse_valor_max: 0,
    disponibilidade_contrapartida: false,
    status: 'Ativo',
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' || type === 'range' ? parseFloat(value) : value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-grid">
        <div className="form-section-title">Informações Básicas</div>
        <div className="form-group">
          <label>Nome da Empresa</label>
          <input type="text" name="nome_empresa" value={formData.nome_empresa} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Razão Social</label>
          <input type="text" name="razao_social" value={formData.razao_social} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>CNPJ</label>
          <input type="text" name="cnpj" value={formData.cnpj} onChange={handleChange} placeholder="00.000.000/0000-00" required />
        </div>
        <div className="form-group">
          <label>Data de Abertura</label>
          <input type="date" name="data_abertura" value={formData.data_abertura} onChange={handleChange} />
        </div>

        <div className="form-section-title">Classificação e Localização</div>
        <div className="form-group">
          <label>Natureza Jurídica</label>
          <input type="text" name="natureza_juridica" value={formData.natureza_juridica} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Porte da Empresa</label>
          <select name="porte_empresa" value={formData.porte_empresa} onChange={handleChange}>
            <option value="MEI">MEI</option>
            <option value="ME">ME</option>
            <option value="EPP">EPP</option>
            <option value="Média">Média</option>
            <option value="Grande">Grande</option>
          </select>
        </div>
        <div className="form-group">
          <label>Setor</label>
          <input type="text" name="setor" value={formData.setor} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>CNAE Principal</label>
          <input type="text" name="cnae_principal" value={formData.cnae_principal} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>País</label>
          <input type="text" name="pais" value={formData.pais} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Estado (UF)</label>
          <input type="text" name="estado" value={formData.estado} onChange={handleChange} maxLength="2" />
        </div>
        <div className="form-group">
          <label>Cidade</label>
          <input type="text" name="cidade" value={formData.cidade} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Região</label>
          <input type="text" name="regiao" value={formData.regiao} onChange={handleChange} />
        </div>

        <div className="form-section-title">Dados Financeiros e Inovação</div>
        <div className="form-group">
          <label>Faturamento Anual: <span>{formatCurrency(formData.faturamento_anual)}</span></label>
          <input type="range" name="faturamento_anual" min="0" max="100000000" step="1000" value={formData.faturamento_anual} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Nº de Funcionários</label>
          <input type="number" name="numero_funcionarios" value={formData.numero_funcionarios} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Capital Social: <span>{formatCurrency(formData.capital_social)}</span></label>
          <input type="range" name="capital_social" min="0" max="100000000" step="1000" value={formData.capital_social} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Área de Inovação</label>
          <input type="text" name="area_inovacao" value={formData.area_inovacao} onChange={handleChange} />
        </div>
        <div className="form-group checkbox-row">
          <input type="checkbox" name="tem_projeto_inovacao" checked={formData.tem_projeto_inovacao} onChange={handleChange} />
          <label>Tem projeto de inovação?</label>
        </div>
        <div className="form-group full-width">
          <label>Descrição do Projeto</label>
          <textarea name="descricao_projeto" rows="3" value={formData.descricao_projeto} onChange={handleChange}></textarea>
        </div>
        <div className="form-group">
          <label>Nível de Maturidade</label>
          <select name="nivel_maturidade" value={formData.nivel_maturidade} onChange={handleChange}>
            <option value="Ideação">Ideação</option>
            <option value="Validação">Validação</option>
            <option value="Operação">Operação</option>
            <option value="Escala">Escala</option>
          </select>
        </div>

        <div className="form-section-title">Regularidade e Interesses</div>
        <div className="form-group checkbox-row">
          <input type="checkbox" name="possui_certidao_negativa" checked={formData.possui_certidao_negativa} onChange={handleChange} />
          <label>Certidão Negativa</label>
        </div>
        <div className="form-group checkbox-row">
          <input type="checkbox" name="regular_fiscal" checked={formData.regular_fiscal} onChange={handleChange} />
          <label>Regular Fiscal</label>
        </div>
        <div className="form-group checkbox-row">
          <input type="checkbox" name="regular_trabalhista" checked={formData.regular_trabalhista} onChange={handleChange} />
          <label>Regular Trabalhista</label>
        </div>
        <div className="form-group checkbox-row">
          <input type="checkbox" name="disponibilidade_contrapartida" checked={formData.disponibilidade_contrapartida} onChange={handleChange} />
          <label>Disponibilidade de Contrapartida</label>
        </div>
        <div className="form-group full-width">
          <label>Temas de Interesse</label>
          <input type="text" name="interesse_temas" value={formData.interesse_temas} onChange={handleChange} placeholder="Ex: Sustentabilidade, IA, Agro" />
        </div>
        <div className="form-group">
          <label>Valor Mínimo Interesse: <span>{formatCurrency(formData.interesse_valor_min)}</span></label>
          <input type="range" name="interesse_valor_min" min="0" max="10000000" step="5000" value={formData.interesse_valor_min} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Valor Máximo Interesse: <span>{formatCurrency(formData.interesse_valor_max)}</span></label>
          <input type="range" name="interesse_valor_max" min="0" max="10000000" step="5000" value={formData.interesse_valor_max} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Status</label>
          <select name="status" value={formData.status} onChange={handleChange} required>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="btn-save">Salvar Cliente</button>
      </div>
    </form>
  );
}
