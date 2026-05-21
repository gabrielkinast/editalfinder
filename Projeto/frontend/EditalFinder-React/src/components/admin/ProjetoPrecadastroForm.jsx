import { useMemo, useState, useRef, useCallback } from 'react';
import {
  buildInitialPrecadastroState,
  savePrecadEnvelope,
  fingerprintPrecadContext,
  loadPrecadEnvelope,
  migratePrecadForm,
} from '../../utils/precadastroProjetoInitialState';
import { logPrecadastro } from '../../utils/precadastro/precadastroLog';
import {
  exportPrecadastroProjetoPdf,
  buildPrecadastroProjetoPdfBlob,
} from '../../services/precadastroProjetoPdf';
import { getClientTheme, themeToCssVars } from '../../utils/precadastro/clientTheme';
import { buildProjectSuggestions } from '../../utils/precadastro/projectIntel';
import {
  buildPreCadastroDraft,
  clearAutoSuggestions,
  markFieldManual,
} from '../../utils/precadastro/buildPreCadastroDraft';
import { calculatePreCadastroCompleteness } from '../../utils/precadastro/calculatePreCadastroCompleteness';
import { hintImpactsForSector, classifySectorKey } from '../../utils/precadastro/preCadastroTemplates';

import PrecadastroHeader from './precadastro/PrecadastroHeader';
import PrecadNavTabs from './precadastro/PrecadNavTabs';
import PrecadCompletionStatus from './precadastro/PrecadCompletionStatus';
import PrecadRecommendationCard from './precadastro/PrecadRecommendationCard';
import PrecadCompanyStrip from './precadastro/PrecadCompanyStrip';
import PrecadProductLines from './precadastro/PrecadProductLines';
import PrecadProjectScope from './precadastro/PrecadProjectScope';
import PrecadFitSection from './precadastro/PrecadFitSection';
import PrecadObservations from './precadastro/PrecadObservations';
import PrecadLegacyFormBody from './precadastro/PrecadLegacyFormBody';
import PrecadIntelToolbar from './precadastro/PrecadIntelToolbar';
import PrecadPendenciasPanel from './precadastro/PrecadPendenciasPanel';
import PrecadImpactHints from './precadastro/PrecadImpactHints';
import PrecadExecutiveSummary from './precadastro/PrecadExecutiveSummary';
import PrecadWorkPlanSection from './precadastro/PrecadWorkPlanSection';
import PrecadBudgetSection from './precadastro/PrecadBudgetSection';
import PrecadDocumentsRisksSection from './precadastro/PrecadDocumentsRisksSection';
import PrecadOpportunitiesConsidered from './precadastro/PrecadOpportunitiesConsidered';
import { calculateClientProfileCompleteness } from '../../utils/cliente/calculateClientProfileCompleteness';

/** Primeira montagem: carrega envelope local ou primeiro rascunho inteligente. */
function iniciarPacoteInteligente(cliente, editalAssociado, radarMatch, initialEnvelope = null) {
  const fp = fingerprintPrecadContext(editalAssociado, '', radarMatch);
  if (initialEnvelope?.form) {
    return {
      form: migratePrecadForm(initialEnvelope.form),
      fieldIntel: initialEnvelope.fieldIntel || {},
      editalFingerprint: fp,
      hadStoredDraft: true,
    };
  }
  const base = buildInitialPrecadastroState(cliente, { edital: editalAssociado, radarMatch });
  const env = loadPrecadEnvelope(cliente?.id_cliente, base, fp);
  if (env.hadStoredDraft) {
    return {
      form: migratePrecadForm(env.form),
      fieldIntel: env.fieldIntel,
      editalFingerprint: fp,
      hadStoredDraft: true,
    };
  }
  const draft = buildPreCadastroDraft({
    cliente,
    edital: editalAssociado,
    radarMatch,
    existingForm: env.form,
    existingFieldIntel: env.fieldIntel,
    options: {},
  });
  return {
    form: migratePrecadForm(draft.mergedForm),
    fieldIntel: draft.mergedFieldIntel,
    editalFingerprint: fp,
    hadStoredDraft: false,
  };
}

