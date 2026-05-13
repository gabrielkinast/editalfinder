import PrecadFieldMeta from './PrecadFieldMeta';

/**
 * Mini análise consultiva + campos estratégicos editáveis.
 */

function FieldRow({ label, children, hint }) {
  return (
    <div className="precad-field-row">
      <label className="precad-field-label">
        {label}
        {hint ? <span className="precad-field-hint">{hint}</span> : null}
      </label>
      {children}
    </div>
  );
}

export default function PrecadRecommendationCard({ suggestions, form, fieldIntel, onChangeTxt, onChangeChk }) {
  return (
    <div className="precad-reco-grid">
      <article className="precad-card precad-card-hero">
        <h3 className="precad-card-title">Contexto e recomendação</h3>
        <p className="precad-card-lead">
          Projeto sugerido para este cliente com base no cadastro e, quando houver, no edital / radar de fomento.
        </p>
        <dl className="precad-dl">
          <div>
            <dt>Resumo automático</dt>
            <dd>{suggestions.resumoExecutivo}</dd>
          </div>
          <div>
            <dt>Linha / produto sugerido</dt>
            <dd>
              <strong>{suggestions.linhaRecomendadaLabel}</strong>
            </dd>
          </div>
          <div>
            <dt>Por que essa indicação</dt>
            <dd>{suggestions.motivoRecomendacao}</dd>
          </div>
          <div>
            <dt>Principais aderências</dt>
            <dd className="precad-pre-wrap">{suggestions.principaisAderencias || '—'}</dd>
          </div>
          <div>
            <dt>Pontos que exigem complementação</dt>
            <dd className="precad-pre-wrap">{suggestions.pontosComplementar || '—'}</dd>
          </div>
        </dl>
      </article>

      <article className="precad-card">
        <h3 className="precad-card-title">Ajustes finos (editáveis)</h3>
        <p className="precad-muted small">
          Texto sugerido preenche os campos abaixo na primeira abertura; altere livremente.
        </p>
        <FieldRow label="Título do edital de referência" hint="opcional">
          <input
            className="precad-input"
            name="bloco_estr_edital_ref_titulo"
            value={form.bloco_estr_edital_ref_titulo}
            onChange={onChangeTxt}
            placeholder="Ex.: linha ou edital prioritário"
          />
        </FieldRow>
        <FieldRow label="Nível de aderência (texto livre)">
          <input
            className="precad-input"
            name="bloco_estr_aderencia_nivel"
            value={form.bloco_estr_aderencia_nivel}
            onChange={onChangeTxt}
            placeholder="Ex.: alta — com ressalvas documentais"
          />
        </FieldRow>
        <FieldRow label="Resumo executivo (documento)">
          <textarea
            className="precad-textarea"
            name="bloco_estr_resumo_executivo"
            rows={4}
            value={form.bloco_estr_resumo_executivo}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_resumo_executivo" /> : null}
        </FieldRow>
        <FieldRow label="Tipo de recurso / produto de referência" hint="alimenta relatório quando edital incompleto">
          <input
            className="precad-input"
            name="bloco_estr_tipo_recurso_pdf"
            value={form.bloco_estr_tipo_recurso_pdf}
            onChange={onChangeTxt}
            placeholder="Ex.: financiamento, subvenção, crédito, etc."
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_tipo_recurso_pdf" /> : null}
        </FieldRow>
        <FieldRow label="Referências financeiras do edital (somente texto)" hint="preencher com dados reais">
          <textarea
            className="precad-textarea"
            name="bloco_estr_ref_fin_texto"
            rows={4}
            value={form.bloco_estr_ref_fin_texto || ''}
            onChange={onChangeTxt}
            placeholder="Valor indicado pela oportunidade, contrapartida, carência/amortização, taxas quando existentes no cadastro público"
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_ref_fin_texto" /> : null}
        </FieldRow>
        <FieldRow label="Montante solicitado pelo projeto" hint="ou marque quando ainda indefinido">
          <input
            className="precad-input"
            name="bloco2_recursos_adicionais_valor"
            value={form.bloco2_recursos_adicionais_valor}
            onChange={onChangeTxt}
          />
          {onChangeChk ? (
            <label className="precad-muted small">
              <input
                type="checkbox"
                name="bloco2_valor_projeto_sem_def"
                checked={!!form.bloco2_valor_projeto_sem_def}
                onChange={onChangeChk}
              />{' '}
              Valor ainda não definido (completude válida assim)
            </label>
          ) : null}
        </FieldRow>
        <FieldRow label="Motivo da recomendação (texto consultivo)">
          <textarea
            className="precad-textarea"
            name="bloco_estr_motivo_recomendacao"
            rows={3}
            value={form.bloco_estr_motivo_recomendacao}
            onChange={onChangeTxt}
          />
        </FieldRow>
        <FieldRow label="Principais aderências (lista)">
          <textarea
            className="precad-textarea"
            name="bloco_estr_principais_aderencias"
            rows={4}
            value={form.bloco_estr_principais_aderencias}
            onChange={onChangeTxt}
          />
        </FieldRow>
        <FieldRow label="Pontos a complementar">
          <textarea
            className="precad-textarea"
            name="bloco_estr_pontos_complementar"
            rows={3}
            value={form.bloco_estr_pontos_complementar}
            onChange={onChangeTxt}
          />
        </FieldRow>
      </article>
    </div>
  );
}
