import { Component } from 'react';
import { Link } from 'react-router-dom';
import { clearScientificWorkspaceLocalCache } from '../../utils/scientific/clearScientificWorkspaceLocalCache';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

export default class ScientificWorkspaceErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    logScientificWorkspace('error_boundary_caught', {
      message: error?.message,
      stack: error?.stack?.slice?.(0, 200),
    });
  }

  handleRetry = () => {
    this.setState({ error: null, errorInfo: null });
    this.props.onRetry?.();
  };

  handleClearCache = () => {
    const ok = window.confirm(
      'Limpar apenas os dados locais do Workspace Científico (interesses, caderno e filtros)? Esta ação não apaga dados do servidor.',
    );
    if (!ok) return;
    clearScientificWorkspaceLocalCache();
    this.setState({ error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    const message = this.state.error?.message || 'Erro desconhecido';

    return (
      <div className="page-wrapper scientific-workspace-page">
        <div className="scientific-error-boundary-card">
          <h1>Não foi possível carregar o Workspace Científico</h1>
          <p className="scientific-muted">
            Ocorreu um erro ao renderizar esta página. Seus dados no servidor não foram alterados.
          </p>
          {import.meta.env.DEV && (
            <pre className="scientific-error-boundary-pre">{message}</pre>
          )}
          <div className="scientific-error-boundary-actions">
            <button type="button" className="scientific-btn scientific-btn-primary" onClick={this.handleRetry}>
              Tentar novamente
            </button>
            <button type="button" className="scientific-btn scientific-btn-secondary" onClick={this.handleClearCache}>
              Limpar cache local do Workspace Científico
            </button>
            <Link to="/dashboard" className="scientific-btn scientific-btn-ghost">
              Voltar ao Dashboard
            </Link>
          </div>
          {import.meta.env.DEV && (
            <p className="scientific-muted scientific-error-boundary-dev">
              Dica DEV: verifique o console — erros comuns incluem localStorage inválido ou imports
              ausentes.
            </p>
          )}
        </div>
      </div>
    );
  }
}
