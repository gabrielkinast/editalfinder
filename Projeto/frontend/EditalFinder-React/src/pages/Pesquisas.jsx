import FeedListaPage from './FeedListaPage';
import { dataService } from '../services/dataService';

export default function Pesquisas() {
  return (
    <FeedListaPage
      title="Pesquisas"
      searchPlaceholder="Buscar pesquisas..."
      exportBaseName="pesquisas"
      loadItems={() => dataService.getPesquisas()}
    />
  );
}
