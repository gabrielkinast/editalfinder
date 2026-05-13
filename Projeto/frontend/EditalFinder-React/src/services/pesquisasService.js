import { dataService } from './dataService';

export async function fetchPesquisas() {
  return dataService.getPesquisas();
}
