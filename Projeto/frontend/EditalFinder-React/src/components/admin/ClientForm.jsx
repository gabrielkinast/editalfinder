import { useState, useEffect, useMemo, useCallback } from 'react';
import {
  CLIENT_FORM_DEFAULT_STATE,
  TIPOS_RECURSO_FOMENTO,
  clientFormStateFromCliente,
} from '../../utils/cliente/clientePerfilConsultivo';
import { calculateClientProfileCompleteness } from '../../utils/cliente/calculateClientProfileCompleteness';
import { logClienteProfile } from '../../utils/clienteProfileLog';
import { normalizeClienteRow } from '../../utils/normalizeCliente';

const TABS = [
  { id: 'basicos', label: 'Básicos' },
  { id: 'contato', label: 'Contato' },
  { id: 'local', label: 'Localização' },
  { id: 'economico', label: 'Econômicos' },
  { id: 'tecnico', label: 'Inovação' },
  { id: 'fomento', label: 'Fomento' },
  { id: 'docs', label: 'Documentos' },
  { id: 'diag', label: 'Consultor' },
];

const CONSULTOR_PLACEHOLDERS = {
  diagnostico_inicial:
    'Descreva a situação atual do cliente, prioridades, dores, oportunidades e hipóteses de fomento.',
  pontos_fortes: 'Capacidades, diferenciais, histórico de projetos e ativos relevantes.',
  lacunas: 'Informações ou capacidades que ainda precisam ser levantadas.',
  riscos: 'Riscos de elegibilidade, prazo, contrapartida ou execução.',
  proximas_acoes: 'Próximos passos acordados com o cliente (reuniões, documentos, editais).',
  observacoes_internas: 'Notas internas do consultor (não exibidas ao cliente).',
};

function TriSelect({ value, onChange, id }) {
  return (
    <select
      id={id}
      className="precad-select"
      value={value === true ? 'sim' : value === false ? 'nao' : ''}
      onChange={(e) => {
        const v = e.target.value;
        onChange(v === 'sim' ? true : v === 'nao' ? false : null);
      }}
    >
      <option value="">Não informado</option>
      <option value="sim">Sim</option>
      <option value="nao">Não</option>
    </select>
  );
}

function Field({ label, children, hint, full = false }) {
  return (
    <div className={`form-group client-form-field ${full ? 'client-form-field--full' : ''}`}>
      <label>{label}</label>
      {children}
      {hint ? <p className="client-form-hint">{hint}</p> : null}
    </div>
  );
}

function TextArea({ size = 'md', className = '', ...props }) {
  const sizeClass =
    size === 'xl'
      ? 'client-form-textarea--xl'
      : size === 'lg'
        ? 'client-form-textarea--lg'
        : size === 'sm'
          ? 'client-form-textarea--sm'
          : '';
  return (
    <textarea
      className={`client-form-textarea ${sizeClass} ${className}`.trim()}
      {...props}
    />
  );
}

