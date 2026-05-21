import { clienteEnrichedForApps } from './cliente/clientePerfilConsultivo';

/**
 * Estado inicial vazio do formulário de pré-cadastro de projeto para editais.
 * Inspirado estruturalmente em modelo oficial de apresentação de projeto / linha de crédito.
 */

/** @deprecated use storageKeyPrecadDraft */
export function storageKeyPrecadastroProjeto(clienteId) {
  return `precadastro_projeto_${clienteId}`;
}

/** Chave estável por cliente + edição/contexto (`geral` se não houver edital identificável). */
export function fingerprintPrecadContext(editalAssociado = null, tituloManual = '', radarMatch = null) {
  const id = editalAssociado?.id_edital ?? editalAssociado?.id;
  if (id != null && `${id}` !== '') return `${id}`;
  const t = (
    `${editalAssociado?.titulo || tituloManual || radarMatch?.tituloEdital || ''}`.trim() || 'geral'
  )
    .replace(/[^\wÀ-ú\- ]+/gi, '_')
    .slice(0, 48);
  return t || 'geral';
}

export function storageKeyPrecadDraft(clienteId, editalFingerprint) {
  const fp = `${editalFingerprint || 'geral'}`.slice(0, 64);
  return `precadastro_draft_${clienteId}_${fp}`;
}

const ENVELOPE_VERSION = 2;

function val(v, fallback = '') {
  return v !== undefined && v !== null ? String(v) : fallback;
}

