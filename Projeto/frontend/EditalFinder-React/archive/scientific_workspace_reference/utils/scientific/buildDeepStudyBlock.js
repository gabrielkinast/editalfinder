import { interestLabelById } from './scientificInterestsConfig';
import { getDeepStudyArea } from './scientificDeepStudyCatalog';
import { getBooksForArea } from './scientificBookCatalog';
import { resolveCanonicalInterest } from './scientificInterestAliases';
import { getPowerIdeasForArea } from './getPowerIdeasForArea';

const LAYER_LABELS = {
  foundations: 'Fundamentos',
  intermediate: 'Intermediário',
  advanced: 'Avançado',
  researchLevel: 'Pesquisa/Mestrado',
  math: 'Matemática',
  physics: 'Física',
  chemistry: 'Química',
  computation: 'Computação',
};

/**
 * @param {string} interestId
 * @param {string[]} [matchedInterests]
 */
export function buildDeepStudyBlock(interestId, matchedInterests = []) {
  const canonicalKey = resolveCanonicalInterest(interestId);
  const area = getDeepStudyArea(interestId);
  if (!area) return null;

  const {
    key,
    label,
    description,
    formationGoal,
    prerequisites,
    theory,
    books,
    projectTracks,
  } = area;

  const matched = matchedInterests.length
    ? matchedInterests
    : [interestId].filter(Boolean);

  const matchedInterestLabels = matched.map(interestLabelById);
  const bookList = getBooksForArea(key);
  const powerIdeas = getPowerIdeasForArea(key);

  const flatBooks = [
    ...(books?.introductory || []),
    ...(books?.intermediate || []),
    ...(books?.advanced || []),
    ...(books?.computational || []),
  ];

  const practicalProjects = [
    ...(projectTracks?.basic || []).slice(0, 5),
    ...(projectTracks?.intermediate || []).slice(0, 3),
  ];

  const researchIdeas = [
    ...(theory?.researchLevel || []).slice(0, 6),
    ...(projectTracks?.masters || []).slice(0, 3),
  ];

  return {
    interestId: key,
    canonicalKey: key,
    sourceInterestId: interestId,
    label: label || interestLabelById(interestId),
    description,
    formationGoal,
    matchedInterests: matched,
    matchedInterestLabels,
    fundamentals: theory?.foundations || [],
    intermediate: theory?.intermediate || [],
    advanced: theory?.advanced || [],
    books: flatBooks.length ? flatBooks : bookList.map((b) => `${b.author} — ${b.title}`),
    practicalProjects,
    researchIdeas,
    professorQuestions: area.professorQuestions || [
      'Quais pré-requisitos devo consolidar primeiro nesta área?',
      'Qual livro introdutório melhor alinha com meu nível atual?',
      'Que projeto prático é mais adequado para o próximo semestre?',
      'Como conectar esta trilha a uma linha de IC/TCC ou mestrado?',
    ],
    theoryCounts: {
      foundations: theory?.foundations?.length || 0,
      intermediate: theory?.intermediate?.length || 0,
      advanced: theory?.advanced?.length || 0,
      researchLevel: theory?.researchLevel?.length || 0,
    },
    powerIdeas,
    deep: {
      prerequisites,
      theory,
      books,
      bookEntries: bookList,
      projectTracks,
      professorQuestions: area.professorQuestions,
      powerIdeas,
      layerLabels: LAYER_LABELS,
    },
  };
}
