import { isGrantsGovSource } from './grantsGovSource.js';
import { isGrantsGovUrl } from '../edital/officialEditalUrl.js';

/** Card snapshot do DOM E2E — indica Grants.gov por atributos/texto/URL resolvida. */
export function isGrantsCardRecord(card) {
  if (!card) return false;
  if (isGrantsGovSource(card.fonte) || isGrantsGovSource(card.source)) return true;

  const urls = [
    card.officialHref,
    card.officialTitle,
    card.btnViewTitle,
    card.btnInscTitle,
    card.qaResolvedUrl,
  ];
  for (const u of urls) {
    if (u && (isGrantsGovUrl(u) || /grants\.gov/i.test(String(u)))) return true;
  }

  const blob = `${card.textPreview || ''}`.toLowerCase();
  if (blob.includes('grants.gov')) return true;
  if (blob.includes('grants') && blob.includes('.gov')) return true;
  return false;
}
