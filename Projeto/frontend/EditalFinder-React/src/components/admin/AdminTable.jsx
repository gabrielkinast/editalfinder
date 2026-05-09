import { usePermissions } from '../../hooks/usePermissions';

function formatCell(raw) {
  if (raw == null || raw === '') return '—';
  const t = typeof raw;
  if (t === 'string' || t === 'number' || t === 'boolean') return String(raw);
  if (t === 'bigint') return raw.toString();
  if (t === 'object') {
    if (Array.isArray(raw)) return raw.length ? raw.join(', ') : '—';
    try {
      const s = JSON.stringify(raw);
      return s.length > 80 ? `${s.slice(0, 77)}…` : s;
    } catch {
      return '—';
    }
  }
  return '—';
}

/** @param {(item: object) => import('react').ReactNode | null} [extraRowActions] */
export default function AdminTable({ columns, data, onEdit, onDelete, extraRowActions }) {
  const permissions = usePermissions();
  
  // A primeira coluna é SEMPRE o ID nas tabelas de cadastro
  const idKey = columns[0]?.key;

  const showsActionsColumn =
    permissions.canEdit ||
    permissions.canDelete ||
    typeof extraRowActions === 'function' ||
    data.some((item) => {
      const link = typeof item.link === 'string' && item.link.trim().length > 0;
      const pdf = typeof item.pdf_url === 'string' && item.pdf_url.trim().length > 0;
      return link || pdf;
    });

  const rowNeedsExternalActions = (item) => {
    if (!item || typeof item !== 'object') return false;
    const link = typeof item.link === 'string' && item.link.trim().length > 0;
    const pdf = typeof item.pdf_url === 'string' && item.pdf_url.trim().length > 0;
    return link || pdf;
  };

  return (
    <div className="table-container">
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((col) => <th key={col.key}>{col.label}</th>)}
            {showsActionsColumn && <th>Ações</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (showsActionsColumn ? 1 : 0)} style={{ textAlign: 'center', padding: '20px' }}>
                Nenhum item encontrado.
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr key={item[idKey] || idx}>
                {columns.map((col) => (
                  <td key={col.key} data-label={col.label}>
                    {col.render
                      ? col.render(item[col.key], item)
                      : formatCell(item[col.key])}
                  </td>
                ))}
                {(permissions.canEdit ||
                  permissions.canDelete ||
                  typeof extraRowActions === 'function' ||
                  rowNeedsExternalActions(item)) && (
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {typeof extraRowActions === 'function' ? extraRowActions(item) : null}
                      {typeof item.pdf_url === 'string' && item.pdf_url.trim() && (
                        <button 
                          className="btn-action btn-open-pdf" 
                          onClick={() => window.open(item.pdf_url, '_blank')}
                        >
                          Abrir PDF
                        </button>
                      )}
                      {typeof item.link === 'string' && item.link.trim() && (
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
