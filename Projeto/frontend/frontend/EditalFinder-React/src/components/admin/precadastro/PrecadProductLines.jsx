const LINHAS = [
  {
    field: 'bloco1_linha_credito_principal',
    title: 'Linha principal',
    subtitle: 'Crédito inovação — produto institucional',
    body: 'Voltada a projetos com foco em desenvolvimento de produtos, processos ou serviços com inovação para a empresa.',
  },
  {
    field: 'bloco1_linha_credito_telecom',
    title: 'Telecomunicações',
    subtitle: 'Linha com aderência a telecomunicações',
    body: 'Indicada quando o projeto envolve conectividade, infraestrutura de redes ou soluções digitais de telecom.',
  },
];

function badgeFromMeta(meta, checked) {
  if (!meta) return { className: 'precad-line-badge muted', label: checked ? 'Selecionada' : 'Opção' };
  const map = {
    recomendada: 'precad-line-badge primary',
    compativel: 'precad-line-badge ok',
    alternativa: 'precad-line-badge alt',
  };
  return {
    className: map[meta.badge] || 'precad-line-badge muted',
    label: meta.badge === 'recomendada' ? 'Recomendada' : meta.badge === 'compativel' ? 'Compatível' : 'Alternativa',
  };
}

function aderenciaLabel(nivel) {
  if (nivel === 'alta') return 'Alta aderência';
  if (nivel === 'media') return 'Média aderência';
  return 'Baixa aderência';
}

export default function PrecadProductLines({ form, onChangeChk, linesMeta }) {
  const principal = linesMeta?.principal;
  const telecom = linesMeta?.telecom;

  return (
    <section className="precad-lines-section">
      <h3 className="precad-section-title">Produtos / linha</h3>
      <p className="precad-muted small">
        Selecione as linhas aplicáveis. As etiquetas são sugestões pela leitura do cadastro — ajuste conforme sua análise.
      </p>
      <div className="precad-line-cards">
        {LINHAS.map((def) => {
          const meta = def.field.includes('principal') ? principal : telecom;
          const checked = !!form[def.field];
          const { className, label } = badgeFromMeta(meta, checked);
          return (
            <label
              key={def.field}
              className={`precad-line-card ${checked ? 'is-selected' : ''}`}
              htmlFor={`ln-${def.field}`}
            >
              <div className="precad-line-card-head">
                <input
                  id={`ln-${def.field}`}
                  type="checkbox"
                  name={def.field}
                  checked={checked}
                  onChange={onChangeChk}
                />
                <div>
                  <div className="precad-line-title-row">
                    <span className="precad-line-title">{def.title}</span>
                    <span className={className}>{label}</span>
                    {meta ? (
                      <span className="precad-line-ader">{aderenciaLabel(meta.aderencia)}</span>
                    ) : null}
                  </div>
                  <span className="precad-line-sub">{def.subtitle}</span>
                </div>
              </div>
              <p className="precad-line-body">{def.body}</p>
              {meta?.motivo ? <p className="precad-line-motivo">{meta.motivo}</p> : null}
            </label>
          );
        })}
      </div>
    </section>
  );
}