export function precadastroEmptyState() {
  return {
    bloco1_linha_credito_principal: false,
    bloco1_linha_credito_telecom: false,

    bloco1_porte_empresa: '',
    bloco1_setor_empresa: '',

    bloco_estr_edital_ref_titulo: '',
    bloco_estr_oportunidade_fonte: '',
    bloco_estr_oportunidade_prazo: '',
    bloco_estr_oportunidade_link: '',
    bloco_estr_oportunidades_selecionadas: '',
    bloco_estr_score_compatibilidade: '',
    bloco_estr_alertas_radar: '',
    bloco_estr_tipo_recurso_pdf: '',
    bloco_estr_ref_fin_texto: '',
    bloco_estr_aderencia_nivel: '',
    bloco_estr_status_precadastro: 'rascunho',
    bloco_estr_plano_trabalho: '',
    bloco_estr_orcamento_resumo: '',
    bloco_estr_orcamento_contrapartida: '',
    bloco_estr_orcamento_categorias: '',
    bloco_estr_orcamento_observacoes: '',
    bloco_estr_docs_cliente: '',
    bloco_estr_docs_tecnicos: '',
    bloco_estr_docs_financeiros: '',
    bloco_estr_docs_edital_regulamento: '',
    bloco_estr_riscos_pendencias: '',
    bloco_estr_checklist_inicial: '',

    bloco_estr_resumo_executivo: '',
    bloco_estr_objetivo_geral: '',
    bloco_estr_problema_oportunidade: '',
    bloco_estr_solucao_proposta: '',
    bloco_estr_diferencial_inovador: '',
    bloco_estr_maturidade: '',
    bloco_estr_publico_mercado: '',
    bloco_estr_resultados_esperados: '',

    bloco_estr_motivo_recomendacao: '',
    bloco_estr_principais_aderencias: '',
    bloco_estr_pontos_complementar: '',
    bloco_estr_por_que_linha: '',
    bloco_estr_requisitos_atendidos: '',
    bloco_estr_lacunas: '',
    bloco_estr_docs_recomendados: '',
    bloco_estr_proximos_passos: '',

    bloco_estr_declaracao_custom: '',

    bloco_estr_obs_internas: '',
    bloco_estr_pendencias: '',
    bloco_estr_pendencias_checklist: '',

    bloco1_cnpj: '',
    bloco1_razao_social: '',
    bloco1_nome_fantasia: '',
    bloco1_data_constituicao: '',
    bloco1_data_inicio_operacao: '',

    bloco1_logradouro: '',
    bloco1_numero: '',
    bloco1_complemento: '',
    bloco1_bairro: '',
    bloco1_municipio: '',
    bloco1_uf: '',
    bloco1_cep: '',
    bloco1_site: '',

    bloco1_cpf_contato: '',
    bloco1_nome_contato: '',
    bloco1_cargo_contato: '',
    bloco1_email_contato: '',
    bloco1_telefone_contato: '',

    bloco1_cnae: '',
    bloco1_parte_grupo_economico: '',
    bloco1_faturamento_grupo: '',
    bloco1_receita_rob_ultimo: '',
    bloco1_ebitda: '',
    bloco1_data_ref_receita: '',
    bloco1_num_pessoas_receita_ref: '',
    bloco1_despesa_empregados_receita: '',

    bloco1_doutores: '',
    bloco1_mestres: '',
    bloco1_graduados: '',
    bloco1_fund_medio: '',
    bloco1_total_empregados: '',

    bloco1_orgao_antecedentes_sim: '',
    bloco1_orgao_antecedentes_texto: '',

    bloco1_principais_atividades: '',

    bloco1_pdi_infraestrutura: '',
    bloco1_pdi_detalhe_pessoas: '',
    bloco1_pdi_parceria_ict_sim: '',
    bloco1_pdi_parceria_ict_txt: '',
    bloco1_pdi_parceria_empresas_sim: '',
    bloco1_pdi_parceria_empresas_txt: '',
    bloco1_pdi_pi_3anos_sim: '',
    bloco1_pdi_pi_3anos_txt: '',
    bloco1_pdi_contratos_inpi_sim: '',
    bloco1_pdi_contratos_inpi_txt: '',
    bloco1_pdi_outras_agencias_sim: '',
    bloco1_pdi_outras_agencias_txt: '',

    bloco2_titulo_projeto: '',
    bloco2_resumo_publicavel: '',
    bloco2_finalidade_a: '',
    bloco2_finalidade_b: '',
    bloco2_finalidade_c: '',
    bloco2_finalidade_d: '',
    bloco2_finalidade_e: '',
    bloco2_finalidade_f: '',
    bloco2_finalidade_g: '',
    bloco2_comentarios_adicionais: '',
    bloco2_cnae_projeto: '',
    bloco2_uf_projeto: '',

    bloco2_pd_i_pos: '',
    bloco2_pd_i_graduados: '',
    bloco2_pd_i_tecnico: '',
    bloco2_pd_i_outros: '',

    bloco2_tp_inov_novo_produto: false,
    bloco2_tp_inov_novo_processo: false,
    bloco2_tp_inov_melhoria_produto: false,
    bloco2_tp_inov_melhoria_processo: false,
    bloco2_nivel_empresa: false,
    bloco2_nivel_regiao: false,
    bloco2_nivel_brasil: false,
    bloco2_nivel_mundo: false,
    bloco2_aspectos_regulatorios_sim: '',
    bloco2_aspectos_regulatorios_txt: '',

    bloco2_recursos_adicionais_sim: '',
    bloco2_recursos_adicionais_valor: '',
    bloco2_valor_projeto_sem_def: false,

    bloco2_pct_icts: '',
    bloco2_justifica_import_naosimilar: false,
    bloco2_justifica_import_qualidade: false,
    bloco2_justifica_import_preco: false,
    bloco2_justifica_sem_importados: false,
    bloco2_justifica_import_obs: '',

    bloco2_compromiso_social: '',

    bloco2_imp_eco_qualidade: false,
    bloco2_imp_eco_custo_trabalho: false,
    bloco2_imp_eco_custo_prod: false,
    bloco2_imp_eco_automacao: false,
    bloco2_imp_eco_participacao: false,
    bloco2_imp_eco_gama: false,
    bloco2_imp_eco_regulatorio: false,
    bloco2_imp_eco_manter_part: false,
    bloco2_imp_eco_novos_mercados: false,
    bloco2_imp_eco_receitas: false,
    bloco2_imp_eco_capacidade: false,
    bloco2_imp_eco_rd: false,
    bloco2_imp_eco_flex: false,
    bloco2_imp_eco_outros_txt: '',

    bloco2_imp_soc_emp_direct: false,
    bloco2_imp_soc_emp_indir: false,
    bloco2_imp_soc_bemestar: false,
    bloco2_imp_soc_seguranca: false,
    bloco2_imp_soc_educacao: false,
    bloco2_imp_soc_pobreza: false,
    bloco2_imp_soc_qualidade_vida: false,
    bloco2_imp_soc_moradia: false,
    bloco2_imp_soc_pcd: false,
    bloco2_imp_soc_outros_txt: '',

    bloco2_imp_amb_co2: false,
    bloco2_imp_amb_energia: false,
    bloco2_imp_amb_agua: false,
    bloco2_imp_amb_poluentes: false,
    bloco2_imp_amb_reciclado: false,
    bloco2_imp_amb_materiais: false,
    bloco2_imp_amb_subst_energy: false,
    bloco2_imp_amb_subst_mp: false,
    bloco2_imp_amb_contaminacao: false,
    bloco2_imp_amb_reciclagem: false,
    bloco2_imp_amb_outros_txt: '',

    bloco2_licencas: '',

    bloco2_uso_fontes: [{ item: '', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' }],
    bloco2_metas_fisicas: [{ meta: '', atividade: '', indicador: '', ini: '', fim: '' }],
  };
}

/**
 * Garante campos novos em rascunhos antigos (localStorage v1/v2) sem apagar dados existentes.
 * @param {Record<string, unknown>} form
 */
export function migratePrecadForm(form) {
  const empty = precadastroEmptyState();
  const out = { ...empty, ...(form && typeof form === 'object' ? form : {}) };
  if (hasText(out.bloco_estr_docs_recomendados) && !hasText(out.bloco_estr_docs_cliente)) {
    /* mantém agregado legado; split só quando autofill ou edição nova */
  }
  return out;
}

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function deepMergeClienteDraft(base, draft) {
  if (!draft || typeof draft !== 'object') return base;
  const out = { ...base };
  Object.keys(draft).forEach((k) => {
    const bv = base[k];
    const dv = draft[k];
    if (Array.isArray(dv)) {
      out[k] = [...dv];
    } else if (dv !== null && typeof dv === 'object' && bv !== undefined && typeof bv === 'object' && !Array.isArray(bv)) {
      out[k] = deepMergeClienteDraft(bv, dv);
    } else if (dv !== undefined) {
      out[k] = dv;
    }
  });
  return out;
}

/**
 * Estado inicial combinando cadastro cliente + valores vazios.
 * @param {object} cliente
 * @param {{ edital?: { titulo?: string }; editalTitulo?: string; radarMatch?: { tituloEdital?: string } }} [extras]
 */
export function buildInitialPrecadastroState(cliente, extras = {}) {
  const base = precadastroEmptyState();
  if (!cliente) return base;

  const c = clienteEnrichedForApps(cliente);
  const cont = c.contatoPrincipal || {};
  const eco = c.dadosEconomicos || {};
  const loc = c.perfilConsultivo?.localizacao || {};

  base.bloco1_cnpj = val(c.cnpj);
  base.bloco1_razao_social = val(c.razao_social);
  base.bloco1_nome_fantasia = val(c.nome_empresa);
  base.bloco1_data_constituicao = val(c.data_abertura);
  base.bloco1_data_inicio_operacao = val(loc.data_inicio_operacao);
  base.bloco1_municipio = val(c.cidade);
  base.bloco1_uf = val(c.estado);
  base.bloco1_cnae = val(c.cnae_principal);
  base.bloco1_porte_empresa = val(c.porte_empresa);
  base.bloco1_setor_empresa = val(c.setor);
  base.bloco1_nome_contato = val(cont.nome || c.nome_contato);
  base.bloco1_email_contato = val(cont.email || c.email);
  base.bloco1_telefone_contato = val(cont.telefone || c.telefone);
  base.bloco1_cargo_contato = val(cont.cargo);
  base.bloco1_cpf_contato = val(cont.cpf);
  base.bloco1_site = val(c.site);
  base.bloco1_ebitda = val(eco.ebitda);
  base.bloco1_parte_grupo_economico = val(eco.grupo_economico);

  base.bloco1_principais_atividades = [
    val(c.descricao_projeto),
    val(c.area_inovacao),
    val(c.setor),
  ]
    .filter(Boolean)
    .join('\n\n');

  if (c.faturamento_anual != null && c.faturamento_anual !== '') {
    base.bloco1_receita_rob_ultimo = String(c.faturamento_anual);
  }
  if (c.numero_funcionarios != null && c.numero_funcionarios !== '') {
    base.bloco1_total_empregados = String(c.numero_funcionarios);
  }

  const edTit = extras.editalTitulo || extras.edital?.titulo || extras.radarMatch?.tituloEdital;
  if (edTit) base.bloco_estr_edital_ref_titulo = val(edTit);

  return base;
}

/**
 * @returns {{ form: object; fieldIntel: Record<string, unknown>; hadStoredDraft: boolean; editalFingerprint: string }}
 */
export function loadPrecadEnvelope(clienteId, initialFromCliente, editalFingerprint = 'geral') {
  const fp = `${editalFingerprint || 'geral'}`.slice(0, 64);
  if (clienteId == null) {
    return { form: initialFromCliente, fieldIntel: {}, hadStoredDraft: false, editalFingerprint: fp };
  }

  const keysTry = [storageKeyPrecadDraft(clienteId, fp), storageKeyPrecadastroProjeto(clienteId)];

  for (const key of keysTry) {
    let raw = null;
    try {
      raw = localStorage.getItem(key);
    } catch {
      /* */
    }
    if (!raw) continue;
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && parsed.version === ENVELOPE_VERSION && parsed.form) {
        return {
          form: migratePrecadForm(deepMergeClienteDraft(initialFromCliente, parsed.form)),
          fieldIntel: typeof parsed.fieldIntel === 'object' && parsed.fieldIntel ? parsed.fieldIntel : {},
          hadStoredDraft: true,
          editalFingerprint: fp,
        };
      }
      return {
        form: migratePrecadForm(deepMergeClienteDraft(initialFromCliente, parsed)),
        fieldIntel: {},
        hadStoredDraft: true,
        editalFingerprint: fp,
      };
    } catch {
      /* próxima chave */
    }
  }

  return { form: initialFromCliente, fieldIntel: {}, hadStoredDraft: false, editalFingerprint: fp };
}

