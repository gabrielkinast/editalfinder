import { IMP_ECO } from '../../../services/precadastroProjetoPdfConstants';

const SOC_KEYS = [
  ['bloco2_imp_soc_emp_direct', 'Aumento geração empregos diretos'],
  ['bloco2_imp_soc_emp_indir', 'Aumento empregos indiretos'],
  ['bloco2_imp_soc_bemestar', 'Bem-estar dos funcionários'],
  ['bloco2_imp_soc_seguranca', 'Segurança no trabalho'],
  ['bloco2_imp_soc_educacao', 'Educação'],
  ['bloco2_imp_soc_pobreza', 'Redução da pobreza'],
  ['bloco2_imp_soc_qualidade_vida', 'Qualidade de vida'],
  ['bloco2_imp_soc_moradia', 'Moradia'],
  ['bloco2_imp_soc_pcd', 'Acessibilidade PcDs'],
];

const AMB_KEYS = [
  ['bloco2_imp_amb_co2', 'Redução CO2'],
  ['bloco2_imp_amb_energia', 'Menos energia'],
  ['bloco2_imp_amb_agua', 'Menos água'],
  ['bloco2_imp_amb_poluentes', 'Menos poluentes'],
  ['bloco2_imp_amb_reciclado', 'Material reciclado'],
  ['bloco2_imp_amb_materiais', 'Menos consumo matéria-prima'],
  ['bloco2_imp_amb_subst_energy', 'Substituição energia fosséis por renovável'],
  ['bloco2_imp_amb_subst_mp', 'Matérias menos contaminantes'],
  ['bloco2_imp_amb_contaminacao', 'Menos contaminação'],
  ['bloco2_imp_amb_reciclagem', 'Reciclagem / reutilização'],
];

