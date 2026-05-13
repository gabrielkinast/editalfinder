import { useState } from 'react';
import { useSettings } from '../../contexts/SettingsContext';
import { usePermissions } from '../../hooks/usePermissions';
import { applyTheme, getSavedThemePreference, saveThemePreference } from '../../config/theme';

export default function SettingsForm({ onCancel }) {
  const { settings, updateSettings } = useSettings();
  const permissions = usePermissions();
  const [formData, setFormData] = useState(settings);
  const [themePref, setThemePref] = useState(() => getSavedThemePreference());

  if (!permissions.canManageUsers) {
    return <p>Você não tem permissão para alterar as configurações.</p>;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({ ...prev, logoImage: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateSettings(formData);
    saveThemePreference(themePref);
    applyTheme(themePref);
    onCancel();
  };

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <div className="form-group">
        <label>Aparência</label>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', gap: '8px', alignItems: 'center', fontWeight: 500, textTransform: 'none', letterSpacing: 0 }}>
            <input
              type="radio"
              name="themePreference"
              value="light"
              checked={themePref === 'light'}
              onChange={(e) => {
                const v = e.target.value;
                setThemePref(v);
                applyTheme(v);
              }}
            />
            Tema claro
          </label>
          <label style={{ display: 'flex', gap: '8px', alignItems: 'center', fontWeight: 500, textTransform: 'none', letterSpacing: 0 }}>
            <input
              type="radio"
              name="themePreference"
              value="dark"
              checked={themePref === 'dark'}
              onChange={(e) => {
                const v = e.target.value;
                setThemePref(v);
                applyTheme(v);
              }}
            />
            Tema escuro
          </label>
          <label style={{ display: 'flex', gap: '8px', alignItems: 'center', fontWeight: 500, textTransform: 'none', letterSpacing: 0 }}>
            <input
              type="radio"
              name="themePreference"
              value="system"
              checked={themePref === 'system'}
              onChange={(e) => {
                const v = e.target.value;
                setThemePref(v);
                applyTheme(v);
              }}
            />
            Usar tema do sistema
          </label>
        </div>
        <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--color-muted)' }}>
          A preferência é salva neste navegador como <code>editalfinder.theme</code>.
        </div>
      </div>

      <div className="form-group">
        <label>Texto da Logo</label>
        <input 
          type="text" 
          name="logoText" 
          value={formData.logoText} 
          onChange={handleChange} 
        />
      </div>
      
      <div className="form-group">
        <label>Imagem da Logo (URL ou Upload)</label>
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleLogoChange} 
          style={{ marginBottom: '10px' }}
        />
        {formData.logoImage && (
          <div style={{ marginBottom: '10px' }}>
            <img src={formData.logoImage} alt="Preview" style={{ maxHeight: '50px' }} />
            <button 
              type="button" 
              onClick={() => setFormData(prev => ({ ...prev, logoImage: null }))}
              style={{ display: 'block', fontSize: '12px', color: 'red', border: 'none', background: 'none', cursor: 'pointer' }}
            >
              Remover Logo
            </button>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Cor Principal (Azul)</label>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input 
            type="color" 
            name="primaryBlue" 
            value={formData.primaryBlue} 
            onChange={handleChange}
            style={{ width: '50px', height: '40px', padding: '2px' }}
          />
          <span>{formData.primaryBlue}</span>
        </div>
      </div>

      <div className="form-group">
        <label>Cor Secundária (Botões/Destaque - Amarelo)</label>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input 
            type="color" 
            name="primaryYellow" 
            value={formData.primaryYellow} 
            onChange={handleChange}
            style={{ width: '50px', height: '40px', padding: '2px' }}
          />
          <span>{formData.primaryYellow}</span>
        </div>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="btn-save">Salvar Configurações</button>
      </div>
    </form>
  );
}
