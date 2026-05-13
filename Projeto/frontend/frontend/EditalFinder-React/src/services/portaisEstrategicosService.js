/**
 * Portais estratégicos — vistas públicas configuráveis (`VITE_VIEW_FORNECEDORES`, `VITE_VIEW_INVESTIMENTOS`).
 */
import { dataService } from './dataService';

export async function fetchFornecedoresFront() {
  return dataService.getPortaisFornecedoresFront();
}

export async function fetchInvestimentosFront() {
  return dataService.getPortaisInvestimentosFront();
}