/** Formulário institucional completo (estrutura original). */
export default function PrecadLegacyFormBody({
  form,
  onChangeTxt,
  onChangeChk,
  atualizaFontes,
  addFonteLinha,
  rmFonteLinha,
  atualizaMeta,
  addMetaLinha,
  rmMetaLinha,
}) {
  const section = (titulo, inner, sectionId) => (
    <details className="precad-section" open id={sectionId || undefined}>
      <summary className="precad-summary">{titulo}</summary>
      <div className="precad-fields">{inner}</div>
    </details>
  );

  return (
    <>
      {section(
        'Produtos / linha',
        <>
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="bloco1_linha_credito_principal"
              checked={!!form.bloco1_linha_credito_principal}
              onChange={onChangeChk}
            />
            <span>Linha principal (crédito inovação produto institucional)</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="bloco1_linha_credito_telecom"
              checked={!!form.bloco1_linha_credito_telecom}
              onChange={onChangeChk}
            />
            <span>Linha com aderência a telecomunicações</span>
          </label>
        </>,
      )}

      {section(
        'Bloco 1 — Dados cadastrais e sede',
        <>
          <div className="form-grid-two">
            <div className="form-group"><label>Porte (cadastro)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_porte_empresa" value={form.bloco1_porte_empresa} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Setor (cadastro)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_setor_empresa" value={form.bloco1_setor_empresa} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-grid-two">
            <div className="form-group"><label>CNPJ</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_cnpj" value={form.bloco1_cnpj} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Razão social</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_razao_social" value={form.bloco1_razao_social} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Nome fantasia</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_nome_fantasia" value={form.bloco1_nome_fantasia} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Data constituição</label><input type="date" className="filter-input-large" style={{ width: '100%' }} name="bloco1_data_constituicao" value={form.bloco1_data_constituicao} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Início da operação</label><input type="date" className="filter-input-large" style={{ width: '100%' }} name="bloco1_data_inicio_operacao" value={form.bloco1_data_inicio_operacao} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-group"><label>Logradouro</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_logradouro" value={form.bloco1_logradouro} onChange={onChangeTxt} /></div>
          <div className="form-grid-two">
            <div className="form-group"><label>Número</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_numero" value={form.bloco1_numero} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Complemento</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_complemento" value={form.bloco1_complemento} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-group"><label>Bairro</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_bairro" value={form.bloco1_bairro} onChange={onChangeTxt} /></div>
          <div className="form-grid-two">
            <div className="form-group"><label>Município</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_municipio" value={form.bloco1_municipio} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>UF</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_uf" value={form.bloco1_uf} maxLength={2} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-group"><label>CEP</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_cep" value={form.bloco1_cep} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Site</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_site" value={form.bloco1_site} onChange={onChangeTxt} /></div>
        </>,
        'precad-legacy-cadastro',
      )}

      {section(
        'Contato na empresa',
        <div className="form-grid-two">
          <div className="form-group"><label>CPF</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_cpf_contato" value={form.bloco1_cpf_contato} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Nome</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_nome_contato" value={form.bloco1_nome_contato} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Cargo</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_cargo_contato" value={form.bloco1_cargo_contato} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>E-mail</label><input type="email" className="filter-input-large" style={{ width: '100%' }} name="bloco1_email_contato" value={form.bloco1_email_contato} onChange={onChangeTxt} /></div>
          <div className="form-group full-width"><label>Telefone</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_telefone_contato" value={form.bloco1_telefone_contato} onChange={onChangeTxt} /></div>
        </div>,
        'precad-legacy-contato',
      )}

      {section(
        'Dados econômicos e quadro',
        <>
          <div className="form-group"><label>CNAE principal</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_cnae" value={form.bloco1_cnae} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Parte de grupo econômico (sim/não / descreva)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_parte_grupo_economico" value={form.bloco1_parte_grupo_economico} onChange={onChangeTxt} /></div>
          <div className="form-grid-two">
            <div className="form-group"><label>Faturamento do grupo (R$)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_faturamento_grupo" value={form.bloco1_faturamento_grupo} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Receita operacional último exercício</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_receita_rob_ultimo" value={form.bloco1_receita_rob_ultimo} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-grid-two">
            <div className="form-group"><label>EBITDA</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_ebitda" value={form.bloco1_ebitda} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Data referência receita/EBITDA</label><input type="date" className="filter-input-large" style={{ width: '100%' }} name="bloco1_data_ref_receita" value={form.bloco1_data_ref_receita} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-grid-two">
            <div className="form-group"><label>Nº pessoas na data da receita</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_num_pessoas_receita_ref" value={form.bloco1_num_pessoas_receita_ref} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Despesa empregados (ano)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_despesa_empregados_receita" value={form.bloco1_despesa_empregados_receita} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-grid-two">
            <div className="form-group"><label>Doutores</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_doutores" value={form.bloco1_doutores} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Mestres</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_mestres" value={form.bloco1_mestres} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Graduados</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_graduados" value={form.bloco1_graduados} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Fundamental e médio</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_fund_medio" value={form.bloco1_fund_medio} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-group"><label>Total empregados</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_total_empregados" value={form.bloco1_total_empregados} onChange={onChangeTxt} /></div>
        </>,
        'precad-legacy-economicos',
      )}

      {section(
        'Relacionamento com órgão / atividades',
        <>
          <div className="form-group"><label>Antecedentes no órgão (sim/não + texto)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_orgao_antecedentes_sim" value={form.bloco1_orgao_antecedentes_sim} onChange={onChangeTxt} placeholder="Ex.: Sim / Não" /></div>
          <div className="form-group"><label>Detalhar apoios anteriores</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '64px' }} name="bloco1_orgao_antecedentes_texto" value={form.bloco1_orgao_antecedentes_texto} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Principais atividades da empresa</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '100px' }} name="bloco1_principais_atividades" value={form.bloco1_principais_atividades} onChange={onChangeTxt} /></div>
        </>,
      )}

      {section(
        'PD&I e parcerias',
        <>
          <div className="form-group"><label>Infraestrutura PD&I (sim/não + detalhar)</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '60px' }} name="bloco1_pdi_infraestrutura" value={form.bloco1_pdi_infraestrutura} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Pessoas 31/12 (referência)</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '60px' }} name="bloco1_pdi_detalhe_pessoas" value={form.bloco1_pdi_detalhe_pessoas} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Parceria ICT (sim/não)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_pdi_parceria_ict_sim" value={form.bloco1_pdi_parceria_ict_sim} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Parceria ICT — detalhar</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '50px' }} name="bloco1_pdi_parceria_ict_txt" value={form.bloco1_pdi_parceria_ict_txt} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Parceria empresas (sim/não)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_pdi_parceria_empresas_sim" value={form.bloco1_pdi_parceria_empresas_sim} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Parceria empresas — detalhar</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '72px' }} name="bloco1_pdi_parceria_empresas_txt" value={form.bloco1_pdi_parceria_empresas_txt} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Propriedade intelectual 3 anos (sim/não + texto)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_pdi_pi_3anos_sim" value={form.bloco1_pdi_pi_3anos_sim} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Depósitos/registros — detalhar</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '44px' }} name="bloco1_pdi_pi_3anos_txt" value={form.bloco1_pdi_pi_3anos_txt} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Contratos tecnologia INPI</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_pdi_contratos_inpi_sim" value={form.bloco1_pdi_contratos_inpi_sim} onChange={onChangeTxt} /></div>
          <textarea className="filter-input-large" style={{ width: '100%', minHeight: '44px' }} name="bloco1_pdi_contratos_inpi_txt" value={form.bloco1_pdi_contratos_inpi_txt} onChange={onChangeTxt} placeholder="Detalhar contratos tecnologia averbados" />
          <div className="form-group"><label>Outras agências de fomento</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco1_pdi_outras_agencias_sim" value={form.bloco1_pdi_outras_agencias_sim} onChange={onChangeTxt} /></div>
          <textarea className="filter-input-large" style={{ width: '100%', minHeight: '44px' }} name="bloco1_pdi_outras_agencias_txt" value={form.bloco1_pdi_outras_agencias_txt} onChange={onChangeTxt} />
        </>,
        'precad-legacy-pdi',
      )}

      {section(
        'Bloco 2 — Projeto e finalidades',
        <>
          <div className="form-group"><label>Título do projeto</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_titulo_projeto" value={form.bloco2_titulo_projeto} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Resumo publicável</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '90px' }} name="bloco2_resumo_publicavel" value={form.bloco2_resumo_publicavel} onChange={onChangeTxt} /></div>
          {['a', 'b', 'c', 'd', 'e', 'f', 'g'].map((l) => (
            <div className="form-group" key={l}>
              <label>{`Finalidade (${l})`}</label>
              <textarea
                className="filter-input-large"
                style={{ width: '100%', minHeight: '56px' }}
                name={`bloco2_finalidade_${l}`}
                value={form[`bloco2_finalidade_${l}`]}
                onChange={onChangeTxt}
              />
            </div>
          ))}
          <div className="form-group"><label>Comentários adicionais</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '64px' }} name="bloco2_comentarios_adicionais" value={form.bloco2_comentarios_adicionais} onChange={onChangeTxt} /></div>
          <div className="form-grid-two">
            <div className="form-group"><label>CNAE do projeto</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_cnae_projeto" value={form.bloco2_cnae_projeto} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>UF execução</label><input className="filter-input-large" style={{ width: '100%' }} maxLength={2} name="bloco2_uf_projeto" value={form.bloco2_uf_projeto} onChange={onChangeTxt} /></div>
          </div>
        </>,
      )}

      {section(
        'PD&I do projeto (quadro)',
        <div className="form-grid-two">
          {[['bloco2_pd_i_pos','Pós/mestrad/dout'],['bloco2_pd_i_graduados','Graduados'],['bloco2_pd_i_tecnico','Técnico médio'],['bloco2_pd_i_outros','Outros suporte']].map(([nm, lb]) => (
            <div className="form-group" key={nm}><label>{lb}</label><input className="filter-input-large" style={{ width: '100%' }} name={nm} value={form[nm]} onChange={onChangeTxt} /></div>
          ))}
        </div>,
      )}

      {section(
        'Tipo / nível de inovação e aspectos',
        <>
          <div className="checkbox-stack">
            {[
              ['bloco2_tp_inov_novo_produto', 'Novo produto'],
              ['bloco2_tp_inov_novo_processo', 'Novo processo'],
              ['bloco2_tp_inov_melhoria_produto', 'Melhoria significativa de produto'],
              ['bloco2_tp_inov_melhoria_processo', 'Melhoria significativa de processo'],
            ].map(([k, lbl]) => (
              <label className="checkbox-label" key={k}>
                <input type="checkbox" name={k} checked={!!form[k]} onChange={onChangeChk} />
                <span>{lbl}</span>
              </label>
            ))}
          </div>
          <div className="checkbox-stack">
            <span style={{ fontWeight: 600, fontSize: '13px', marginBottom: '6px', display: 'block' }}>
              Nível desejado (marque os que aplicar)
            </span>
            {[
              ['bloco2_nivel_empresa', 'Empresa'],
              ['bloco2_nivel_regiao', 'Região'],
              ['bloco2_nivel_brasil', 'Brasil'],
              ['bloco2_nivel_mundo', 'Mundo'],
            ].map(([k, lbl]) => (
              <label className="checkbox-label" key={k}>
                <input type="checkbox" name={k} checked={!!form[k]} onChange={onChangeChk} />
                <span>{lbl}</span>
              </label>
            ))}
          </div>
          <div className="form-group"><label>Aspectos regulatórios (sim/não)</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_aspectos_regulatorios_sim" value={form.bloco2_aspectos_regulatorios_sim} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Aspectos regulatórios — descrever</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '50px' }} name="bloco2_aspectos_regulatorios_txt" value={form.bloco2_aspectos_regulatorios_txt} onChange={onChangeTxt} /></div>
        </>,
      )}

      {section(
        'Recursos contrapartidas e equipamentos importados',
        <>
          <div className="form-grid-two">
            <div className="form-group"><label>Percentual projeto com ICTs</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_pct_icts" value={form.bloco2_pct_icts} onChange={onChangeTxt} /></div>
            <div className="form-group"><label>Recursos adicionais?</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_recursos_adicionais_sim" value={form.bloco2_recursos_adicionais_sim} onChange={onChangeTxt} /></div>
          </div>
          <div className="form-group"><label>Montante recursos adicionais</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_recursos_adicionais_valor" value={form.bloco2_recursos_adicionais_valor} onChange={onChangeTxt} /></div>
          <label className="checkbox-label"><input type="checkbox" name="bloco2_justifica_import_naosimilar" checked={!!form.bloco2_justifica_import_naosimilar} onChange={onChangeChk} /><span>Não há similar nacional (importação)</span></label>
          <label className="checkbox-label"><input type="checkbox" name="bloco2_justifica_import_qualidade" checked={!!form.bloco2_justifica_import_qualidade} onChange={onChangeChk} /><span>Importação com qualidade superior</span></label>
          <label className="checkbox-label"><input type="checkbox" name="bloco2_justifica_import_preco" checked={!!form.bloco2_justifica_import_preco} onChange={onChangeChk} /><span>Importação com preço inferior</span></label>
          <label className="checkbox-label"><input type="checkbox" name="bloco2_justifica_sem_importados" checked={!!form.bloco2_justifica_sem_importados} onChange={onChangeChk} /><span>Não haverá equipamentos importados</span></label>
          <div className="form-group"><label>Obs. importação</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '44px' }} name="bloco2_justifica_import_obs" value={form.bloco2_justifica_import_obs} onChange={onChangeTxt} /></div>
          <div className="form-group"><label>Compromisso / impactos sociais (texto)</label><textarea className="filter-input-large" style={{ width: '100%', minHeight: '60px' }} name="bloco2_compromiso_social" value={form.bloco2_compromiso_social} onChange={onChangeTxt} /></div>
        </>,
        'precad-legacy-recursos',
      )}

      {section(
        'Impactos econômicos',
        <div className="checkbox-stack">
          {IMP_ECO.map(([k, lbl]) => (
            <label className="checkbox-label" key={k}>
              <input type="checkbox" name={k} checked={!!form[k]} onChange={onChangeChk} />
              <span>{lbl}</span>
            </label>
          ))}
          <div className="form-group full-width"><label>Outros econômicos</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_imp_eco_outros_txt" value={form.bloco2_imp_eco_outros_txt} onChange={onChangeTxt} /></div>
        </div>,
        'precad-legacy-impactos-eco',
      )}

      {section(
        'Impactos sociais',
        <div className="checkbox-stack">
          {SOC_KEYS.map(([k, lbl]) => (
            <label className="checkbox-label" key={k}>
              <input type="checkbox" name={k} checked={!!form[k]} onChange={onChangeChk} />
              <span>{lbl}</span>
            </label>
          ))}
          <div className="form-group"><label>Outros sociais</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_imp_soc_outros_txt" value={form.bloco2_imp_soc_outros_txt} onChange={onChangeTxt} /></div>
        </div>,
      )}

      {section(
        'Impactos ambientais',
        <div className="checkbox-stack">
          {AMB_KEYS.map(([k, lbl]) => (
            <label className="checkbox-label" key={k}>
              <input type="checkbox" name={k} checked={!!form[k]} onChange={onChangeChk} />
              <span>{lbl}</span>
            </label>
          ))}
          <div className="form-group"><label>Outros ambientais</label><input className="filter-input-large" style={{ width: '100%' }} name="bloco2_imp_amb_outros_txt" value={form.bloco2_imp_amb_outros_txt} onChange={onChangeTxt} /></div>
        </div>,
      )}

      {section(
        'Licenças',
        <div className="form-group"><textarea className="filter-input-large" style={{ width: '100%', minHeight: '64px' }} name="bloco2_licencas" value={form.bloco2_licencas} onChange={onChangeTxt} placeholder="Licenças necessárias (ou ‘Não aplicável’)." /></div>,
        'precad-legacy-licencas',
      )}

      {section(
        'Quadro de usos / fontes (linhas)',
        <>
          {(form.bloco2_uso_fontes || []).map((linha, i) => (
            <div key={i} className="precad-row-box">
              <div className="form-grid-two">
                {['item', 'lib1', 'lib2', 'libN', 'totalFin', 'contrapartida'].map((campo) => (
                  <div className="form-group" key={campo}>
                    <label>{campo}</label>
                    <input
                      className="filter-input-large"
                      style={{ width: '100%' }}
                      value={linha[campo] || ''}
                      onChange={(e) => atualizaFontes(i, campo, e.target.value)}
                    />
                  </div>
                ))}
              </div>
              {(form.bloco2_uso_fontes || []).length > 1 ? (
                <button type="button" className="btn-action btn-delete" onClick={() => rmFonteLinha(i)}>Remover linha</button>
              ) : null}
            </div>
          ))}
          <button type="button" className="btn-edit btn-action" onClick={addFonteLinha}>+ Linha financiável</button>
        </>,
        'precad-legacy-fontes',
      )}

      {section(
        'Cronograma físico (metas)',
        <>
          {(form.bloco2_metas_fisicas || []).map((linha, i) => (
            <div key={i} className="precad-row-box">
              <div className="form-grid-two">
                <div className="form-group full-width"><label>Meta</label><input className="filter-input-large" style={{ width: '100%' }} value={linha.meta || ''} onChange={(e) => atualizaMeta(i, 'meta', e.target.value)} /></div>
                <div className="form-group full-width"><label>Atividades</label><input className="filter-input-large" style={{ width: '100%' }} value={linha.atividade || ''} onChange={(e) => atualizaMeta(i, 'atividade', e.target.value)} /></div>
                <div className="form-group full-width"><label>Indicador de execução</label><input className="filter-input-large" style={{ width: '100%' }} value={linha.indicador || ''} onChange={(e) => atualizaMeta(i, 'indicador', e.target.value)} /></div>
                <div className="form-group"><label>Início</label><input type="date" className="filter-input-large" style={{ width: '100%' }} value={linha.ini || ''} onChange={(e) => atualizaMeta(i, 'ini', e.target.value)} /></div>
                <div className="form-group"><label>Fim</label><input type="date" className="filter-input-large" style={{ width: '100%' }} value={linha.fim || ''} onChange={(e) => atualizaMeta(i, 'fim', e.target.value)} /></div>
              </div>
              {(form.bloco2_metas_fisicas || []).length > 1 ? (
                <button type="button" className="btn-action btn-delete" onClick={() => rmMetaLinha(i)}>Remover meta</button>
              ) : null}
            </div>
          ))}
          <button type="button" className="btn-edit btn-action" onClick={addMetaLinha}>+ Meta física</button>
        </>,
        'precad-legacy-metas',
      )}
    </>
  );
}