const STATUS_LABEL = {
  rascunho: 'Rascunho',
  revisao: 'Em revisão',
  pronto: 'Pronto para exportar',
};

const NAV_FIELD_TARGETS = [
  { id: 'precad-resumo-executivo', label: 'Resumo executivo' },
  { id: 'precad-fit-aderencia', label: 'Aderência' },
  { id: 'precad-contexto-projeto', label: 'Escopo' },
  { id: 'precad-plano-trabalho', label: 'Plano de trabalho' },
  { id: 'precad-orcamento', label: 'Orçamento' },
  { id: 'precad-documentos', label: 'Documentos' },
  { id: 'precad-proximos-passos', label: 'Próximos passos' },
];

export default function ProjetoPrecadastroForm({
  cliente,
  onCancel,
  editalAssociado = null,
  radarMatch = null,
  onDraftSaved = null,
  initialEnvelope = null,
  oportunidadesSelecionadas = null,
  modalSize = 'default',
}) {
  const theme = useMemo(() => getClientTheme(cliente), [cliente]);
  const cssVars = useMemo(() => themeToCssVars(theme), [theme]);

  const packRef = useRef(null);
  if (!packRef.current) {
    packRef.current = iniciarPacoteInteligente(cliente, editalAssociado, radarMatch, initialEnvelope);
  }
  const { editalFingerprint } = packRef.current;

  const [form, setForm] = useState(() => packRef.current.form);
  const [fieldIntel, setFieldIntel] = useState(() => packRef.current.fieldIntel);

  const [tab, setTab] = useState('visao');

  const suggestions = useMemo(
    () => buildProjectSuggestions(cliente, editalAssociado, radarMatch),
    [cliente, editalAssociado, radarMatch],
  );

  const impactHints = useMemo(() => hintImpactsForSector(classifySectorKey(cliente)), [cliente]);
  const completeness = useMemo(() => {
    const c = calculatePreCadastroCompleteness(form);
    logPrecadastro('completeness_calculated', {
      score: c.score,
      status: c.status,
      consultive_count: c.consultivePendencies?.length ?? 0,
    });
    return c;
  }, [form]);

  const clientProfileCompleteness = useMemo(
    () => (cliente ? calculateClientProfileCompleteness(cliente) : null),
    [cliente],
  );

  const empresaSlug = useMemo(
    () =>
      (cliente?.nome_empresa || cliente?.razao_social || `cliente-${cliente?.id_cliente}`)
        .replace(/[^\wÀ-ú\- ]/gi, '_')
        .slice(0, 48),
    [cliente],
  );

  const buildPdfMeta = useCallback(
    (opts = {}) => ({
      empresaNome: cliente?.nome_empresa || empresaSlug,
      arquivoStem: `precadastro-projeto_${empresaSlug}`.slice(0, 80),
      cliente,
      theme,
      edital: editalAssociado,
      radarMatch,
      editalTitulo: form.bloco_estr_edital_ref_titulo || editalAssociado?.titulo,
      sistema: 'EditalFinder',
      ...opts,
    }),
    [cliente, empresaSlug, theme, form, editalAssociado, radarMatch],
  );

  const reaplicarSugestoesInteligentes = useCallback(() => {
    const r = buildPreCadastroDraft({
      cliente,
      edital: editalAssociado,
      radarMatch,
      existingForm: form,
      existingFieldIntel: fieldIntel,
      options: {},
    });
    setForm(r.mergedForm);
    setFieldIntel(r.mergedFieldIntel);
    if (r.report.pendencias.length) console.info('[precad modelo — cadastro incompleto]', r.report.pendencias);
  }, [cliente, editalAssociado, radarMatch, form, fieldIntel]);

  const onChangeTxt = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldIntel((prev) => markFieldManual(prev, name));
  };

  const onChangeChk = (e) => {
    const { name, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: checked }));
    setFieldIntel((prev) => markFieldManual(prev, name));
  };

  const atualizaFontes = useCallback((i, campo, valor) => {
    setForm((prev) => {
      const lista = [...(prev.bloco2_uso_fontes || [])];
      lista[i] = { ...(lista[i] || {}), [campo]: valor };
      return { ...prev, bloco2_uso_fontes: lista };
    });
    setFieldIntel((prev) => markFieldManual(prev, 'bloco2_uso_fontes'));
  }, []);
  const addFonteLinha = () =>
    setForm((prev) => ({
      ...prev,
      bloco2_uso_fontes: [
        ...(prev.bloco2_uso_fontes || []),
        { item: '', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
      ],
    }));
  const rmFonteLinha = (i) =>
    setForm((prev) => ({
      ...prev,
      bloco2_uso_fontes: (prev.bloco2_uso_fontes || []).filter((_, idx) => idx !== i),
    }));

  const atualizaMeta = useCallback((i, campo, valor) => {
    setForm((prev) => {
      const lista = [...(prev.bloco2_metas_fisicas || [])];
      lista[i] = { ...(lista[i] || {}), [campo]: valor };
      return { ...prev, bloco2_metas_fisicas: lista };
    });
    setFieldIntel((prev) => markFieldManual(prev, 'bloco2_metas_fisicas'));
  }, []);
  const addMetaLinha = () =>
    setForm((prev) => ({
      ...prev,
      bloco2_metas_fisicas: [
        ...(prev.bloco2_metas_fisicas || []),
        { meta: '', atividade: '', indicador: '', ini: '', fim: '' },
      ],
    }));
  const rmMetaLinha = (i) =>
    setForm((prev) => ({
      ...prev,
      bloco2_metas_fisicas: (prev.bloco2_metas_fisicas || []).filter((_, idx) => idx !== i),
    }));

  const hadStoredDraft = packRef.current?.hadStoredDraft === true;

  const scrollToPrecadAnchor = (id) => {
    window.requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  };

  const handleSalvarRascunho = () => {
    if (cliente?.id_cliente == null) return;
    savePrecadEnvelope(
      cliente.id_cliente,
      {
        form,
        fieldIntel,
        draftMeta: {
          completenessScore: completeness.score,
          completenessStatus: completeness.status,
          ultimaEdicaoManualEm: new Date().toISOString(),
        },
      },
      editalFingerprint,
    );
    alert('Rascunho (com meta de inteligência) guardado neste navegador.');
    onDraftSaved?.();
  };

  const handlePdf = () => {
    logPrecadastro('pdf_export_start', { id_cliente: cliente?.id_cliente });
    try {
      exportPrecadastroProjetoPdf(form, buildPdfMeta());
      logPrecadastro('pdf_export_success', { id_cliente: cliente?.id_cliente });
    } catch (e) {
      console.error(e);
      logPrecadastro('pdf_export_error', { message: e?.message });
      alert('Falha ao gerar PDF.');
    }
  };

  const handlePreview = () => {
    try {
      const blob = buildPrecadastroProjetoPdfBlob(form, buildPdfMeta({ suppressAlerts: true }));
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank', 'noopener,noreferrer');
      setTimeout(() => URL.revokeObjectURL(url), 120000);
    } catch (e) {
      console.error(e);
      alert('Falha ao abrir pré-visualização.');
    }
  };

  const editalTituloHeader =
    form.bloco_estr_edital_ref_titulo || editalAssociado?.titulo || radarMatch?.tituloEdital || '';

  const aderenciaChip = form.bloco_estr_aderencia_nivel || suggestions.aderenciaNivel;
  const isWorkspaceFull = modalSize === 'workspaceLarge';

  const profileHint =
    clientProfileCompleteness && clientProfileCompleteness.score < 70 ? (
      <p className="precad-client-profile-hint" role="status">
        Perfil do cliente: {clientProfileCompleteness.score}% completo —{' '}
        {clientProfileCompleteness.radarImprovementHint} Completar o cadastro reduz pendências no PDF.
      </p>
    ) : null;

  const intelToolbar = (
    <PrecadIntelToolbar
      defaultOpen={!hadStoredDraft}
      onSmartDraft={() => {
        if (
          window.confirm(
            'Gerar sugestões automáticas usando cadastro, edital e Radar (mantém textos marcados como manuais e só preenche campos ainda vazios)?',
          )
        ) {
          reaplicarSugestoesInteligentes();
        }
      }}
      onFillLacunas={() => reaplicarSugestoesInteligentes()}
      onLimparAutos={() => {
        const cleared = clearAutoSuggestions(form, fieldIntel);
        setForm(cleared.form);
        setFieldIntel(cleared.fieldIntel);
      }}
      onRevisarPendencias={() => {
        setTab('visao');
        scrollToPrecadAnchor('precad-pend-anchor');
      }}
      onScrollProject={() => {
        setTab('escopo');
        scrollToPrecadAnchor('precad-contexto-projeto');
      }}
    />
  );

  return (
    <div
      className={`precad-wrap precad-prof-wrap${
        modalSize === 'large' || isWorkspaceFull ? ' precad-wrap--workspace-large' : ''
      }${isWorkspaceFull ? ' precad-wrap--workspace-full' : ''}`}
      style={cssVars}
    >
      {isWorkspaceFull ? (
        <div className="precad-workspace-top">
          <p className="precad-workspace-flow-hint" role="note">
            Os campos foram preenchidos a partir do perfil do cliente e das oportunidades selecionadas. Revise
            antes de enviar ao cliente.
          </p>
          <PrecadastroHeader
            empresaNome={cliente?.nome_empresa}
            clientId={cliente?.id_cliente}
            editalTitulo={editalTituloHeader}
            aderenciaLabel={aderenciaChip}
            completudePct={completeness.score}
            pendencias={{
              obrigatorias: completeness.requiredMissing.length,
              recomendadas: completeness.recommendedMissing.length,
            }}
            statusLabel={STATUS_LABEL[form.bloco_estr_status_precadastro] || STATUS_LABEL.rascunho}
            logoUrl={theme.logoUrl || undefined}
            onSaveDraft={handleSalvarRascunho}
            onExportPdf={handlePdf}
            onPreviewPdf={handlePreview}
            onClose={onCancel}
          />
          {profileHint}
          <PrecadNavTabs active={tab} onChange={setTab} compact />
        </div>
      ) : (
        <>
          <PrecadastroHeader
            empresaNome={cliente?.nome_empresa}
            clientId={cliente?.id_cliente}
            editalTitulo={editalTituloHeader}
            aderenciaLabel={aderenciaChip}
            completudePct={completeness.score}
            pendencias={{
              obrigatorias: completeness.requiredMissing.length,
              recomendadas: completeness.recommendedMissing.length,
            }}
            statusLabel={STATUS_LABEL[form.bloco_estr_status_precadastro] || STATUS_LABEL.rascunho}
            logoUrl={theme.logoUrl || undefined}
            onSaveDraft={handleSalvarRascunho}
            onExportPdf={handlePdf}
            onPreviewPdf={handlePreview}
            onClose={onCancel}
          />
          {profileHint}
          <PrecadNavTabs active={tab} onChange={setTab} />
        </>
      )}

      <div className="precad-scroll precad-prof-scroll">
        {intelToolbar}
        {tab === 'visao' && (
          <div className="precad-tab-panel">
            <PrecadImpactHints hints={impactHints} />
            <PrecadOpportunitiesConsidered
              form={form}
              oportunidadesSelecionadas={oportunidadesSelecionadas}
            />

            <div className="precad-visao-grid">
              <PrecadCompletionStatus form={form} completeness={completeness} />
              <div className="precad-card precad-status-card">
                <h3 className="precad-card-title">Status do pré-cadastro</h3>
                <select
                  className="precad-select"
                  name="bloco_estr_status_precadastro"
                  value={form.bloco_estr_status_precadastro}
                  onChange={onChangeTxt}
                >
                  <option value="rascunho">Rascunho</option>
                  <option value="revisao">Em revisão</option>
                  <option value="pronto">Pronto para exportar</option>
                </select>
              </div>
              <div id="precad-strip">
                <PrecadCompanyStrip form={form} />
              </div>
            </div>
            <div id="precad-pend-anchor" />
            <PrecadPendenciasPanel
              completeness={completeness}
              fieldTargets={NAV_FIELD_TARGETS}
              onNavigateField={(id) => {
                if (id === 'precad-resumo-executivo') setTab('resumo');
                else if (id === 'precad-fit-aderencia') setTab('aderencia');
                else if (id === 'precad-contexto-projeto' || id === 'precad-plano-trabalho') setTab('escopo');
                else if (id === 'precad-orcamento') setTab('orcamento');
                else if (
                  id === 'precad-documentos' ||
                  id === 'precad-proximos-passos' ||
                  id === 'precad-riscos'
                )
                  setTab('riscos');
                scrollToPrecadAnchor(id);
              }}
            />

            <PrecadRecommendationCard
              suggestions={suggestions}
              form={form}
              fieldIntel={fieldIntel}
              onChangeTxt={onChangeTxt}
              onChangeChk={onChangeChk}
            />
          </div>
        )}

        {tab === 'resumo' && (
          <div className="precad-tab-panel">
            <PrecadExecutiveSummary
              form={form}
              fieldIntel={fieldIntel}
              onChangeTxt={onChangeTxt}
              clienteNome={cliente?.nome_empresa || cliente?.razao_social}
            />
          </div>
        )}

        {tab === 'aderencia' && (
          <div className="precad-tab-panel">
            <PrecadFitSection form={form} fieldIntel={fieldIntel} onChangeTxt={onChangeTxt} />
          </div>
        )}

        {tab === 'escopo' && (
          <div className="precad-tab-panel precad-context-stack">
            <PrecadProjectScope form={form} fieldIntel={fieldIntel} onChangeTxt={onChangeTxt} />
            <PrecadWorkPlanSection
              form={form}
              fieldIntel={fieldIntel}
              onChangeTxt={onChangeTxt}
              onGoCompleto={() => setTab('completo')}
            />
            <div id="precad-linhas-produtos">
              <PrecadProductLines form={form} onChangeChk={onChangeChk} linesMeta={suggestions.linhasMeta} />
            </div>
            <PrecadObservations form={form} onChangeTxt={onChangeTxt} />
          </div>
        )}

        {tab === 'orcamento' && (
          <div className="precad-tab-panel">
            <PrecadBudgetSection
              form={form}
              fieldIntel={fieldIntel}
              onChangeTxt={onChangeTxt}
              onChangeChk={onChangeChk}
            />
          </div>
        )}

        {tab === 'riscos' && (
          <div className="precad-tab-panel">
            <PrecadDocumentsRisksSection form={form} fieldIntel={fieldIntel} onChangeTxt={onChangeTxt} />
          </div>
        )}

        {tab === 'completo' && (
          <div className="precad-tab-panel">
            <p className="precad-muted small precad-complete-intro">
              Formulário técnico completo (estrutura original). Os dados são os mesmos da aba{' '}
              <strong>Contexto e projeto</strong>
              onde houver equivalência — tudo alimenta o mesmo PDF e o mesmo rascunho.
            </p>
            <PrecadLegacyFormBody
              form={form}
              onChangeTxt={onChangeTxt}
              onChangeChk={onChangeChk}
              atualizaFontes={atualizaFontes}
              addFonteLinha={addFonteLinha}
              rmFonteLinha={rmFonteLinha}
              atualizaMeta={atualizaMeta}
              addMetaLinha={addMetaLinha}
              rmMetaLinha={rmMetaLinha}
            />
          </div>
        )}
      </div>

      {!isWorkspaceFull ? (
        <div className="precad-footer precad-footer-prof precad-footer--cadastros">
          <span className="precad-muted small">
            Rascunho salvo localmente neste navegador. Use Salvar rascunho antes de fechar.
          </span>
        </div>
      ) : null}
    </div>
  );
}
