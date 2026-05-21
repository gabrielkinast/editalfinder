import {
  hydratePerfilFromClienteRow,
  parsePerfilConsultivoFromExtras,
} from './cliente/clientePerfilConsultivo';

/**
 * Unifica shapes vindos do PostgREST/Supabase (snake_case, camelCase ou sinônimos comuns).
 */
function pickFirst(obj, keys) {
  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null && obj[k] !== '') return obj[k];
  }
  return undefined;
}

export function normalizeClienteRow(row) {
  if (!row || typeof row !== 'object') return row;

  const id =
    pickFirst(row, ['id_cliente', 'idCliente', 'cliente_id', 'id']) ?? row.id_cliente;

  const extras = row.extras;
  const perfilConsultivo = hydratePerfilFromClienteRow(row);
  const perfilRaw = parsePerfilConsultivoFromExtras(extras);

  const contatoPrincipal = {
    ...perfilConsultivo.contato,
    nome:
      pickFirst(row, ['nome_contato', 'nomeContato']) ?? perfilConsultivo.contato?.nome ?? '',
    email: pickFirst(row, ['email', 'Email']) ?? perfilConsultivo.contato?.email ?? '',
    telefone: pickFirst(row, ['telefone', 'Telefone']) ?? perfilConsultivo.contato?.telefone ?? '',
  };

  return {
    ...row,
    id_cliente: id,
    id_usuario:
      pickFirst(row, ['id_usuario', 'idUsuario', 'usuario_id', 'id_usuario_fk']) ?? row.id_usuario ?? null,
    nome_empresa:
      pickFirst(row, ['nome_empresa', 'nomeEmpresa', 'NomeEmpresa', 'empresa', 'nome', 'nome_fantasia'])
      ?? row.nome_empresa,
    razao_social: pickFirst(row, ['razao_social', 'razaoSocial', 'RazaoSocial']) ?? row.razao_social,
    cnpj: pickFirst(row, ['cnpj', 'CNPJ']) ?? row.cnpj,
    setor: pickFirst(row, ['setor', 'Setor']) ?? row.setor,
    porte_empresa: pickFirst(row, ['porte_empresa', 'porteEmpresa', 'porte']) ?? row.porte_empresa,
    status:
      typeof pickFirst(row, ['status', 'Status']) !== 'undefined'
        ? pickFirst(row, ['status', 'Status'])
        : row.status,
    cidade: pickFirst(row, ['cidade', 'Cidade', 'municipio']) ?? row.cidade,
    estado: pickFirst(row, ['estado', 'Estado', 'uf']) ?? row.estado,
    regiao: pickFirst(row, ['regiao', 'Regiao']) ?? row.regiao,
    data_abertura: pickFirst(row, ['data_abertura', 'dataAbertura', 'data_constituicao']) ?? row.data_abertura,
    cnae_principal: pickFirst(row, ['cnae_principal', 'cnaePrincipal', 'cnae']) ?? row.cnae_principal,
    faturamento_anual:
      pickFirst(row, ['faturamento_anual', 'faturamentoAnual', 'receita_anual']) ?? row.faturamento_anual,
    numero_funcionarios:
      pickFirst(row, ['numero_funcionarios', 'numeroFuncionarios', 'total_empregados']) ?? row.numero_funcionarios,
    area_inovacao: pickFirst(row, ['area_inovacao', 'areaInovacao']) ?? row.area_inovacao,
    descricao_projeto:
      pickFirst(row, ['descricao_projeto', 'descricaoProjeto', 'descricao']) ?? row.descricao_projeto,
    interesse_temas: pickFirst(row, ['interesse_temas', 'interesseTemas']) ?? row.interesse_temas,
    interesse_valor_min: row.interesse_valor_min ?? 0,
    interesse_valor_max: row.interesse_valor_max ?? 0,
    site: pickFirst(row, ['site', 'website']) ?? perfilRaw.site ?? '',
    email: contatoPrincipal.email,
    telefone: contatoPrincipal.telefone,
    nome_contato: contatoPrincipal.nome,
    extras,
    perfilConsultivo,
    contatoPrincipal,
    dadosEconomicos: perfilConsultivo.dados_economicos,
    perfilTecnologico: perfilConsultivo.perfil_tecnologico,
    preferenciasFomento: perfilConsultivo.preferencias_fomento,
    documentacao: perfilConsultivo.documentacao,
    diagnosticoConsultor: perfilConsultivo.diagnostico_consultor,
  };
}
