import { useMemo, useState } from 'react';
import ConsultorClientStatusBadge from './ConsultorClientStatusBadge';
import { CLIENT_STATUS_FILTER_OPTIONS } from '../../utils/consultor/deriveConsultorClientStatus';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';

const MAX_TAGS_VISIBLE = 3;

function rowKey(c, idx) {
  const v = c?.id_cliente ?? c?.id;
  return v !== undefined && v !== null ? String(v) : `idx-${idx}`;
}

function textoCurto(val, max = 22) {
  if (val == null || val === '') return null;
  const s =
    typeof val === 'string'
      ? val
      : Array.isArray(val)
        ? val.map(String).join(', ')
        : String(val);
  const t = s.trim();
  if (!t) return null;
  return t.length > max ? `${t.slice(0, max)}…` : t;
}

function norm(s) {
  return String(s ?? '')
    .trim()
    .toLowerCase();
}

function buildClienteTags(c) {
  const tags = [];
  if (c.porte_empresa) tags.push({ key: 'porte', label: String(c.porte_empresa), title: c.porte_empresa });
  if (c.estado) tags.push({ key: 'uf', label: String(c.estado), title: c.estado });
  const setorTxt = textoCurto(c.setor, 20);
  if (setorTxt) tags.push({ key: 'setor', label: setorTxt, title: c.setor });
  const interesseTxt = textoCurto(c.interesse_temas, 28);
  if (interesseTxt) {
    tags.push({
      key: 'interesse',
      label: interesseTxt,
      title: c.interesse_temas,
      className: 'consultor-tag-interesse',
    });
  }
  return tags;
}

/**
 * Lista lateral de clientes no Workspace (busca, filtros, novo/editar).
 */
