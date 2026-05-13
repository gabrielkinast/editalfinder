/**
 * Camada fina sobre `dataService` — lista de editais para o catálogo principal.
 * As páginas existentes continuam a importar `dataService` diretamente até migração opcional.
 */
import { dataService } from './dataService';

export async function fetchEditaisCatalog() {
  return dataService.getEditais();
}

export async function fetchEditalById(id) {
  return dataService.getEditalById(id);
}

export async function fetchAnexosByEdital(idEdital) {
  return dataService.getAnexosByEdital(idEdital);
}
