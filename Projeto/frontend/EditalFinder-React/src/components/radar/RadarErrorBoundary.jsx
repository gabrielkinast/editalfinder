import { Component } from 'react';

export default class RadarErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('[radar-error-boundary]', {
      message: error?.message,
      stack: error?.stack,
      componentStack: info?.componentStack,
    });
  }

  handleRetry = () => {
    this.setState({ error: null });
    this.props.onRetry?.();
  };

  render() {
    if (this.state.error) {
      return (
        <div className="radar-error-boundary" role="alert">
          <h3>Erro ao renderizar o Radar</h3>
          <p>Tente recarregar a página ou recalcular as recomendações.</p>
          {import.meta.env?.DEV && (
            <pre className="radar-error-boundary-detail">{this.state.error.message}</pre>
          )}
          <div className="radar-error-boundary-actions">
            <button type="button" className="radar-btn-recalc" onClick={this.handleRetry}>
              Tentar novamente
            </button>
            <button
              type="button"
              className="radar-btn-recalc"
              onClick={() => window.location.reload()}
            >
              Recarregar página
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
