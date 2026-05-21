import { Component } from 'react';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';

/**
 * Evita derrubar a app inteira quando o painel do Workspace falha no render.
 */
export default class ConsultorWorkspaceErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    logConsultorWorkspace('workspace_error_boundary', {
      message: error?.message || String(error),
      stack: error?.stack || null,
      componentStack: info?.componentStack || null,
    });
    if (import.meta.env?.DEV) {
      console.error('[consultor-workspace] workspace_error_boundary', error, info);
    }
  }

  handleRetry = () => {
    this.setState({ error: null });
    this.props.onRetry?.();
  };

  render() {
    if (this.state.error) {
      return (
        <div className="consultor-workspace-body consultor-error-boundary" role="alert">
          <h2 className="consultor-error-boundary-title">Não foi possível carregar o Workspace do Consultor.</h2>
          <p className="consultor-error-boundary-desc">
            Ocorreu um erro ao exibir o painel. Você pode tentar novamente sem sair da página.
          </p>
          {import.meta.env?.DEV ? (
            <pre className="consultor-error-boundary-detail">{this.state.error.message}</pre>
          ) : null}
          <button type="button" className="btn-primary" onClick={this.handleRetry}>
            Tentar novamente
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
