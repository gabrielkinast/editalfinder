import FeedListaPage from './FeedListaPage';
import { dataService } from '../services/dataService';

export default function Noticias() {
  return (
    <FeedListaPage
      title="Notícias"
      searchPlaceholder="Buscar notícias..."
      exportBaseName="noticias"
      loadItems={() => dataService.getNoticias()}
    />
  );
}
