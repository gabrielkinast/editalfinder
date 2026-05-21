import PrecadFieldMeta from './PrecadFieldMeta';

export default function PrecadProjectScope({ form, fieldIntel, onChangeTxt }) {
  return (
    <section id="precad-contexto-projeto" className="precad-scope-section">
      <h3 className="precad-section-title">C) Escopo inicial</h3>
      <p className="precad-section-hint precad-muted small">
        Problema, solução, diferencial e entregáveis — linguagem clara para o cliente. Detalhes técnicos finos ficam no
        formulário completo.
      </p>

      <div className="precad-form-grid">
        <div className="precad-field-row full">
          <label className="precad-field-label">
            Título do projeto<span className="precad-tag important">importante</span>
          </label>
          <input
            className="precad-input"
            name="bloco2_titulo_projeto"
            value={form.bloco2_titulo_projeto}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco2_titulo_projeto" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">
            Resumo publicável<span className="precad-tag sug">compatível com o PDF</span>
          </label>
          <textarea
            className="precad-textarea"
            name="bloco2_resumo_publicavel"
            rows={4}
            value={form.bloco2_resumo_publicavel}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco2_resumo_publicavel" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Objetivo geral</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_objetivo_geral"
            rows={3}
            value={form.bloco_estr_objetivo_geral}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_objetivo_geral" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Problema / oportunidade</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_problema_oportunidade"
            rows={3}
            value={form.bloco_estr_problema_oportunidade}
            onChange={onChangeTxt}
          />
          {fieldIntel ? (
            <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_problema_oportunidade" />
          ) : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Solução proposta</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_solucao_proposta"
            rows={3}
            value={form.bloco_estr_solucao_proposta}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_solucao_proposta" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Diferencial inovador</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_diferencial_inovador"
            rows={3}
            value={form.bloco_estr_diferencial_inovador}
            onChange={onChangeTxt}
          />
          {fieldIntel ? (
            <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_diferencial_inovador" />
          ) : null}
        </div>
        <div className="precad-field-row">
          <label className="precad-field-label">Estágio de maturidade</label>
          <input
            className="precad-input"
            name="bloco_estr_maturidade"
            value={form.bloco_estr_maturidade}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_maturidade" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Público-alvo / mercado</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_publico_mercado"
            rows={2}
            value={form.bloco_estr_publico_mercado}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_publico_mercado" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Resultados esperados</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_resultados_esperados"
            rows={3}
            value={form.bloco_estr_resultados_esperados}
            onChange={onChangeTxt}
          />
          {fieldIntel ? (
            <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_resultados_esperados" />
          ) : null}
        </div>
      </div>
    </section>
  );
}
