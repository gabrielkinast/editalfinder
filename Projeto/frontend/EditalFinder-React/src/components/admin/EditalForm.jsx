import { useState, useEffect } from 'react';
import { formatCurrency } from '../../utils/formatters';
import { dataService } from '../../services/dataService';
import { classificarEdital } from '../../services/classificationService';
import { loadOrganizationsSafe } from '../../utils/admin/loadOrganizationsSafe';
import {
  buildEditalWritePayload,
  normalizeEditalFormInitialData,
} from '../../utils/admin/buildEditalWritePayload';
import EditalSaveErrorPanel from './EditalSaveErrorPanel.jsx';

const EMPTY_FORM = {
  titulo: '',
  descricao: '',
  objetivo: '',
  temas: '',
  publico_alvo: '',
  fonte_recurso: '',
  valor_maximo: 0,
  data_publicacao: '',
  prazo_envio: '',
  situacao: 'Aberto',
  pdf_url: '',
  link: '',
  status: 'Ativo',
  id_organizacao: '',
  orgao_responsavel: '',
  estado: '',
};

export default function EditalForm({
  initialData,
  onSave,
  onCancel,
  saveError = null,
  onDismissSaveError,
  pendingDraftsCount = 0,
  copyStatus = null,
  onCopyStatusChange,
}) {
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [orgsState, setOrgsState] = useState({
    ok: false,
    organizations: [],
    reason: null,
  });
  const [classificacao, setClassificacao] = useState(null);

  const orgs = orgsState.organizations;
  const orgsAvailable = orgsState.ok && orgs.length > 0;

  const estados = [
    { uf: 'AC', nome: 'Acre' },
    { uf: 'AL', nome: 'Alagoas' },
    { uf: 'AP', nome: 'Amapá' },
    { uf: 'AM', nome: 'Amazonas' },
    { uf: 'BA', nome: 'Bahia' },
    { uf: 'CE', nome: 'Ceará' },
    { uf: 'DF', nome: 'Distrito Federal' },
    { uf: 'ES', nome: 'Espírito Santo' },
    { uf: 'GO', nome: 'Goiás' },
    { uf: 'MA', nome: 'Maranhão' },
    { uf: 'MT', nome: 'Mato Grosso' },
    { uf: 'MS', nome: 'Mato Grosso do Sul' },
    { uf: 'MG', nome: 'Minas Gerais' },
    { uf: 'PA', nome: 'Pará' },
    { uf: 'PB', nome: 'Paraíba' },
    { uf: 'PR', nome: 'Paraná' },
    { uf: 'PE', nome: 'Pernambuco' },
    { uf: 'PI', nome: 'Piauí' },
    { uf: 'RJ', nome: 'Rio de Janeiro' },
    { uf: 'RN', nome: 'Rio Grande do Norte' },
    { uf: 'RS', nome: 'Rio Grande do Sul' },
    { uf: 'RO', nome: 'Rondônia' },
    { uf: 'RR', nome: 'Roraima' },
    { uf: 'SC', nome: 'Santa Catarina' },
    { uf: 'SP', nome: 'São Paulo' },
    { uf: 'SE', nome: 'Sergipe' },
    { uf: 'TO', nome: 'Tocantins' },
    { uf: 'EX', nome: 'Exterior' },
  ];

  useEffect(() => {
    let cancelled = false;
    loadOrganizationsSafe().then((result) => {
      if (!cancelled) setOrgsState(result);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (initialData) {
      setFormData((prev) => ({
        ...prev,
        ...normalizeEditalFormInitialData(initialData),
      }));
    } else {
      setFormData(EMPTY_FORM);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;

    if (name === 'fonte_recurso') {
      const matchedOrg = orgs.find((o) => o.nome.toLowerCase() === value.toLowerCase());
      setFormData((prev) => ({
        ...prev,
        fonte_recurso: value,
        orgao_responsavel: prev.orgao_responsavel || value,
        id_organizacao: matchedOrg ? matchedOrg.id_organizacao : prev.id_organizacao,
      }));
      return;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' || type === 'range' ? parseFloat(value) : value,
    }));
  };

  const handleAutoClassify = () => {
    const resultado = classificarEdital(formData);
    setClassificacao(resultado);

    setFormData((prev) => ({
      ...prev,
      temas: prev.temas || resultado.area.join(', '),
      fonte_recurso: prev.fonte_recurso || resultado.orgao || prev.fonte_recurso,
      orgao_responsavel: prev.orgao_responsavel || resultado.orgao || prev.orgao_responsavel,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(buildEditalWritePayload(formData));
  };

  const handleCopyData = async () => {
    const payload = buildEditalWritePayload(formData);
    const text = JSON.stringify(payload, null, 2);
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        onCopyStatusChange?.('Dados copiados para a área de transferência.');
      } else {
        onCopyStatusChange?.('Clipboard indisponível — copie os campos manualmente.');
      }
    } catch {
      onCopyStatusChange?.('Não foi possível copiar automaticamente.');
    }
  };

  const orgHint =
    orgsState.reason === 'table_not_exposed'
      ? 'Lista de organizações indisponível neste ambiente; use o campo textual acima.'
      : orgsState.reason === 'load_failed'
        ? 'Não foi possível carregar organizações; o cadastro continua sem vínculo.'
        : null;

  return (
    <form onSubmit={handleSubmit} className="modal-form">
      <EditalSaveErrorPanel
        saveError={saveError}
        pendingDraftsCount={pendingDraftsCount}
        onDismiss={onDismissSaveError}
        onCopyData={handleCopyData}
        copyStatus={copyStatus}
      />
      <div className="form-grid">
        <div className="form-section-title">Informações Principais</div>
        <div className="form-group full-width">
          <label>Título do Edital</label>
          <input type="text" name="titulo" value={formData.titulo} onChange={handleChange} required data-testid="edital-form-titulo" />
        </div>
        <div className="form-group full-width">
          <label>Descrição</label>
          <textarea name="descricao" rows="3" value={formData.descricao} onChange={handleChange}></textarea>
        </div>
        <div className="form-group full-width">
          <label>Objetivo</label>
          <textarea name="objetivo" rows="2" value={formData.objetivo} onChange={handleChange}></textarea>
        </div>

        <div className="form-section-title">Detalhes e Classificação</div>

        <div className="form-group full-width" style={{ marginBottom: 0 }}>
          <button
            type="button"
            onClick={handleAutoClassify}
            style={{
              background: 'linear-gradient(135deg, #6c47ff, #a07cff)',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            ✦ Classificar automaticamente
          </button>
        </div>

        {classificacao && (
          <div
            className="form-group full-width"
            style={{
              background: '#f4f1ff',
              border: '1px solid #c9b8ff',
              borderRadius: '10px',
              padding: '12px 16px',
              fontSize: '13px',
              lineHeight: '1.6',
            }}
          >
            <strong>Resultado da classificação</strong>
            <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <span style={{ background: '#6c47ff', color: '#fff', borderRadius: '6px', padding: '2px 10px' }}>
                Tipo: {classificacao.tipo}
              </span>
              {classificacao.orgao && (
                <span style={{ background: '#3b82f6', color: '#fff', borderRadius: '6px', padding: '2px 10px' }}>
                  Órgão: {classificacao.orgao}
                </span>
              )}
              <span style={{ background: '#10b981', color: '#fff', borderRadius: '6px', padding: '2px 10px' }}>
                Confiança: {classificacao.nivel_confianca}%
              </span>
            </div>
            <div style={{ marginTop: '6px', color: '#555' }}>
              <strong>Áreas:</strong> {classificacao.area.join(', ')}
            </div>
            <div style={{ marginTop: '4px', color: '#777', fontStyle: 'italic' }}>
              {classificacao.justificativa}
            </div>
          </div>
        )}
        <div className="form-group">
          <label>Temas</label>
          <input type="text" name="temas" value={formData.temas} onChange={handleChange} placeholder="Ex: IA, Saúde, Sustentabilidade" />
        </div>
        <div className="form-group">
          <label>Público Alvo</label>
          <input type="text" name="publico_alvo" value={formData.publico_alvo} onChange={handleChange} placeholder="Ex: Startups, MEI, Indústrias" />
        </div>
        <div className="form-group">
          <label>Fonte de Recurso</label>
          <input type="text" name="fonte_recurso" value={formData.fonte_recurso} onChange={handleChange} placeholder="Ex: FINEP, BNDES, FAPESP" />
        </div>
        <div className="form-group">
          <label>Valor Máximo: <span>{formatCurrency(formData.valor_maximo)}</span></label>
          <input type="range" name="valor_maximo" min="0" max="50000000" step="100000" value={formData.valor_maximo} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Órgão / organização responsável</label>
          <input
            type="text"
            name="orgao_responsavel"
            value={formData.orgao_responsavel}
            onChange={handleChange}
            placeholder="Ex: FINEP, BNDES, universidade emissora"
          />
        </div>
        {orgsAvailable ? (
          <div className="form-group">
            <label>Vincular organização (opcional)</label>
            <select name="id_organizacao" value={formData.id_organizacao} onChange={handleChange}>
              <option value="">Nenhuma</option>
              {orgs.map((org) => (
                <option key={org.id_organizacao} value={org.id_organizacao}>
                  {org.nome}
                </option>
              ))}
            </select>
          </div>
        ) : null}
        {orgHint ? (
          <div className="form-group full-width">
            <p className="form-hint" style={{ margin: 0, fontSize: '12px', color: '#666' }}>
              {orgHint}
            </p>
          </div>
        ) : null}
        <div className="form-group">
          <label>Estado (UF)</label>
          <select name="estado" value={formData.estado} onChange={handleChange}>
            <option value="">Selecione o estado...</option>
            {estados.map((est) => (
              <option key={est.uf} value={est.nome}>
                {est.nome}
              </option>
            ))}
          </select>
        </div>

        <div className="form-section-title">Datas e Links</div>
        <div className="form-group">
          <label>Data de Publicação</label>
          <input type="date" name="data_publicacao" value={formData.data_publicacao} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Prazo de Envio</label>
          <input type="date" name="prazo_envio" value={formData.prazo_envio} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Situação</label>
          <select name="situacao" value={formData.situacao} onChange={handleChange}>
            <option value="Aberto">Aberto</option>
            <option value="Em análise">Em análise</option>
            <option value="Encerrado">Encerrado</option>
            <option value="Suspenso">Suspenso</option>
          </select>
        </div>
        <div className="form-group">
          <label>Status</label>
          <select name="status" value={formData.status} onChange={handleChange} required>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>
        <div className="form-group full-width">
          <label>URL do PDF</label>
          <input type="url" name="pdf_url" value={formData.pdf_url} onChange={handleChange} placeholder="https://exemplo.com/edital.pdf" />
        </div>
        <div className="form-group full-width">
          <label>Link do Edital</label>
          <input type="url" name="link" value={formData.link} onChange={handleChange} placeholder="https://exemplo.com/pagina-edital" required data-testid="edital-form-link" />
        </div>
      </div>

      <div className="modal-actions">
        <button
          type="button"
          className="btn-cancel"
          onClick={onCancel}
          data-testid="edital-form-cancel"
        >
          Cancelar
        </button>
        <button type="submit" className="btn-save" data-testid="edital-form-submit">
          Salvar Edital
        </button>
      </div>
    </form>
  );
}