export default function ConsultorClienteList({
  clientes,
  clienteIdSelecionado = null,
  onSelecionar,
  loading,
  error,
  onNovoCliente,
  onEditarCliente,
  canCreate = false,
  canEdit = false,
  clienteSelecionado = null,
  getClientStatus,
}) {
  const [busca, setBusca] = useState('');
  const [filtroPorte, setFiltroPorte] = useState('');
  const [filtroSetor, setFiltroSetor] = useState('');
  const [filtroStatus, setFiltroStatus] = useState('');

  const portes = useMemo(() => {
    const s = new Set();
    clientes.forEach((c) => {
      if (c.porte_empresa) s.add(String(c.porte_empresa));
    });
    return [...s].sort();
  }, [clientes]);

  const setores = useMemo(() => {
    const s = new Set();
    clientes.forEach((c) => {
      if (c.setor) s.add(String(c.setor));
    });
    return [...s].sort();
  }, [clientes]);

  const filtrados = useMemo(() => {
    const q = norm(busca);
    return clientes.filter((c) => {
      if (filtroPorte && String(c.porte_empresa || '') !== filtroPorte) return false;
      if (filtroSetor && String(c.setor || '') !== filtroSetor) return false;
      if (filtroStatus && getClientStatus) {
        const st = getClientStatus(c);
        if (st?.key !== filtroStatus) return false;
      }
      if (!q) return true;
      const hay = norm(`${c.nome_empresa} ${c.razao_social} ${c.cnpj}`);
      return hay.includes(q);
    });
  }, [clientes, busca, filtroPorte, filtroSetor, filtroStatus, getClientStatus]);

  if (loading) {
    return (
      <div className="radar-clientes-panel consultor-clientes-panel">
        <div className="radar-panel-header">
          <h2 className="radar-panel-title">Clientes</h2>
        </div>
        <div className="radar-empty">Carregando clientes…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="radar-clientes-panel consultor-clientes-panel">
        <div className="radar-panel-header">
          <h2 className="radar-panel-title">Clientes</h2>
        </div>
        <div className="consultor-panel-error" role="alert">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="radar-clientes-panel consultor-clientes-panel">
      <div className="radar-panel-header consultor-clientes-panel-head">
        <h2 className="radar-panel-title">Clientes</h2>
        <span className="radar-count-badge">{filtrados.length}</span>
      </div>

      {canCreate || canEdit ? (
        <div className={`consultor-client-actions ${!canCreate ? 'consultor-client-actions--single' : ''}`}>
          {canCreate ? (
            <button type="button" className="consultor-btn-novo-cliente" onClick={onNovoCliente}>
              + Novo cliente
            </button>
          ) : null}
          {canEdit ? (
            <button
              type="button"
              className="consultor-btn-editar-cliente"
              disabled={!clienteSelecionado}
              onClick={() => clienteSelecionado && onEditarCliente?.(clienteSelecionado)}
            >
              Editar
            </button>
          ) : null}
        </div>
      ) : null}

      <label className="consultor-clientes-search">
        <span className="sr-only">Buscar cliente</span>
        <input
          type="search"
          className="filter-input-large"
          placeholder="Nome ou CNPJ…"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          autoComplete="off"
        />
      </label>

      <div className="consultor-clientes-filters">
        <select
          className="precad-select consultor-filter-select"
          value={filtroStatus}
          onChange={(e) => {
            const v = e.target.value;
            setFiltroStatus(v);
            logConsultorWorkspace('client_status_filter_change', { status: v || 'all' });
          }}
          aria-label="Filtrar por status"
        >
          {CLIENT_STATUS_FILTER_OPTIONS.map((opt) => (
            <option key={opt.value || 'all'} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {portes.length > 1 ? (
          <select
            className="precad-select consultor-filter-select"
            value={filtroPorte}
            onChange={(e) => setFiltroPorte(e.target.value)}
            aria-label="Filtrar por porte"
          >
            <option value="">Porte (todos)</option>
            {portes.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        ) : null}
        {setores.length > 1 ? (
          <select
            className="precad-select consultor-filter-select"
            value={filtroSetor}
            onChange={(e) => setFiltroSetor(e.target.value)}
            aria-label="Filtrar por setor"
          >
            <option value="">Setor (todos)</option>
            {setores.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        ) : null}
      </div>

      {clientes.length === 0 ? (
        <div className="radar-empty">
          Nenhum cliente ativo. {canCreate ? 'Use “Novo cliente” para começar.' : 'Peça acesso ao administrador.'}
        </div>
      ) : filtrados.length === 0 ? (
        <div className="radar-empty">Nenhum cliente corresponde à busca.</div>
      ) : (
        <ul className="radar-clientes-lista consultor-clientes-lista">
          {filtrados.map((c, idx) => {
            const key = rowKey(c, idx);
            const ativo =
              clienteIdSelecionado != null && String(clienteIdSelecionado) === String(key);
            const allTags = buildClienteTags(c);
            const visibleTags = allTags.slice(0, MAX_TAGS_VISIBLE);
            const extraCount = allTags.length - visibleTags.length;
            const extraTitles = allTags.slice(MAX_TAGS_VISIBLE).map((t) => t.title || t.label);
            const clientStatus = getClientStatus?.(c) ?? null;

            return (
              <li key={key} className="radar-cliente-li">
                <div
                  role="button"
                  tabIndex={0}
                  className={`radar-cliente-item consultor-cliente-item ${ativo ? 'ativo' : ''}`}
                  onClick={() => onSelecionar?.(c, idx)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelecionar?.(c, idx);
                    }
                  }}
                >
                  <div className="radar-cliente-nome-row consultor-cliente-nome-row">
                    <span className="radar-cliente-nome" title={c.nome_empresa}>
                      {c.nome_empresa || 'Sem nome'}
                    </span>
                    {clientStatus ? (
                      <ConsultorClientStatusBadge
                        status={clientStatus}
                        className="consultor-client-status-badge--list"
                      />
                    ) : null}
                  </div>
                  <div className="radar-cliente-meta consultor-cliente-tags">
                    {visibleTags.map((tag) => (
                      <span
                        key={tag.key}
                        className={`radar-tag ${tag.className || ''}`}
                        title={tag.title}
                      >
                        {tag.label}
                      </span>
                    ))}
                    {extraCount > 0 ? (
                      <span
                        className="radar-tag consultor-tag-more"
                        title={extraTitles.join(' · ')}
                      >
                        +{extraCount}
                      </span>
                    ) : null}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
