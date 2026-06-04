import { levelLabel, normalizeProjectLevel } from './scientificProjectLevels';
import { interestLabelById } from './scientificInterestsConfig';

/**
 * Tag visual para item do caderno (Fase 2B).
 * Ex.: "Projeto · Mestrado" ou "Feed · Nuclear"
 */
export function notebookDisplayTag(item) {
  const tipo = String(item?.tipo || '').toLowerCase();
  if (tipo === 'rota_estudo') return 'Rota/estudo';
  if (tipo === 'ideia_poderosa') return 'Ideia poderosa';
  if (tipo === 'pergunta_professor' || item?.categoria === 'pergunta') return 'Pergunta';
  const cat = item?.contentCategory || 'feed';
  const catLabel =
    cat === 'projeto' ? 'Projeto' : cat === 'estudo' ? 'Estudo' : 'Feed';
  const parts = [catLabel];

  if (item?.level) {
    parts.push(levelLabel(normalizeProjectLevel(item.level)));
  } else if (item?.levelLabel) {
    parts.push(item.levelLabel);
  }

  if (cat === 'feed' && item?.interesses?.[0]) {
    parts.push(interestLabelById(item.interesses[0]));
  }

  return parts.join(' · ');
}
