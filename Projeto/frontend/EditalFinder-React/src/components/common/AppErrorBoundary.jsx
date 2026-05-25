import { Component } from 'react';
import { Link } from 'react-router-dom';
import AppReportProblemButton from '../feedback/AppReportProblemButton';
import { buildAppFeedbackPayload } from '../../utils/feedback/buildAppFeedbackPayload';
import { logAppFeedback } from '../../utils/feedback/appFeedbackLog';

export default class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    logAppFeedback('error_boundary_caught', {
      origem: this.props.origem,
      pagina: this.props.pagina,
      message: error?.message?.slice?.(0, 200),
    });
  }

  handleRetry = () => {
    this.setState({ error: null, errorInfo: null });
    this.props.onRetry?.();
  };

  handleClearCache = () => {
    const keys = this.props.clearLocalCacheKeys;
    if (!keys?.length || typeof keys === 'function') {
      this.props.onClearLocalCache?.();
      return;
    }
    const ok = window.confirm(
      'Limpar dados locais desta área? Isso não apaga dados do servidor.',
    );
    if (!ok) return;
    try {
      for (const key of keys) {
        localStorage.removeItem(key);
      }
    } catch {
      /* ignore */
    }
    this.props.onClearLocalCache?.();
    window.location.reload();
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    const {
      origem = 'error_boundary',
      pagina = 'app',
      fallbackTitle = 'Algo deu errado nesta página',
      fallbackMessage = 'Ocorreu um erro ao carregar esta tela. Seus dados no servidor não foram alterados.',
      allowClearLocalCache = false,
    } = this.props;

    const message = this.state.error?.message || 'Erro desconhecido';
    const reportPayload = buildAppFeedbackPayload({
      tipo: 'erro_pagina',
      origem,
      pagina,
      componente: this.props.componente,
      error: this.state.error,
      errorInfo: this.state.errorInfo,
    });

    return (
      <div className="page-wrapper app-error-boundary-page">
        <div className="app-error-boundary-card">
          <h1>{fallbackTitle}</h1>
          <p className="app-feedback-muted">{fallbackMessage}</p>
          {import.meta.env.DEV && (
            <pre className="app-error-boundary-pre">{message}</pre>
          )}
          <div className="app-error-boundary-actions">
            <button type="button" className="btn-primary" onClick={this.handleRetry}>
              Tentar novamente
            </button>
            {allowClearLocalCache && (
              <button type="button" className="btn-secondary" onClick={this.handleClearCache}>
                Limpar cache local
              </button>
            )}
            <AppReportProblemButton
              origem={origem}
              pagina={pagina}
              componente={this.props.componente}
              tipo="erro_pagina"
              error={this.state.error}
              errorInfo={this.state.errorInfo}
              extraContext={{ payload: reportPayload }}
              label="Reportar problema"
              variant="secondary"
            />
            <Link to="/dashboard" className="btn-secondary app-error-boundary-link">
              Voltar ao Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }
}
