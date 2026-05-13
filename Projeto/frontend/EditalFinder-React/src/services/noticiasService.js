import { dataService } from './dataService';

export async function fetchNoticias() {
  return dataService.getNoticias();
}
