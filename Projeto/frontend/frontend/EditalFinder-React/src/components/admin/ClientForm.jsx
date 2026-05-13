import { useState, useEffect } from 'react';

const defaultState = {
  nome_empresa: '',
  razao_social: '',
  cnpj: '',
  setor: '',
  porte_empresa: 'MEI',
  status: 'Ativo',
  interesse_temas: '',
  interesse_valor_min: 0,
  interesse_valor_max: 0,
};

export default function ClientForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState(defaultState);

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...defaultState,
        ...initialData,
        interesse_valor_min: initialData.interesse_valor_min ?? 0,
        interesse_valor_max: initialData.interesse_valor_max ?? 0,
      });
    } else {
      setFormData(defaultState);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: value === '' ? 0 : Number(value) }));
      return;
    }
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-group">
        <label htmlFor="nome_empresa">Nome da empresa</label>
        <input
          type="text"
          id="nome_empresa"
          name="nome_empresa"
          value={formData.nome_empresa}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="razao_social">Razão social</label>
        <input
          type="text"
          id="razao_social"
          name="razao_social"
          value={formData.razao_social || ''}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="cnpj">CNPJ</label>
        <input type="text" id="cnpj" name="cnpj" value={formData.cnpj} onChange={handleChange} />
      </div>
      <div className="form-group">
        <label htmlFor="setor">Setor</label>
        <input type="text" id="setor" name="setor" value={formData.setor} onChange={handleChange} />
      </div>
      <div className="form-group">
        <label htmlFor="porte_empresa">Porte</label>
        <select id="porte_empresa" name="porte_empresa" value={formData.porte_empresa} onChange={handleChange}>
          <option value="MEI">MEI</option>
          <option value="ME">ME</option>
          <option value="EPP">EPP</option>
          <option value="Média">Média</option>
          <option value="Grande">Grande</option>
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="status">Status</label>
        <select id="status" name="status" value={formData.status} onChange={handleChange}>
          <option value="Ativo">Ativo</option>
          <option value="Inativo">Inativo</option>
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="interesse_temas">Temas de interesse</label>
        <input
          type="text"
          id="interesse_temas"
          name="interesse_temas"
          value={formData.interesse_temas || ''}
          onChange={handleChange}
          placeholder="Ex.: IA, Saúde, Agro"
        />
      </div>
      <div className="form-group">
        <label htmlFor="interesse_valor_min">Interesse valor mín.</label>
        <input
          type="number"
          id="interesse_valor_min"
          name="interesse_valor_min"
          min={0}
          value={formData.interesse_valor_min}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="interesse_valor_max">Interesse valor máx.</label>
        <input
          type="number"
          id="interesse_valor_max"
          name="interesse_valor_max"
          min={0}
          value={formData.interesse_valor_max}
          onChange={handleChange}
        />
      </div>
      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="btn-save">
          Salvar
        </button>
      </div>
    </form>
  );
}
