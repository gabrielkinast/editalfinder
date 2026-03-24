import { useState, useEffect } from 'react';

export default function UserForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    nome: '',
    nome_email: '',
    senha: '',
    tipo_usuario: 'Consultor',
    nivel_acesso: 1,
    status: 'Ativo',
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'tipo_usuario') {
      const niveis = {
        'Administrador': 1,
        'Consultor': 2,
        'Funcionário': 3
      };
      setFormData(prev => ({ 
        ...prev, 
        [name]: value,
        nivel_acesso: niveis[value] || 3
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-group">
        <label htmlFor="nome">Nome Completo</label>
        <input 
          type="text" 
          id="nome" 
          name="nome" 
          value={formData.nome} 
          onChange={handleChange} 
          required 
        />
      </div>
      <div className="form-group">
        <label htmlFor="nome_email">Email</label>
        <input 
          type="email" 
          id="nome_email" 
          name="nome_email" 
          value={formData.nome_email} 
          onChange={handleChange} 
          required 
        />
      </div>
      <div className="form-group">
        <label htmlFor="senha">Senha</label>
        <input 
          type="password" 
          id="senha" 
          name="senha" 
          value={formData.senha} 
          onChange={handleChange} 
          required 
        />
      </div>
      <div className="form-group">
        <label htmlFor="tipo_usuario">Tipo de Usuário</label>
        <select 
          id="tipo_usuario" 
          name="tipo_usuario" 
          value={formData.tipo_usuario} 
          onChange={handleChange} 
          required
        >
          <option value="Administrador">Administrador</option>
          <option value="Consultor">Consultor</option>
          <option value="Funcionário">Funcionário</option>
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="nivel_acesso">Nível de Acesso</label>
        <input 
          type="number" 
          id="nivel_acesso" 
          name="nivel_acesso" 
          value={formData.nivel_acesso} 
          readOnly 
          disabled
        />
        <small>O nível é definido pelo tipo de usuário</small>
      </div>
      <div className="form-group">
        <label htmlFor="status">Status</label>
        <select 
          id="status" 
          name="status" 
          value={formData.status} 
          onChange={handleChange} 
          required
        >
          <option value="Ativo">Ativo</option>
          <option value="Inativo">Inativo</option>
        </select>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="btn-save">Salvar Usuário</button>
      </div>
    </form>
  );
}
