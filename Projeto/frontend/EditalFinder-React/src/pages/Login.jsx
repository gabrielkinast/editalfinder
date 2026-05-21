import { useState, useCallback, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateSignupFields({ nome, email, senha, senhaConfirm }) {
  const nomeTrim = String(nome ?? '').trim();
  if (!nomeTrim) return 'Informe seu nome.';
  const emailTrim = String(email ?? '').trim();
  if (!emailTrim) return 'Informe um e-mail válido.';
  if (!EMAIL_RE.test(emailTrim.toLowerCase())) return 'Informe um e-mail válido.';
  if (!senha || String(senha).length < 6) return 'A senha deve ter pelo menos 6 caracteres.';
  if (String(senha) !== String(senhaConfirm ?? '')) return 'As senhas não conferem.';
  return null;
}

export default function Login() {
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [signupNome, setSignupNome] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupPassword2, setSignupPassword2] = useState('');
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [formInfo, setFormInfo] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();

  useEffect(() => {
    if (!location.state?.emailConfirmed) return;
    setFormInfo('E-mail confirmado. Entre com sua conta.');
    setMode('signin');
    window.history.replaceState({}, document.title, location.pathname);
  }, [location.state?.emailConfirmed, location.pathname]);
  const { settings } = useSettings();

  const switchMode = useCallback((next) => {
    setMode(next);
    setFormError('');
    if (next !== 'signin') setFormInfo('');
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setFormError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error) {
      setFormError(error?.message || 'Não foi possível entrar.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormInfo('');
    const localErr = validateSignupFields({
      nome: signupNome,
      email: signupEmail,
      senha: signupPassword,
      senhaConfirm: signupPassword2,
    });
    if (localErr) {
      setFormError(localErr);
      return;
    }
    setLoading(true);
    try {
      const result = await register({
        nome: signupNome.trim(),
        email: signupEmail.trim(),
        senha: signupPassword,
      });
      if (result?.status === 'pending_email_confirmation') {
        setFormInfo(result.message);
        setSignupNome('');
        setSignupEmail('');
        setSignupPassword('');
        setSignupPassword2('');
        switchMode('signin');
        return;
      }
      if (result?.status === 'complete') {
        navigate('/dashboard');
        return;
      }
      setFormError('Resposta inesperada ao criar conta. Tente entrar ou contacte o suporte.');
    } catch (error) {
      setFormError(error?.message || 'Não foi possível criar a conta.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          {settings.logoImage ? (
            <>
              <img className="login-logo-img" src={settings.logoImage} alt="Logo" />
              <h1 className="logo logo--with-image">EditalFinder</h1>
            </>
          ) : (
            <h1 className="logo">{settings.logoText}</h1>
          )}
          <p className="tagline">Encontre oportunidades de financiamento e inovação</p>
        </div>

        <div className="login-mode-tabs" role="tablist" aria-label="Modo de acesso">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'signin'}
            className={`login-mode-tab ${mode === 'signin' ? 'active' : ''}`}
            onClick={() => switchMode('signin')}
          >
            Entrar
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'signup'}
            className={`login-mode-tab ${mode === 'signup' ? 'active' : ''}`}
            onClick={() => switchMode('signup')}
          >
            Criar conta
          </button>
        </div>

        {formInfo ? (
          <div className="login-alert login-alert--info" role="status">
            {formInfo}
          </div>
        ) : null}

        {formError ? (
          <div className="login-alert login-alert--error" role="alert">
            {formError}
          </div>
        ) : null}

        {mode === 'signin' ? (
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="email">E-mail</label>
              <input
                type="email"
                id="email"
                name="email"
                placeholder="seu@email.com"
                autoComplete="username"
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
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className="btn-login" disabled={loading}>
              {loading ? 'Verificando…' : 'Entrar'}
            </button>

            <p className="login-switch-hint">
              Novo no EditalFinder?{' '}
              <button type="button" className="login-text-link" onClick={() => switchMode('signup')}>
                Criar conta
              </button>
            </p>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="login-form">
            <div className="form-group">
              <label htmlFor="signup-nome">Nome</label>
              <input
                type="text"
                id="signup-nome"
                name="signup-nome"
                placeholder="Seu nome completo"
                autoComplete="name"
                value={signupNome}
                onChange={(e) => setSignupNome(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="signup-email">E-mail</label>
              <input
                type="email"
                id="signup-email"
                name="signup-email"
                placeholder="seu@email.com"
                autoComplete="email"
                value={signupEmail}
                onChange={(e) => setSignupEmail(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="signup-password">Senha</label>
              <input
                type="password"
                id="signup-password"
                name="signup-password"
                placeholder="Mínimo 6 caracteres"
                autoComplete="new-password"
                value={signupPassword}
                onChange={(e) => setSignupPassword(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="signup-password2">Confirmar senha</label>
              <input
                type="password"
                id="signup-password2"
                name="signup-password2"
                placeholder="Repita a senha"
                autoComplete="new-password"
                value={signupPassword2}
                onChange={(e) => setSignupPassword2(e.target.value)}
              />
            </div>

            <button type="submit" className="btn-login" disabled={loading}>
              {loading ? 'Criando conta…' : 'Criar conta'}
            </button>

            <button
              type="button"
              className="btn-login btn-login--secondary"
              disabled={loading}
              onClick={() => switchMode('signin')}
            >
              Voltar para login
            </button>

            <p className="login-switch-hint">
              Já tem conta?{' '}
              <button type="button" className="login-text-link" onClick={() => switchMode('signin')}>
                Entrar
              </button>
            </p>
          </form>
        )}

        {mode === 'signin' && import.meta.env.DEV ? (
          <div className="login-footer">
            <p className="credentials-hint">
              <strong>Demo (apenas DEV):</strong> admin@finder.com / 123456
            </p>
          </div>
        ) : null}
      </div>

      <div className="login-background" aria-hidden />
    </div>
  );
}
