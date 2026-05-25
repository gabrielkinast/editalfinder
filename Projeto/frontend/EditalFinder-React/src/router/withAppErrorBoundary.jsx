import AppErrorBoundary from '../components/common/AppErrorBoundary';

/**
 * Envolve página com AppErrorBoundary (Fase app_feedback).
 * @param {string} origem
 * @param {string} pagina
 * @param {import('react').ReactNode} element
 * @param {object} [opts]
 */
export function withAppErrorBoundary(origem, pagina, element, opts = {}) {
  return (
    <AppErrorBoundary origem={origem} pagina={pagina} {...opts}>
      {element}
    </AppErrorBoundary>
  );
}
