import Modal from '../ui/Modal';
import { formatDateLoose } from '../../utils/formatters';
import { formatTipoAmigavel } from '../../utils/edital/formatEditalUi';
import { coerceStringArray } from '../../utils/edital/coerceArrays';
import { prazoVencido } from '../../utils/edital/dates';

function Row({ label, children }) {
  return (
    <div className="edital-detail-row">
      <span className="edital-detail-k">{label}</span>
      <span className="edital-detail-v">{children ?? '—'}</span>
    </div>
  );
}

export default function EditalDetailsModal({ edital, onClose }) {
  if (!edital) return null;

  const alerts = [];
  const p = edital.prazo_envio_raw || edital.dataLimite;
  if (p && prazoVencido(p)) alerts.push({ tipo: 'erro', t: 'Prazo vencido' });

  const vs = String(edital.validacao_status_raw || '').toLowerCase();
  if (vs === 'incompleto') alerts.push({ tipo: 'aviso', t: 'Dados incompletos' });
  if (vs === 'suspeito') alerts.push({ tipo: 'aviso', t: 'Item suspeito pela validação' });
  if (vs === 'acesso_limitado') alerts.push({ tipo: 'aviso', t: 'Acesso limitado' });

  const qc = Number(edital.qualidade_dado_raw ?? 0);
  if ((qc <= 40 && qc > 0) || (edital.descricao?.length ?? 0) < 120) {
    if (!vs) alerts.push({ tipo: 'info', t: 'Classificação / dados amplos — revise a fonte.' });
  }

  function listaPieces(...chunks) {
    const acc = [];
    for (const c of chunks) {
      acc.push(...coerceStringArray(c));
    }
    const u = [...new Set(acc)].slice(0, 14);
    return u.length ? u.join(', ') : '—';
  }

  return (
    <Modal onClose={onClose}>
      <div className="modal-header edital-detail-header">
        <h2>Detalhes do edital</h2>
      </div>
      <div className="edital-detail-scroll">
        {alerts.length > 0 && (
          <div className="edital-detail-alerts">
            {alerts.map((a) => (
              <div key={a.t} className={`edital-alert edital-alert-${a.tipo}`}>
                {a.t}
              </div>
            ))}
          </div>
        )}
        <h3 className="edital-detail-title">{edital.titulo}</h3>
        <p className="edital-detail-desc">{edital.descricao || 'Descrição não informada.'}</p>

        <div className="edital-detail-grid">
          <Row label="Fonte / órgão">{edital.fonte_recurso_display || edital.orgao}</Row>
          <Row label="Link oficial">
            {edital.linkOriginal ? (
              <a href={edital.linkOriginal} target="_blank" rel="noreferrer">
                Abrir site
              </a>
            ) : (
              '—'
            )}
          </Row>
          <Row label="PDF">
            {edital.pdfUrl ? (
              <a href={edital.pdfUrl} target="_blank" rel="noreferrer">
                Abrir PDF
              </a>
            ) : (
              'Sem PDF cadastrado'
            )}
          </Row>
          <Row label="Tipo de oportunidade">{formatTipoAmigavel(edital.tipo_oportunidade_raw)}</Row>
          <Row label="Tipo de recurso">{formatTipoAmigavel(edital.tipo_recurso_raw || edital.tipoRecurso)}</Row>
          <Row label="Perfil ideal">{listaPieces(edital.perfil_ideal_raw)}</Row>
          <Row label="Público-alvo">{listaPieces(edital.publico_alvo_arr_raw, edital.publico_alvo_raw)}</Row>
          <Row label="Setores estratégicos">{listaPieces(edital.setor_estrategico_raw)}</Row>
          <Row label="Áreas tecnológicas">{listaPieces(edital.area_tecnologica_raw)}</Row>
          <Row label="Área (campo texto)">{edital.area || '—'}</Row>
          <Row label="Localização">
            {[edital.cidade_raw, edital.uf_raw, edital.regiao_raw, edital.pais_raw].filter(Boolean).join(' · ') ||
              edital.estado ||
              '—'}
          </Row>
          <Row label="Valor (est.)">
            {edital.valor_principal_num ? `R$ ${edital.valor_principal_num.toLocaleString('pt-BR')}` : 'Não informado'}
          </Row>
          <Row label="Moeda">{edital.moeda_raw}</Row>
          <Row label="Prazo envio">{p ? formatDateLoose(p) : 'Sem prazo'}</Row>
          <Row label="Publicação">{edital.data_publicacao_raw ? formatDateLoose(edital.data_publicacao_raw) : '—'}</Row>
          <Row label="Ativo">{edital.ativo === false ? 'Não' : 'Sim'}</Row>
          <Row label="Situação">{edital.situacao_raw}</Row>
          <Row label="Qualidade (0–100)">
            {edital.qualidade_dado_raw != null ? `${edital.qualidade_dado_raw}` : 'Qualidade não avaliada'}
          </Row>
          <Row label="Validação">{edital.validacao_status_raw || '—'}</Row>
          <Row label="Classificação confiança">{edital.classificacao_confianca_raw}</Row>
          <Row label="Origem portal">{edital.origem_portal_raw}</Row>
          <Row label="Idioma original">{edital.idioma_original_raw}</Row>
          <Row label="Código / nº edital / chamada">
            {[edital.codigo_oportunidade_raw, edital.numero_edital_raw, edital.numero_chamada_raw]
              .filter(Boolean)
              .join(' · ') || '—'}
          </Row>
          {edital.extras_raw && (
            <Row label="Extras (JSON)">
              <pre className="edital-extras-pre">{JSON.stringify(edital.extras_raw, null, 2)}</pre>
            </Row>
          )}
        </div>
      </div>
      <div className="edital-detail-footer">
        <button type="button" className="btn-view" onClick={onClose}>
          Fechar
        </button>
      </div>
    </Modal>
  );
}
