import { useState, useEffect } from 'react';

export default function OrgForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    nome: '',
    tipo: '',
    país: 'Brasil',
    estado: '',
    site: '',
    status: 'Ativo',
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-group">
        <label>Nome da Organização</label>
        <input type="text" name="nome" value={formData.nome} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>Tipo (ex: Pública, Privada, ONG)</label>
        <input type="text" name="tipo" value={formData.tipo} onChange={handleChange} />
      </div>
      <div className="form-group">
        <label>País</label>
        <input type="text" name="país" value={formData.país} onChange={handleChange} />
      </div>
      <div className="form-group">
        <label>Estado (UF)</label>
        <input type="text" name="estado" value={formData.estado} onChange={handleChange} maxLength="2" />
      </div>
      <div className="form-group">
        <label>Site Oficial</label>
        <input type="url" name="site" value={formData.site} onChange={handleChange} placeholder="https://exemplo.com" />
      </div>
      <div className="form-group">
        <label>Status</label>
        <select name="status" value={formData.status} onChange={handleChange} required>
          <option value="Ativo">Ativo</option>
          <option value="Inativo">Inativo</option>
        </select>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="btn-save">Salvar Organização</button>
      </div>
    </form>
  );
}
