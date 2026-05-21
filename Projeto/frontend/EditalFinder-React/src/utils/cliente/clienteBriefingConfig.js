/** IDs persistidos em extras.perfil_consultivo.preferencias_fomento.tipos_recurso */
export const BRIEFING_TIPOS_RECURSO = [
  { id: 'subvencao', label: 'Subvenção econômica' },
  { id: 'credito', label: 'Crédito / financiamento' },
  { id: 'bolsa', label: 'Bolsa / formação' },
  { id: 'cooperacao_ict', label: 'Cooperação com ICT' },
  { id: 'cooperacao_internacional', label: 'Cooperação internacional' },
  { id: 'licitacao', label: 'Licitação / contratação pública' },
  { id: 'investimento', label: 'Investimento' },
  { id: 'aceleracao', label: 'Programa de aceleração' },
];

export const BRIEFING_FAIXA_VALOR = [
  { id: 'ate_50k', label: 'Até R$ 50 mil', min: 0, max: 50000 },
  { id: '50k_250k', label: 'R$ 50 mil a R$ 250 mil', min: 50000, max: 250000 },
  { id: '250k_1m', label: 'R$ 250 mil a R$ 1 milhão', min: 250000, max: 1000000 },
  { id: 'acima_1m', label: 'Acima de R$ 1 milhão', min: 1000000, max: 0 },
  { id: 'indefinido', label: 'Ainda não definido', min: null, max: null },
];

export const BRIEFING_CRITERIOS_ACEITE = [
  { id: 'fluxo_continuo', label: 'Fluxo contínuo' },
  { id: 'prazo_curto', label: 'Chamadas com prazo curto' },
  { id: 'internacional', label: 'Oportunidades internacionais' },
  { id: 'contrapartida', label: 'Oportunidades com contrapartida' },
  { id: 'licitacao', label: 'Licitações' },
  { id: 'parceria', label: 'Projetos em parceria' },
];

export const BRIEFING_DOCUMENTOS = [
  { id: 'cnpj_contrato', label: 'CNPJ / contrato social', docKey: 'contrato_social' },
  { id: 'certidoes_fiscais', label: 'Certidões fiscais', docKey: 'certidoes_fiscais' },
  { id: 'balanco_dre', label: 'Balanço / DRE', docKey: 'balanco_dre' },
  { id: 'portfolio', label: 'Portfólio / apresentação institucional', docKey: 'documentos_tecnicos' },
  { id: 'descricao_tecnica', label: 'Descrição técnica do projeto', docKey: 'documentos_tecnicos' },
  { id: 'orcamento', label: 'Orçamento preliminar', docKey: 'documentos_tecnicos' },
  { id: 'curriculos', label: 'Currículos da equipe', docKey: 'representante_legal' },
  { id: 'nenhum', label: 'Nenhum / ainda não verificado', docKey: null },
];
