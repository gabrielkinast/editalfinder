import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  completeEmailAuthCallback,
  EMAIL_CONFIRMED_SUCCESS_HINT,
  EMAIL_CONFIRMED_SUCCESS_MESSAGE,
  resetLocalAuthAfterCallbackFailure,
  stripAuthParamsFromUrl,
} from '../services/authCallbackService';
import { markAuthCallbackHandling } from '../auth/authCallbackCoordinator';
import { authCallbackLog } from '../utils/authCallbackDevLog';

/**
 * Página pública de confirmação de e-mail (/auth/callback).
 * Não redireciona automaticamente ao dashboard — orienta o utilizador ao login.
 */
export default function AuthCallback() {
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('Confirmando…');
  const [hint, setHint] = useState('');
  const ranRef = useRef(false);

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;

    markAuthCallbackHandling(true);

    (async () => {
      try {
        const result = await completeEmailAuthCallback(window.location.href);

        if (result.status === 'success') {
          setStatus('success');
          setMessage(result.message || EMAIL_CONFIRMED_SUCCESS_MESSAGE);
          setHint(result.hint || EMAIL_CONFIRMED_SUCCESS_HINT);
          authCallbackLog('redirect_to_login_clicked', { auto: false, phase: 'success_shown' });
          return;
        }

        if (result.status === 'expired') {
          setStatus('expired');
          setMessage(result.message);
          setHint('');
          return;
        }

        if (result.status === 'timeout') {
          setStatus('manual_login');
          setMessage(result.message);
          setHint('Use o mesmo e-mail e senha que você cadastrou.');
          return;
        }

        setStatus('manual_login');
        setMessage(result.message);
        setHint('Use o mesmo e-mail e senha que você cadastrou.');
      } catch {
        await resetLocalAuthAfterCallbackFailure();
        stripAuthParamsFromUrl();
        setStatus('manual_login');
        setMessage('Não foi possível confirmar automaticamente, mas você pode tentar fazer login.');
        setHint('Se o e-mail já foi confirmado, entre com sua conta.');
        authCallbackLog('manual_login', { reason: 'unexpected_error' });
      } finally {
        markAuthCallbackHandling(false);
      }
    })();

    return () => {
      markAuthCallbackHandling(false);
    };
  }, []);

  const loginState = { emailConfirmed: true };

  return (
    <div className="login-container">
      <div className="login-card auth-callback-card">
        <div className="login-header">
          <h1 className="logo">EditalFinder</h1>
          <p className="tagline">Confirmação de e-mail</p>
        </div>

        {status === 'loading' && (
          <div className="auth-callback-body" role="status" aria-live="polite">
            <div className="auth-callback-spinner" aria-hidden />
            <p className="auth-callback-text">{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="auth-callback-result" role="status">
            <div className="login-alert login-alert--success auth-callback-alert-success">
              <strong>{message}</strong>
            </div>
            {hint ? <p className="auth-callback-hint">{hint}</p> : null}
            <Link
              to="/login"
              className="btn-login auth-callback-primary"
              state={loginState}
              onClick={() => authCallbackLog('redirect_to_login_clicked', { from: 'success' })}
            >
              Ir para login
            </Link>
          </div>
        )}

        {(status === 'manual_login' || status === 'expired') && (
          <div className="auth-callback-result" role={status === 'expired' ? 'alert' : 'status'}>
            <div
              className={`login-alert ${
                status === 'expired' ? 'login-alert--warn' : 'login-alert--info'
              }`}
            >
              {message}
            </div>
            {hint ? <p className="auth-callback-hint">{hint}</p> : null}
            <div className="auth-callback-actions">
              <Link
                to="/login"
                className="btn-login auth-callback-primary"
                state={status === 'manual_login' ? loginState : undefined}
                onClick={() =>
                  authCallbackLog('redirect_to_login_clicked', { from: status })
                }
              >
                Ir para login
              </Link>
              <Link
                to="/login"
                className="auth-callback-link-secondary"
                onClick={() => authCallbackLog('redirect_to_login_clicked', { from: 'home_link' })}
              >
                Voltar para início
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
