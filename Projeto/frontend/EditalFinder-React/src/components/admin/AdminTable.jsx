import { usePermissions } from '../../hooks/usePermissions';

export default function AdminTable({ columns, data, onEdit, onDelete }) {
  const permissions = usePermissions();
  
  // A primeira coluna é SEMPRE o ID nas tabelas de cadastro
  const idKey = columns[0]?.key;

  return (
    <div className="table-container">
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((col) => <th key={col.key}>{col.label}</th>)}
            {(permissions.canEdit || permissions.canDelete || data.some(item => item.link)) && <th>Ações</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + ((permissions.canEdit || permissions.canDelete || data.some(item => item.link)) ? 1 : 0)} style={{ textAlign: 'center', padding: '20px' }}>
                Nenhum item encontrado.
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr key={item[idKey] || idx}>
                {columns.map((col) => (
                  <td key={col.key} data-label={col.label}>
                    {col.render ? col.render(item[col.key], item) : item[col.key]}
                  </td>
                ))}
                {(permissions.canEdit || permissions.canDelete || item.link || item.pdf_url) && (
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {item.pdf_url && (
                        <button 
                          className="btn-action btn-open-pdf" 
                          onClick={() => window.open(item.pdf_url, '_blank')}
                        >
                          Abrir PDF
                        </button>
                      )}
                      {item.link && (
                        <button 
                          className="btn-action btn-open-link" 
                          onClick={() => window.open(item.link, '_blank')}
                        >
                          Abrir Link
                        </button>
                      )}
                      {permissions.canEdit && (
                        <button className="btn-action btn-edit" onClick={() => onEdit(item)}>Editar</button>
                      )}
                      {permissions.canDelete && (
                        <button className="btn-action btn-delete" onClick={() => onDelete(item[idKey])}>Deletar</button>
                      )}
                    </div>
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
