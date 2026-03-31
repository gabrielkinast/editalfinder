import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();
  const { settings } = useSettings();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {settings.logoImage ? (
            <>
              <img src={settings.logoImage} alt="Logo" style={{ maxHeight: '100px', width: 'auto', marginBottom: '15px' }} />
              <h1 className="logo" style={{ fontSize: '28px', marginBottom: '0' }}>EditalFinder</h1>
            </>
          ) : (
            <h1 className="logo">{settings.logoText}</h1>
          )}
          <p className="tagline" style={{ marginTop: '8px' }}>Encontre oportunidades de financiamento e inovação</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="seu@email.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? 'Verificando...' : 'Entrar'}
          </button>
        </form>

        <div className="login-footer">
          <p className="credentials-hint">
            <strong>Demo:</strong> admin@finder.com / 123456
          </p>
        </div>
      </div>

      <div className="login-background"></div>
    </div>
  );
}
