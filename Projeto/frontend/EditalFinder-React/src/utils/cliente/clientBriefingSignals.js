import { hydratePerfilFromClienteRow } from './clientePerfilConsultivo';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

/**
 * Indica se o cliente já tem conteúdo típico do briefing salvo (sem schema novo).
 * @param {object|null} cliente — linha normalizada
 */
export function hasBriefingContent(cliente) {
  if (!cliente) return false;
  const perfil = cliente.perfilConsultivo || hydratePerfilFromClienteRow(cliente);
  const diag = perfil?.diagnostico_consultor || {};
  const tec = perfil?.perfil_tecnologico || {};
  const pref = perfil?.preferencias_fomento || {};
  const doc = perfil?.documentacao || {};

  if (hasText(diag.contexto_cliente)) return true;
  if (hasText(diag.observacoes_internas)) return true;
  if (hasText(tec.descricao_projeto)) return true;
  if (hasText(tec.temas_prioritarios)) return true;
  if (Array.isArray(pref.tipos_recurso) && pref.tipos_recurso.length > 0) return true;
  if (hasText(pref.faixa_valor_interesse)) return true;
  if (Array.isArray(pref.criterios_aceite) && pref.criterios_aceite.length > 0) return true;
  if (Array.isArray(doc.documentos_disponiveis) && doc.documentos_disponiveis.length > 0) {
    return true;
  }

  return false;
}

/**
 * Badge/subtítulo para etapa Perfil na esteira.
 * @param {object|null} cliente
 * @param {number} profileScore
 * @param {number} [profileThreshold=70]
 * @returns {{ kind: 'saved'|'pending'|'recommended'|null, label: string }}
 */
export function getBriefingWorkflowBadge(cliente, profileScore, profileThreshold = 70) {
  if (!cliente) return { kind: null, label: '' };
  if (hasBriefingContent(cliente)) {
    return { kind: 'saved', label: 'Briefing salvo' };
  }
  if (profileScore >= profileThreshold) {
    return { kind: null, label: '' };
  }
  if (profileScore < 50) {
    return { kind: 'recommended', label: 'Briefing recomendado' };
  }
  return { kind: 'pending', label: 'Briefing pendente' };
}