function CompletenessBlock({ completeness, compact = false }) {
  const { score, level, recommendedMissing, radarImprovementHint } = completeness;
  const hintText =
    score < 60
      ? 'Faltam dados para melhorar pré-projetos e recomendações.'
      : radarImprovementHint;

  return (
    <div
      className={`client-form-completeness ${compact ? 'client-form-completeness--compact' : ''}`}
      role="status"
    >
      <div className="client-form-completeness-row">
        <span className={`client-form-badge client-form-badge--${level}`}>
          Perfil {score}% completo
        </span>
        <div
          className="client-form-progress"
          role="progressbar"
          aria-valuenow={score}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Perfil ${score}% completo`}
        >
          <div className="client-form-progress-fill" style={{ width: `${score}%` }} />
        </div>
      </div>
      {compact ? (
        <>
          {score < 60 ? <p className="client-form-completeness-hint">{hintText}</p> : null}
          {recommendedMissing.length > 0 ? (
            <details className="client-form-recommended-details">
              <summary>Ver campos recomendados</summary>
              <p className="client-form-recommended">{recommendedMissing.join(' · ')}</p>
            </details>
          ) : null}
        </>
      ) : (
        <>
          <p className="client-form-completeness-hint">{hintText}</p>
          {recommendedMissing.length > 0 ? (
            <details className="client-form-recommended-details">
              <summary>Ver campos recomendados</summary>
              <p className="client-form-recommended">{recommendedMissing.join(' · ')}</p>
            </details>
          ) : null}
        </>
      )}
    </div>
  );
}

export default function ClientForm({
  initialData,
  onSave,
  onCancel,
  variant = 'default',
  title,
}) {
  const [formData, setFormData] = useState(CLIENT_FORM_DEFAULT_STATE);
  const [activeTab, setActiveTab] = useState('basicos');

  const isWorkspaceLarge =
    variant === 'workspaceLarge' || variant === 'workspace';

  useEffect(() => {
    if (initialData) {
      setFormData(clientFormStateFromCliente(normalizeClienteRow(initialData)));
    } else {
      setFormData(CLIENT_FORM_DEFAULT_STATE);
    }
    setActiveTab('basicos');
    logClienteProfile('form_open', { editing: !!initialData, variant });
  }, [initialData, variant]);

  const completeness = useMemo(() => {
    const norm = normalizeClienteRow({
      ...formData,
      extras: { perfil_consultivo: formData.perfil },
    });
    const c = calculateClientProfileCompleteness(norm);
    logClienteProfile('completeness_calculated', {
      score: c.score,
      missing_recommended: c.recommendedMissing,
    });
    return c;
  }, [formData]);

  const setTop = useCallback((name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }, []);

  const setPerfil = useCallback((section, field, value) => {
    setFormData((prev) => ({
      ...prev,
      perfil: {
        ...prev.perfil,
        [section]: {
          ...prev.perfil[section],
          [field]: value,
        },
      },
    }));
  }, []);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    if (type === 'number') {
      const optionalNumeric = ['faturamento_anual', 'numero_funcionarios'];
      if (optionalNumeric.includes(name)) {
        setTop(name, value === '' ? '' : Number(value));
      } else {
        setTop(name, value === '' ? 0 : Number(value));
      }
      return;
    }
    setTop(name, value);
  };

  const toggleTipoRecurso = (id) => {
    setFormData((prev) => {
      const cur = prev.perfil?.preferencias_fomento?.tipos_recurso || [];
      const next = cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id];
      return {
        ...prev,
        perfil: {
          ...prev.perfil,
          preferencias_fomento: {
            ...prev.perfil.preferencias_fomento,
            tipos_recurso: next,
          },
        },
      };
    });
  };

  const handleTab = (id) => {
    setActiveTab(id);
    logClienteProfile('form_section_change', { section: id });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!completeness.canSaveMinimal) {
      alert('Informe pelo menos o nome fantasia ou a razão social.');
      return;
    }
    logClienteProfile('save_start', { score: completeness.score });
    try {
      onSave(formData);
      logClienteProfile('save_success', { score: completeness.score });
    } catch (err) {
      logClienteProfile('save_error', { message: err?.message });
      throw err;
    }
  };

  const p = formData.perfil || CLIENT_FORM_DEFAULT_STATE.perfil;
  const diag = p.diagnostico_consultor || {};

  const tabsNav = (
    <nav className="client-form-tabs" aria-label="Seções do cadastro">
      {TABS.map((t) => (
        <button
          key={t.id}
          type="button"
          className={`client-form-tab ${activeTab === t.id ? 'client-form-tab--active' : ''}`}
          onClick={() => handleTab(t.id)}
        >
          {t.label}
        </button>
      ))}
    </nav>
  );

  const panelContent = (
    <div className="client-form-panel">
      {activeTab === 'basicos' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Dados básicos</h3>
          <div className="client-form-grid-2">
            <Field label="Nome fantasia *" full>
              <input type="text" name="nome_empresa" value={formData.nome_empresa} onChange={handleChange} required />
            </Field>
            <Field label="Razão social" full>
              <input type="text" name="razao_social" value={formData.razao_social || ''} onChange={handleChange} />
            </Field>
            <Field label="CNPJ">
              <input type="text" name="cnpj" value={formData.cnpj || ''} onChange={handleChange} placeholder="00.000.000/0000-00" />
            </Field>
            <Field label="Setor principal">
              <input type="text" name="setor" value={formData.setor || ''} onChange={handleChange} />
            </Field>
            <Field label="Porte">
              <select name="porte_empresa" value={formData.porte_empresa} onChange={handleChange}>
                <option value="MEI">MEI</option>
                <option value="ME">ME</option>
                <option value="EPP">EPP</option>
                <option value="Média">Média</option>
                <option value="Grande">Grande</option>
              </select>
            </Field>
            <Field label="Status">
              <select name="status" value={formData.status} onChange={handleChange}>
                <option value="Ativo">Ativo</option>
                <option value="Inativo">Inativo</option>
              </select>
            </Field>
            <Field label="Site" full>
              <input type="url" name="site" value={formData.site || ''} onChange={handleChange} placeholder="https://..." />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'contato' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Contato principal</h3>
          <div className="client-form-grid-2">
            <Field label="Nome do responsável" full>
              <input
                type="text"
                value={p.contato.nome}
                onChange={(e) => setPerfil('contato', 'nome', e.target.value)}
              />
            </Field>
            <Field label="Cargo">
              <input
                type="text"
                value={p.contato.cargo}
                onChange={(e) => setPerfil('contato', 'cargo', e.target.value)}
              />
            </Field>
            <Field label="CPF">
              <input
                type="text"
                value={p.contato.cpf}
                onChange={(e) => setPerfil('contato', 'cpf', e.target.value)}
              />
            </Field>
            <Field label="E-mail">
              <input
                type="email"
                value={p.contato.email}
                onChange={(e) => setPerfil('contato', 'email', e.target.value)}
              />
            </Field>
            <Field label="Telefone">
              <input
                type="tel"
                value={p.contato.telefone}
                onChange={(e) => setPerfil('contato', 'telefone', e.target.value)}
              />
            </Field>
            <Field label="Observações de contato" full>
              <TextArea
                size="lg"
                value={p.contato.observacoes}
                onChange={(e) => setPerfil('contato', 'observacoes', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'local' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Localização e operação</h3>
          <div className="client-form-grid-2">
            <Field label="País">
              <input
                type="text"
                value={p.localizacao.pais}
                onChange={(e) => setPerfil('localizacao', 'pais', e.target.value)}
              />
            </Field>
            <Field label="Região de atuação">
              <input type="text" name="regiao" value={formData.regiao || ''} onChange={handleChange} placeholder="Ex.: Sudeste" />
            </Field>
            <Field label="Estado (UF)">
              <input type="text" name="estado" value={formData.estado || ''} onChange={handleChange} maxLength={2} />
            </Field>
            <Field label="Cidade">
              <input type="text" name="cidade" value={formData.cidade || ''} onChange={handleChange} />
            </Field>
            <Field label="Unidade de execução do projeto" full>
              <input
                type="text"
                value={p.localizacao.unidade_execucao}
                onChange={(e) => setPerfil('localizacao', 'unidade_execucao', e.target.value)}
              />
            </Field>
            <Field label="Data de constituição">
              <input type="date" name="data_abertura" value={formData.data_abertura || ''} onChange={handleChange} />
            </Field>
            <Field label="Início de operação">
              <input
                type="date"
                value={p.localizacao.data_inicio_operacao}
                onChange={(e) => setPerfil('localizacao', 'data_inicio_operacao', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'economico' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Dados econômicos</h3>
          <div className="client-form-grid-2">
            <Field label="CNAE principal" full>
              <input type="text" name="cnae_principal" value={formData.cnae_principal || ''} onChange={handleChange} />
            </Field>
            <Field label="Receita operacional anual (R$)">
              <input
                type="number"
                name="faturamento_anual"
                min={0}
                value={formData.faturamento_anual === '' ? '' : formData.faturamento_anual}
                onChange={handleChange}
              />
            </Field>
            <Field label="EBITDA">
              <input
                type="text"
                value={p.dados_economicos.ebitda}
                onChange={(e) => setPerfil('dados_economicos', 'ebitda', e.target.value)}
              />
            </Field>
            <Field label="Número de empregados">
              <input
                type="number"
                name="numero_funcionarios"
                min={0}
                value={formData.numero_funcionarios === '' ? '' : formData.numero_funcionarios}
                onChange={handleChange}
              />
            </Field>
            <Field label="Grupo econômico">
              <input
                type="text"
                value={p.dados_economicos.grupo_economico}
                onChange={(e) => setPerfil('dados_economicos', 'grupo_economico', e.target.value)}
              />
            </Field>
            <Field label="Faixa de faturamento (texto)" full>
              <input
                type="text"
                value={p.dados_economicos.faixa_faturamento}
                onChange={(e) => setPerfil('dados_economicos', 'faixa_faturamento', e.target.value)}
              />
            </Field>
            <Field label="Capacidade de contrapartida" full>
              <TextArea
                size="md"
                value={p.dados_economicos.contrapartida_capacidade}
                onChange={(e) => setPerfil('dados_economicos', 'contrapartida_capacidade', e.target.value)}
              />
            </Field>
            <Field label="Valor de interesse mín. (R$)">
              <input type="number" name="interesse_valor_min" min={0} value={formData.interesse_valor_min} onChange={handleChange} />
            </Field>
            <Field label="Valor de interesse máx. (R$)">
              <input type="number" name="interesse_valor_max" min={0} value={formData.interesse_valor_max} onChange={handleChange} />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'tecnico' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Perfil tecnológico e inovação</h3>
          <div className="client-form-stack">
            <Field label="Principais atividades / descrição do projeto">
              <TextArea
                size="lg"
                name="descricao_projeto"
                value={formData.descricao_projeto || ''}
                onChange={handleChange}
                placeholder="Descreva o que a empresa faz e o foco de inovação."
              />
            </Field>
            <div className="client-form-grid-2">
              <Field label="Áreas tecnológicas">
                <input type="text" name="area_inovacao" value={formData.area_inovacao || ''} onChange={handleChange} />
              </Field>
              <Field label="Temas de interesse">
                <input type="text" name="interesse_temas" value={formData.interesse_temas || ''} onChange={handleChange} />
              </Field>
              <Field label="Setores estratégicos">
                <input
                  type="text"
                  value={p.perfil_tecnologico.setores_estrategicos}
                  onChange={(e) => setPerfil('perfil_tecnologico', 'setores_estrategicos', e.target.value)}
                />
              </Field>
              <Field label="Maturidade tecnológica">
                <input
                  type="text"
                  value={p.perfil_tecnologico.maturidade_tecnologica}
                  onChange={(e) => setPerfil('perfil_tecnologico', 'maturidade_tecnologica', e.target.value)}
                />
              </Field>
            </div>
            <Field label="Experiência anterior com P&D">
              <TextArea
                size="lg"
                value={p.perfil_tecnologico.experiencia_pd}
                onChange={(e) => setPerfil('perfil_tecnologico', 'experiencia_pd', e.target.value)}
              />
            </Field>
            <Field label="Parcerias com ICTs / laboratórios">
              <TextArea
                size="lg"
                value={p.perfil_tecnologico.parcerias_ict}
                onChange={(e) => setPerfil('perfil_tecnologico', 'parcerias_ict', e.target.value)}
              />
            </Field>
            <Field label="Portfólio / produtos principais">
              <TextArea
                size="lg"
                value={p.perfil_tecnologico.portfolio_produtos}
                onChange={(e) => setPerfil('perfil_tecnologico', 'portfolio_produtos', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'fomento' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Preferências de fomento</h3>
          <fieldset className="client-form-checkgroup">
            <legend>Tipo de recurso desejado</legend>
            {TIPOS_RECURSO_FOMENTO.map((t) => (
              <label key={t.id} className="client-form-check">
                <input
                  type="checkbox"
                  checked={(p.preferencias_fomento.tipos_recurso || []).includes(t.id)}
                  onChange={() => toggleTipoRecurso(t.id)}
                />
                {t.label}
              </label>
            ))}
          </fieldset>
          <div className="client-form-grid-2">
            <Field label="Aceita oportunidades internacionais?">
              <TriSelect
                value={p.preferencias_fomento.aceita_internacional}
                onChange={(v) => setPerfil('preferencias_fomento', 'aceita_internacional', v)}
              />
            </Field>
            <Field label="Aceita licitações?">
              <TriSelect
                value={p.preferencias_fomento.aceita_licitacao}
                onChange={(v) => setPerfil('preferencias_fomento', 'aceita_licitacao', v)}
              />
            </Field>
            <Field label="Aceita chamadas sem prazo definido?">
              <TriSelect
                value={p.preferencias_fomento.aceita_sem_prazo}
                onChange={(v) => setPerfil('preferencias_fomento', 'aceita_sem_prazo', v)}
              />
            </Field>
            <Field label="Prazo mínimo confortável (dias)">
              <input
                type="number"
                min={0}
                value={p.preferencias_fomento.prazo_minimo_confortavel_dias}
                onChange={(e) =>
                  setPerfil('preferencias_fomento', 'prazo_minimo_confortavel_dias', e.target.value)
                }
              />
            </Field>
            <Field label="Fontes preferidas" full>
              <TextArea
                size="md"
                value={p.preferencias_fomento.fontes_preferidas}
                onChange={(e) => setPerfil('preferencias_fomento', 'fontes_preferidas', e.target.value)}
              />
            </Field>
            <Field label="Fontes a evitar" full>
              <TextArea
                size="md"
                value={p.preferencias_fomento.fontes_evitar}
                onChange={(e) => setPerfil('preferencias_fomento', 'fontes_evitar', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'docs' && (
        <div className="client-form-section">
          <h3 className="client-form-section-title">Documentação e regularidade</h3>
          <div className="client-form-grid-2">
            {[
              ['contrato_social', 'Contrato social disponível?'],
              ['certidoes_fiscais', 'Certidões fiscais disponíveis?'],
              ['regularidade_trabalhista', 'Regularidade trabalhista?'],
              ['balanco_dre', 'Balanço/DRE disponíveis?'],
              ['representante_legal', 'Representante legal definido?'],
              ['documentos_tecnicos', 'Documentos técnicos disponíveis?'],
            ].map(([key, lab]) => (
              <Field key={key} label={lab}>
                <TriSelect
                  value={p.documentacao[key]}
                  onChange={(v) => setPerfil('documentacao', key, v)}
                  id={key}
                />
              </Field>
            ))}
            <Field label="Observações documentais" full>
              <TextArea
                size="md"
                value={p.documentacao.observacoes}
                onChange={(e) => setPerfil('documentacao', 'observacoes', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}

      {activeTab === 'diag' && (
        <div className="client-form-section client-form-section--consultor">
          <h3 className="client-form-section-title">Análise do consultor</h3>
          <p className="client-form-section-lead">
            Use esta aba para registrar diagnóstico, riscos e próximos passos — esses dados enriquecem pré-projetos e o PDF.
          </p>
          <div className="client-form-stack client-form-consultor-cards">
            <Field label="Diagnóstico inicial">
              <TextArea
                size="xl"
                value={diag.diagnostico_inicial || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.diagnostico_inicial}
                onChange={(e) => setPerfil('diagnostico_consultor', 'diagnostico_inicial', e.target.value)}
              />
            </Field>
            <Field label="Pontos fortes do cliente">
              <TextArea
                size="lg"
                value={diag.pontos_fortes || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.pontos_fortes}
                onChange={(e) => setPerfil('diagnostico_consultor', 'pontos_fortes', e.target.value)}
              />
            </Field>
            <Field label="Lacunas">
              <TextArea
                size="lg"
                value={diag.lacunas || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.lacunas}
                onChange={(e) => setPerfil('diagnostico_consultor', 'lacunas', e.target.value)}
              />
            </Field>
            <Field label="Riscos">
              <TextArea
                size="lg"
                value={diag.riscos || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.riscos}
                onChange={(e) => setPerfil('diagnostico_consultor', 'riscos', e.target.value)}
              />
            </Field>
            <Field label="Próximas ações">
              <TextArea
                size="lg"
                value={diag.proximas_acoes || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.proximas_acoes}
                onChange={(e) => setPerfil('diagnostico_consultor', 'proximas_acoes', e.target.value)}
              />
            </Field>
            <Field label="Observações internas">
              <TextArea
                size="lg"
                value={diag.observacoes_internas || ''}
                placeholder={CONSULTOR_PLACEHOLDERS.observacoes_internas}
                onChange={(e) => setPerfil('diagnostico_consultor', 'observacoes_internas', e.target.value)}
              />
            </Field>
          </div>
        </div>
      )}
    </div>
  );

  const footerActions = (
    <>
      <p className="client-form-save-note">
        Campos mínimos: nome fantasia ou razão social. Demais seções são recomendadas e melhoram pré-projetos e PDF.
      </p>
      <div className="client-form-footer-actions">
        <button type="button" className="btn-cancel" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="btn-save">
          Salvar cliente
        </button>
      </div>
    </>
  );

  if (isWorkspaceLarge) {
    return (
      <form
        onSubmit={handleSubmit}
        className="modal-form client-form-prof client-form-prof--workspace-large"
      >
        <header className="client-form-header">
          <div className="client-form-header-main">
            {title ? <h2 className="client-form-title">{title}</h2> : null}
            <CompletenessBlock completeness={completeness} compact />
          </div>
          <button
            type="button"
            className="client-form-close-btn"
            onClick={onCancel}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>
        {tabsNav}
        <div className="client-form-body">{panelContent}</div>
        <footer className="client-form-footer">{footerActions}</footer>
      </form>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="modal-form client-form-prof">
      <CompletenessBlock completeness={completeness} />
      {tabsNav}
      {panelContent}
      <div className="client-form-footer client-form-footer--inline">{footerActions}</div>
    </form>
  );
}
