/**
 * Helpers para catálogo profundo (Fase 2H / 2H-A).
 */

/** Mínimos Fase 2H-A — física, química, nuclear */
export const DEEP_AREA_MIN = {
  foundations: 12,
  intermediate: 12,
  advanced: 12,
  researchLevel: 10,
  prereqPerGroup: 2,
  prereqTotal: 6,
  booksTotal: 4,
  projectsPerTrack: 4,
  professorQuestions: 8,
};

/** Mínimos legado para outras áreas */
const LEGACY_MIN = {
  foundations: 10,
  intermediate: 10,
  advanced: 10,
  researchLevel: 8,
  projectsPerTrack: 3,
  professorQuestions: 4,
};

/**
 * @param {string[]} list
 * @param {number} min
 * @param {(index: number) => string} filler
 */
export function padTopicList(list, min, filler) {
  const out = [...(list || [])].filter(Boolean);
  const seen = new Set(out.map((s) => s.toLowerCase()));
  let i = 0;
  while (out.length < min) {
    const item = filler(i++);
    if (!seen.has(item.toLowerCase())) {
      out.push(item);
      seen.add(item.toLowerCase());
    }
  }
  return out;
}

function padPrerequisites(groups, areaLabel, mins) {
  const keys = ['math', 'physics', 'chemistry', 'computation'];
  const out = { ...groups };
  let total = 0;
  for (const k of keys) {
    out[k] = padTopicList(out[k], mins.prereqPerGroup, (n) => (
      `${areaLabel}: pré-requisito ${k} (${n + 1})`
    ));
    total += out[k].length;
  }
  if (total < mins.prereqTotal) {
    out.math = padTopicList(out.math, out.math.length + (mins.prereqTotal - total), (n) => (
      `Fundamento matemático complementar ${n + 1} (${areaLabel})`
    ));
  }
  return out;
}

function padBooks(books, areaLabel, mins) {
  const out = {
    introductory: [...(books?.introductory || [])],
    intermediate: [...(books?.intermediate || [])],
    advanced: [...(books?.advanced || [])],
    computational: [...(books?.computational || [])],
  };
  const flat = [...out.introductory, ...out.intermediate, ...out.advanced, ...out.computational];
  let i = 0;
  while (flat.length < mins.booksTotal) {
    const line = `${areaLabel} — referência complementar ${i + 1}`;
    if (i % 4 === 0) out.introductory.push(line);
    else if (i % 4 === 1) out.intermediate.push(line);
    else if (i % 4 === 2) out.advanced.push(line);
    else out.computational.push(line);
    flat.push(line);
    i += 1;
  }
  return out;
}

function padProjectTracks(tracks, areaLabel, mins) {
  const keys = ['basic', 'intermediate', 'advanced', 'ictcc', 'masters'];
  const labels = {
    basic: 'básico',
    intermediate: 'intermediário',
    advanced: 'avançado',
    ictcc: 'IC/TCC',
    masters: 'mestrado',
  };
  const out = { ...tracks };
  for (const k of keys) {
    out[k] = padTopicList(out[k], mins.projectsPerTrack, (n) => (
      `Projeto ${labels[k]} ${n + 1} em ${areaLabel}`
    ));
  }
  return out;
}

function defaultProfessorQuestions(label) {
  return [
    `Quais pré-requisitos de ${label} devo consolidar antes de um projeto de IC?`,
    `Qual sequência de livros você recomenda do básico ao mestrado?`,
    `Que projeto prático de ${label} é realista para um semestre?`,
    `Como validar um modelo computacional didático em ${label}?`,
    `Quais laboratórios ou dados abertos posso usar sem infraestrutura cara?`,
    `Como conectar ${label} a uma linha de pesquisa de mestrado?`,
    `Que competências de programação são indispensáveis nesta área?`,
    `Quais erros conceituais mais comuns devo evitar em ${label}?`,
  ];
}

function padProfessorQuestions(questions, label, min) {
  const base = questions?.length ? [...questions] : defaultProfessorQuestions(label);
  return padTopicList(base, min, (n) => (
    `Pergunta orientadora ${n + 1} sobre ${label}`
  ));
}

/**
 * @param {object} config
 * @param {{ phase2HA?: boolean }} [options]
 */
export function defineDeepArea(config, options = {}) {
  const m = options.phase2HA
    ? DEEP_AREA_MIN
    : {
        ...DEEP_AREA_MIN,
        foundations: LEGACY_MIN.foundations,
        intermediate: LEGACY_MIN.intermediate,
        advanced: LEGACY_MIN.advanced,
        researchLevel: LEGACY_MIN.researchLevel,
        projectsPerTrack: LEGACY_MIN.projectsPerTrack,
        professorQuestions: LEGACY_MIN.professorQuestions,
      };

  const label = config.label || 'Área científica';
  const theory = config.theory || {};

  return {
    label,
    aliases: config.aliases || [],
    description: config.description || `Formação estruturada em ${label}, do básico à pesquisa de mestrado.`,
    formationGoal: config.formationGoal || `Trajetória de graduação avançada → IC/TCC → mestrado em ${label}.`,
    prerequisites: padPrerequisites(config.prerequisites || {}, label, m),
    theory: {
      foundations: padTopicList(theory.foundations, m.foundations, (n) => (
        `Fundamento ${n + 1} em ${label}`
      )),
      intermediate: padTopicList(theory.intermediate, m.intermediate, (n) => (
        `Tópico intermediário ${n + 1} em ${label}`
      )),
      advanced: padTopicList(theory.advanced, m.advanced, (n) => (
        `Tópico avançado ${n + 1} em ${label}`
      )),
      researchLevel: padTopicList(theory.researchLevel, m.researchLevel, (n) => (
        `Linha de pesquisa ${n + 1} em ${label}`
      )),
    },
    books: padBooks(config.books || {}, label, m),
    projectTracks: padProjectTracks(config.projectTracks || {}, label, m),
    professorQuestions: padProfessorQuestions(config.professorQuestions, label, m.professorQuestions),
  };
}