/** Compat: retorna só o form (sem metadados intel). */
export function loadDraftMerged(clienteId, initialFromCliente, editalFingerprint = 'geral') {
  return loadPrecadEnvelope(clienteId, initialFromCliente, editalFingerprint).form;
}

/**
 * @param {number|string} clienteId
 * @param {{ form: object; fieldIntel?: Record<string, unknown>; draftMeta?: object }} envelope
 * @param {string} [editalFingerprint]
 */
export function savePrecadEnvelope(clienteId, envelope, editalFingerprint = 'geral') {
  if (clienteId == null) return;
  const fp = `${editalFingerprint || 'geral'}`.slice(0, 64);
  try {
    const blob = {
      version: ENVELOPE_VERSION,
      form: envelope.form,
      fieldIntel: envelope.fieldIntel || {},
      draftMeta: {
        ...(envelope.draftMeta || {}),
        editalFingerprint: fp,
        savedAt: new Date().toISOString(),
      },
    };
    localStorage.setItem(storageKeyPrecadDraft(clienteId, fp), JSON.stringify(blob));
  } catch (e) {
    console.error('Falha ao salvar rascunho inteligente', e);
  }
}

/** @deprecated usar savePrecadEnvelope */
export function saveDraft(clienteId, state) {
  if (clienteId == null) return;
  savePrecadEnvelope(clienteId, { form: state, fieldIntel: {} }, 'geral');
}
