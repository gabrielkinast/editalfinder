import { usePermissions } from '../../hooks/usePermissions';

export default function AdminTable({ columns, data, onEdit, onDelete }) {
  const permissions = usePermissions();

  return (
    <div className="table-container">
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((col) => <th key={col.key}>{col.label}</th>)}
            {(permissions.canEdit || permissions.canDelete) && <th>Ações</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + ((permissions.canEdit || permissions.canDelete) ? 1 : 0)} style={{ textAlign: 'center', padding: '20px' }}>
                Nenhum item encontrado.
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr key={item.id || item.id_usuario || item.id_cliente || item.id_organizacao || item.id_edital || idx}>
                {columns.map((col) => (
                  <td key={col.key} data-label={col.label}>
                    {col.render ? col.render(item[col.key], item) : item[col.key]}
                  </td>
                ))}
                {(permissions.canEdit || permissions.canDelete) && (
                  <td>
                    {permissions.canEdit && (
                      <button className="btn-action btn-edit" onClick={() => onEdit(item)}>Editar</button>
                    )}
                    {permissions.canDelete && (
                      <button className="btn-action btn-delete" onClick={() => onDelete(item.id_usuario || item.id_cliente || item.id_organizacao || item.id_edital || item.id)}>Deletar</button>
                    )}
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
