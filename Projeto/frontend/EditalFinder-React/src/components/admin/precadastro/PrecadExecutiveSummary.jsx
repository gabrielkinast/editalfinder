import PrecadFieldMeta from './PrecadFieldMeta';
import PrecadSectionHint from './PrecadSectionHint';

export default function PrecadExecutiveSummary({ form, fieldIntel, onChangeTxt, clienteNome }) {
  return (
    <section id="precad-resumo-executivo" className="precad-consultor-section">
      <h3 className="precad-section-title">A) Resumo executivo</h3>
      <PrecadSectionHint>
        Visão para o consultor apresentar ao cliente: oportunidade, objetivo, valor e status. Campos vazios podem ser
        preenchidos com &quot;Gerar sugestões automáticas&quot;.
      </PrecadSectionHint>

      <div className="precad-form-grid">
        {clienteNome ? (
          <div className="precad-field-row full">
            <label className="precad-field-label">Cliente</label>
            <input className="precad-input" value={clienteNome} readOnly disabled aria-readonly="true" />
          </div>
        ) : null}
        <div className="precad-field-row full">
          <label className="precad-field-label">Oportunidade / edital de referência</label>
          <input
            className="precad-input"
            name="bloco_estr_edital_ref_titulo"
            value={form.bloco_estr_edital_ref_titulo}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_edital_ref_titulo" /> : null}
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Fonte / órgão</label>
          <input
            className="precad-input"
            name="bloco_estr_oportunidade_fonte"
            value={form.bloco_estr_oportunidade_fonte}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Prazo (referência)</label>
          <input
            className="precad-input"
            name="bloco_estr_oportunidade_prazo"
            value={form.bloco_estr_oportunidade_prazo}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Link da oportunidade</label>
          <input
            className="precad-input"
            name="bloco_estr_oportunidade_link"
            value={form.bloco_estr_oportunidade_link}
            onChange={onChangeTxt}
            placeholder="https://…"
          />
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Compatibilidade (Radar)</label>
          <input
            className="precad-input"
            name="bloco_estr_score_compatibilidade"
            value={form.bloco_estr_score_compatibilidade}
            onChange={onChangeTxt}
            placeholder="Ex.: 72% — Alta (referência interna)"
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_score_compatibilidade" /> : null}
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Nível de aderência</label>
          <select
            className="precad-select"
            name="bloco_estr_aderencia_nivel"
            value={form.bloco_estr_aderencia_nivel}
            onChange={onChangeTxt}
          >
            <option value="">— Selecionar —</option>
            <option value="alta">Alta</option>
            <option value="media">Média</option>
            <option value="baixa">Baixa</option>
          </select>
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Resumo executivo</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_resumo_executivo"
            rows={5}
            value={form.bloco_estr_resumo_executivo}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_resumo_executivo" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Objetivo do projeto</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_objetivo_geral"
            rows={3}
            value={form.bloco_estr_objetivo_geral}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Valor solicitado / estimado</label>
          <input
            className="precad-input"
            name="bloco2_recursos_adicionais_valor"
            value={form.bloco2_recursos_adicionais_valor}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Status do pré-projeto</label>
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
      </div>
    </section>
  );
}
