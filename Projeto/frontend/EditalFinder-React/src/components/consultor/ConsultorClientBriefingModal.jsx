import { useCallback, useEffect, useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { calculateClientProfileCompleteness } from '../../utils/cliente/calculateClientProfileCompleteness';
import { logClienteBriefing } from '../../utils/cliente/clienteBriefingLog';
import {
  BRIEFING_CRITERIOS_ACEITE,
  BRIEFING_DOCUMENTOS,
  BRIEFING_FAIXA_VALOR,
  BRIEFING_TIPOS_RECURSO,
  briefingStateFromCliente,
  estimateCompletenessAfterBriefing,
} from '../../utils/cliente/clientBriefingState';

function toggleInList(list, id) {
  const set = new Set(Array.isArray(list) ? list : []);
  if (set.has(id)) set.delete(id);
  else set.add(id);
  return [...set];
}

function BriefingSection({ code, title, question, children, tall }) {
  return (
    <section className="consultor-briefing-section">
      <div className="consultor-briefing-section-head">
        <span className="consultor-briefing-section-code">{code}</span>
        <h3 className="consultor-briefing-section-title">{title}</h3>
      </div>
      {question ? <p className="consultor-briefing-q">{question}</p> : null}
      <div className={tall ? 'consultor-briefing-section-body consultor-briefing-section-body--tall' : 'consultor-briefing-section-body'}>
        {children}
      </div>
    </section>
  );
}

function CheckboxGroup({ options, selected, onChange, name }) {
  return (
    <div className="consultor-briefing-checkgrid" role="group" aria-label={name}>
      {options.map((opt) => (
        <label key={opt.id} className="consultor-briefing-check">
          <input
            type="checkbox"
            checked={selected.includes(opt.id)}
            onChange={() => onChange(toggleInList(selected, opt.id))}
          />
          <span>{opt.label}</span>
        </label>
      ))}
    </div>
  );
}

/**
 * Briefing rápido — perguntas guiadas para perfil consultivo.
 */
export default function ConsultorClientBriefingModal({
  isOpen = false,
  onClose,
  cliente = null,
  onSaveBriefing,
  saving = false,
}) {
  const [form, setForm] = useState(() => briefingStateFromCliente(cliente));

  useEffect(() => {
    if (!isOpen) return;
    setForm(briefingStateFromCliente(cliente));
    logClienteBriefing('modal_open', { id_cliente: cliente?.id_cliente ?? null });
  }, [isOpen, cliente]);

  const completenessBefore = useMemo(
    () => (cliente ? calculateClientProfileCompleteness(cliente).score : 0),
    [cliente],
  );

  const completenessAfter = useMemo(
    () => (cliente ? estimateCompletenessAfterBriefing(cliente, form) : 0),
    [cliente, form],
  );

  const patch = useCallback((key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleClose = useCallback(() => {
    logClienteBriefing('close', { id_cliente: cliente?.id_cliente ?? null });
    onClose?.();
  }, [onClose, cliente?.id_cliente]);

  const handleSave = useCallback(
    async (openFullForm = false) => {
      logClienteBriefing('save_start', {
        id_cliente: cliente?.id_cliente ?? null,
        open_full_form: openFullForm,
      });
      logClienteBriefing('completeness_before_after', {
        before: completenessBefore,
        after_estimate: completenessAfter,
      });
      try {
        await onSaveBriefing?.(form, { openFullForm });
        logClienteBriefing('save_success', { id_cliente: cliente?.id_cliente ?? null });
        if (openFullForm) {
          logClienteBriefing('save_and_open_full_form', { id_cliente: cliente?.id_cliente ?? null });
        }
      } catch (e) {
        logClienteBriefing('save_error', {
          id_cliente: cliente?.id_cliente ?? null,
          message: e?.message || String(e),
        });
      }
    },
    [onSaveBriefing, form, cliente?.id_cliente, completenessBefore, completenessAfter],
  );

  if (!isOpen || !cliente) return null;

  const nome = cliente.nome_empresa || cliente.razao_social || 'Cliente';

  return (
    <Modal
      portal
      zIndex={1188}
      onClose={handleClose}
      className="modal-large modal-consultor-briefing"
    >
      <div className="consultor-briefing-shell">
        <header className="consultor-briefing-header">
          <div>
            <h2 className="consultor-briefing-title">Briefing rápido do cliente</h2>
            <p className="consultor-briefing-sub">
              Preencha o essencial para melhorar a carteira, a triagem e o pré-projeto.
            </p>
            <p className="consultor-briefing-time">Tempo estimado: 3–5 minutos</p>
            <p className="consultor-briefing-intro">
              Você pode responder só o que souber agora. O restante pode ser completado depois.
            </p>
            <p className="consultor-briefing-client">{nome}</p>
          </div>
          <button
            type="button"
            className="consultor-all-opps-close-x"
            onClick={handleClose}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>

        <div className="consultor-briefing-meta">
          <span className="consultor-briefing-meta-pill">
            Completude atual: <strong>{completenessBefore}%</strong>
          </span>
          {completenessAfter > completenessBefore ? (
            <span className="consultor-briefing-meta-pill consultor-briefing-meta-pill--up">
              Estimada após salvar: <strong>{completenessAfter}%</strong>
            </span>
          ) : (
            <span className="consultor-briefing-meta-pill">
              Estimada após salvar: <strong>{completenessAfter}%</strong>
            </span>
          )}
          <p className="consultor-briefing-hint">
            Você pode complementar depois no cadastro completo.
          </p>
        </div>

        <div className="consultor-briefing-scroll">
          <BriefingSection
            code="A"
            title="Contexto do cliente"
            question="O que esse cliente faz?"
            tall
          >
            <label className="consultor-briefing-label consultor-briefing-label--field-only">
              <textarea
                className="consultor-briefing-textarea consultor-briefing-textarea--tall"
                rows={4}
                value={form.contexto_cliente}
                onChange={(e) => patch('contexto_cliente', e.target.value)}
                placeholder="Atividade principal, mercado, diferencial…"
              />
            </label>
          </BriefingSection>

          <BriefingSection
            code="B"
            title="Projeto atual"
            question="Qual projeto, problema ou oportunidade o cliente quer desenvolver?"
            tall
          >
            <label className="consultor-briefing-label consultor-briefing-label--field-only">
              <textarea
                className="consultor-briefing-textarea consultor-briefing-textarea--tall"
                rows={4}
                value={form.descricao_projeto}
                onChange={(e) => patch('descricao_projeto', e.target.value)}
                placeholder="Objetivo do projeto, problema a resolver, resultado esperado…"
              />
            </label>
          </BriefingSection>

          <BriefingSection
            code="C"
            title="Temas prioritários"
            question="Quais temas ou áreas tecnológicas são prioritários?"
          >
            <label className="consultor-briefing-label consultor-briefing-label--field-only">
              <textarea
                className="consultor-briefing-textarea"
                rows={3}
                value={form.temas_prioritarios}
                onChange={(e) => patch('temas_prioritarios', e.target.value)}
                placeholder="IA, energia, defesa, educação, sustentabilidade, indústria, saúde, software, materiais…"
              />
            </label>
          </BriefingSection>

          <BriefingSection
            code="D"
            title="Tipo de recurso"
            question="Que tipo de oportunidade faz sentido para este cliente?"
          >
            <CheckboxGroup
              name="tipos_recurso"
              options={BRIEFING_TIPOS_RECURSO}
              selected={form.tipos_recurso}
              onChange={(v) => patch('tipos_recurso', v)}
            />
          </BriefingSection>

          <BriefingSection code="E" title="Valor" question="Qual faixa de valor faz sentido?">
            <div className="consultor-briefing-radios">
              {BRIEFING_FAIXA_VALOR.map((opt) => (
                <label key={opt.id} className="consultor-briefing-radio">
                  <input
                    type="radio"
                    name="faixa_valor"
                    checked={form.faixa_valor_interesse === opt.id}
                    onChange={() => patch('faixa_valor_interesse', opt.id)}
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
            </div>
          </BriefingSection>

          <BriefingSection
            code="F"
            title="Perfil de oportunidade"
            question="O cliente aceita quais tipos de oportunidades?"
          >
            <CheckboxGroup
              name="criterios_aceite"
              options={BRIEFING_CRITERIOS_ACEITE}
              selected={form.criterios_aceite}
              onChange={(v) => patch('criterios_aceite', v)}
            />
          </BriefingSection>

          <BriefingSection code="G" title="Documentos" question="Quais documentos o cliente já tem?">
            <CheckboxGroup
              name="documentos"
              options={BRIEFING_DOCUMENTOS}
              selected={form.documentos_disponiveis}
              onChange={(v) => patch('documentos_disponiveis', v)}
            />
          </BriefingSection>

          <BriefingSection
            code="H"
            title="Observações do consultor"
            question="O que o consultor precisa lembrar sobre esse cliente?"
            tall
          >
            <label className="consultor-briefing-label consultor-briefing-label--field-only">
              <textarea
                className="consultor-briefing-textarea consultor-briefing-textarea--tall"
                rows={4}
                value={form.observacoes_internas}
                onChange={(e) => patch('observacoes_internas', e.target.value)}
                placeholder="Riscos, lacunas, combinados com o cliente, próximos passos…"
              />
            </label>
          </BriefingSection>
        </div>

        <footer className="consultor-briefing-footer">
          <button
            type="button"
            className="btn-detalhes dash-action-outline"
            onClick={handleClose}
            disabled={saving}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-view"
            onClick={() => handleSave(false)}
            disabled={saving}
          >
            {saving ? 'Salvando…' : 'Salvar briefing'}
          </button>
          <button
            type="button"
            className="btn-detalhes dash-action-outline"
            onClick={() => handleSave(true)}
            disabled={saving}
          >
            Salvar e abrir cadastro completo
          </button>
        </footer>
      </div>
    </Modal>
  );
}
