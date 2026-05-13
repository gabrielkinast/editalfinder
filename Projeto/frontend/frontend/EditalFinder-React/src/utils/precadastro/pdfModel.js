import { computeCompletion } from './projectIntel';

function t(v) {
  if (v == null || v === '') return '—';
  return String(v);
}

/**
 * Normaliza estado do formulário + cliente para o gerador de PDF (layout de documento).
 * @param {Record<string, unknown>} formData
 * @param {Record<string, unknown> | null} cliente
 * @param {{ editalTitulo?: string; geradoEm?: string; sistema?: string }} meta
 */
export function mapFormToPdfModel(formData, cliente, meta = {}) {
  const c = cliente || {};
  const completion = computeCompletion(formData || {});

  const empresaNome = c.nome_empresa || c.razao_social || 'Cliente';
  const sede = [
    [formData.bloco1_logradouro, formData.bloco1_numero, formData.bloco1_complemento].filter(Boolean).join(', '),
    formData.bloco1_bairro,
    [formData.bloco1_municipio, formData.bloco1_uf].filter(Boolean).join(' / '),
    formData.bloco1_cep ? `CEP ${formData.bloco1_cep}` : '',
  ]
    .filter(Boolean)
    .join(' — ');

  const linhasSel = [];
  if (formData.bloco1_linha_credito_principal) {
    linhasSel.push('Linha principal (crédito inovação — produto institucional)');
  }
  if (formData.bloco1_linha_credito_telecom) {
    linhasSel.push('Linha com aderência a telecomunicações');
  }

  return {
    cover: {
      empresa: empresaNome,
      tituloDoc: 'Relatório de pré-enquadramento',
      subtitulo:
        meta.editalTitulo ||
        formData.bloco_estr_edital_ref_titulo ||
        'Pré-cadastro de projeto para linhas de crédito / editais',
      dataGeracao: meta.geradoEm || new Date().toLocaleString('pt-BR'),
    },
    executive: {
      cliente: empresaNome,
      editalOuLinha:
        meta.editalTitulo ||
        formData.bloco_estr_edital_ref_titulo ||
        (linhasSel[0] ?? 'Não especificado'),
      aderencia:
        formData.bloco_estr_aderencia_nivel ||
        `${completion.score}% — ${completion.level === 'pronto' ? 'pronto para PDF' : completion.level}`,
      recomendacao: (
        formData.bloco_estr_motivo_recomendacao ||
        formData.bloco2_resumo_publicavel ||
        ''
      ).slice(0, 600),
      completudeLabel: `${completion.level} (${completion.score}%)`,
      linhasSeleccionadas: linhasSel,
    },
    empresa: {
      cnpj: t(formData.bloco1_cnpj),
      razao: t(formData.bloco1_razao_social),
      fantasia: t(formData.bloco1_nome_fantasia),
      constituicao: t(formData.bloco1_data_constituicao),
      inicioOp: t(formData.bloco1_data_inicio_operacao),
      sede: sede || '—',
      setor: t(formData.bloco1_setor_empresa || c.setor),
      porte: t(formData.bloco1_porte_empresa || c.porte_empresa),
      cnae: t(formData.bloco1_cnae),
      site: t(formData.bloco1_site),
      contatoNome: t(formData.bloco1_nome_contato),
      contatoCargo: t(formData.bloco1_cargo_contato),
      contatoEmail: t(formData.bloco1_email_contato),
      contatoFone: t(formData.bloco1_telefone_contato),
    },
    projeto: {
      titulo: t(formData.bloco2_titulo_projeto),
      resumo: t(formData.bloco_estr_resumo_executivo || formData.bloco2_resumo_publicavel),
      problema: t(formData.bloco_estr_problema_oportunidade),
      solucao: t(formData.bloco_estr_solucao_proposta),
      objetivo: t(formData.bloco_estr_objetivo_geral),
      diferencial: t(formData.bloco_estr_diferencial_inovador),
      maturidade: t(formData.bloco_estr_maturidade),
      publico: t(formData.bloco_estr_publico_mercado),
      resultados: t(formData.bloco_estr_resultados_esperados),
      finalidades: ['a', 'b', 'c', 'd', 'e', 'f', 'g'].map((l) => ({
        tag: l,
        texto: t(formData[`bloco2_finalidade_${l}`]),
      })),
    },
    enquadramento: {
      linhas: linhasSel.join(' · ') || '—',
      justificativa: t(formData.bloco_estr_por_que_linha),
      aderencias: t(formData.bloco_estr_principais_aderencias),
      requisitos: t(formData.bloco_estr_requisitos_atendidos),
      lacunas: t(formData.bloco_estr_lacunas),
      documentos: t(formData.bloco_estr_docs_recomendados),
      proximos: t(formData.bloco_estr_proximos_passos),
    },
    observacoes: {
      internas: t(formData.bloco_estr_obs_internas),
      pendencias: t(formData.bloco_estr_pendencias_checklist || formData.bloco_estr_pendencias),
    },
    rodape: {
      sistema: meta.sistema || 'EditalFinder — Pré-cadastro de projeto',
      data: meta.geradoEm || new Date().toISOString().slice(0, 10),
    },
    /** Todo o formulário cru ainda disponível para anexos / tabela longa no PDF profissional */
    rawForm: formData,
    completion,
  };
}
