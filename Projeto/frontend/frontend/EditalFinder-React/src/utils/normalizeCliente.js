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
  };
}
