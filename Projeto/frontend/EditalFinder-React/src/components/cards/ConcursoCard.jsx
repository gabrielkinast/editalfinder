import { formatCurrency, formatDate, formatArray } from '../../utils/formatters';
import { labelTipoSelecao, labelStatus, getConcursoBadges } from '../../utils/concursos/concursosLabels';
import ExternalActionButton, { EXTERNAL_ACTION_TYPES } from '../../utils/externalActions';
import './ConcursoCard.css';

function formatDiasLegenda(dias) {
  if (dias == null || Number.isNaN(Number(dias))) return null;
  const d = Number(dias);
  if (d === 0) return 'Hoje';
  if (d > 0) return `Em ${d} dia${d === 1 ? '' : 's'}`;
  return `Há ${Math.abs(d)} dia${Math.abs(d) === 1 ? '' : 's'}`;
}

function formatFaixaSalario(min, max) {
  const hasMin = min != null && min !== '' && Number.isFinite(Number(min));
  const hasMax = max != null && max !== '' && Number.isFinite(Number(max));
  if (!hasMin && !hasMax) return null;
  const a = hasMin ? formatCurrency(Number(min)) : null;
  const b = hasMax ? formatCurrency(Number(max)) : null;
  if (a && b && Number(min) === Number(max)) return a;
  if (a && b) return `${a} — ${b}`;
  if (a) return `Desde ${a}`;
  if (b) return `Até ${b}`;
  return null;
}

/** Órgão / instituição: um só valor quando redundante ou muito parecido. */
function orgaoInstituicaoText(row) {
  const o = (row.orgao || '').trim();
  const i = (row.instituicao || '').trim();
  if (!o && !i) return null;
  if (o && !i) return o;
  if (i && !o) return i;
  const lo = o.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const li = i.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  if (lo === li) return o;
  if (lo.includes(li) || li.includes(lo)) return o.length >= i.length ? o : i;
  return `${o} · ${i}`;
}

function cargoCursoText(row) {
  const c = (row.cargo || '').trim();
  const u = (row.curso || '').trim();
  if (c && u) return `${c} · ${u}`;
  return c || u || null;
}

function localEstadoMunicipioText(row) {
  const e = (row.estado || '').trim();
  const m = (row.municipio || '').trim();
  if (e && m) return `${m} (${e})`;
  return m || e || null;
}

function mutedHint(text) {
  return <span className="concurso-card__missing-hint">{text}</span>;
}

export default function ConcursoCard({ row }) {
  if (!row) return null;

  const badges = getConcursoBadges(row);
  const salarioFmt = formatFaixaSalario(row.salario_min, row.salario_max);
  const taxa =
    row.taxa_inscricao != null && row.taxa_inscricao !== '' && Number.isFinite(Number(row.taxa_inscricao))
      ? formatCurrency(Number(row.taxa_inscricao))
      : null;
  const hasFimInsc = Boolean(row.data_fim_inscricao);
  const fimInsc = hasFimInsc ? formatDate(String(row.data_fim_inscricao).slice(0, 10)) : null;
  const diasFim = hasFimInsc ? formatDiasLegenda(row.dias_ate_fim_inscricao) : null;
  const hasProva = Boolean(row.data_prova);
  const dataProva = hasProva ? formatDate(String(row.data_prova).slice(0, 10)) : null;
  const diasProva = hasProva ? formatDiasLegenda(row.dias_ate_prova) : null;
  const vagas =
    row.numero_vagas != null && row.numero_vagas !== '' && Number.isFinite(Number(row.numero_vagas))
      ? String(row.numero_vagas)
      : null;
  const escRaw = (row.nivel_escolaridade || '').trim();
  const banca = (row.banca || '').trim() || '—';
  const linkEdital = (row.link_edital || '').trim();
  const orgInst = orgaoInstituicaoText(row);
  const localTxt = localEstadoMunicipioText(row);
  const cargoCurso = cargoCursoText(row);
  const isAgregador = String(row.fonte_tipo || '').toLowerCase() === 'agregador';

  return (
    <article className="concurso-card">
      <header className="concurso-card__head">
        <h3 className="concurso-card__title">{row.titulo || '—'}</h3>
        <div className="concurso-card__meta-line">
          <span className="concurso-card__tipo">{labelTipoSelecao(row.tipo_selecao)}</span>
          <span className="concurso-card__status" title="Status do certame">
            {labelStatus(row.status)}
          </span>
        </div>
        {isAgregador ? (
          <p className="concurso-card__aggregator" title="Resumo editorial; confirme no órgão emissor">
            Fonte agregadora
          </p>
        ) : null}
        {badges.length > 0 && (
          <ul className="concurso-card__badges" aria-label="Indicadores">
            {badges.map((b) => (
              <li key={b.id}>
                <span className={`concurso-badge concurso-badge--${b.variant}`}>{b.label}</span>
              </li>
            ))}
          </ul>
        )}
      </header>

      <dl className="concurso-card__dl">
        <div>
          <dt>Órgão / instituição</dt>
          <dd>{orgInst || mutedHint('Não identificado no resumo agregado')}</dd>
        </div>
        <div>
          <dt>Banca / fonte</dt>
          <dd>{banca}</dd>
        </div>
        <div>
          <dt>Cargo ou curso</dt>
          <dd>{cargoCurso || mutedHint('Não informado no resumo')}</dd>
        </div>
        <div>
          <dt>Local</dt>
          <dd>{localTxt || mutedHint('UF ou município não identificados no título')}</dd>
        </div>
        <div>
          <dt>Escolaridade</dt>
          <dd>{escRaw || mutedHint('Não especificada no resumo')}</dd>
        </div>
        {vagas != null && (
          <div>
            <dt>Vagas</dt>
            <dd>{vagas}</dd>
          </div>
        )}
        {salarioFmt && (
          <div>
            <dt>Salário</dt>
            <dd>{salarioFmt}</dd>
          </div>
        )}
        {taxa && (
          <div>
            <dt>Taxa de inscrição</dt>
            <dd>{taxa}</dd>
          </div>
        )}
        <div>
          <dt>Inscrição</dt>
          <dd>
            {fimInsc ? (
              <>
                Até {fimInsc}
                {diasFim ? <span className="concurso-card__dias"> · {diasFim}</span> : null}
              </>
            ) : (
              mutedHint('Não identificada no texto disponível')
            )}
          </dd>
        </div>
        <div>
          <dt>Prova</dt>
          <dd>
            {dataProva ? (
              <>
                {dataProva}
                {diasProva ? <span className="concurso-card__dias"> · {diasProva}</span> : null}
              </>
            ) : (
              mutedHint('Não identificada no texto disponível')
            )}
          </dd>
        </div>
      </dl>

      {Array.isArray(row.tags) && row.tags.length > 0 && (
        <div className="concurso-card__tags">
          <span className="concurso-card__tags-label">Tags</span>
          <span className="concurso-card__tags-val">{formatArray(row.tags, ' · ')}</span>
        </div>
      )}

      <footer className="concurso-card__actions">
        <ExternalActionButton
          item={row}
          actionType={EXTERNAL_ACTION_TYPES.CONCURSO_PRIMARY}
          label="Abrir"
          className="btn-primary concurso-card__btn"
        />
        {linkEdital ? (
          <ExternalActionButton
            item={row}
            actionType={EXTERNAL_ACTION_TYPES.CONCURSO_EDITAL}
            url={linkEdital}
            label="Edital"
            className="btn-secondary concurso-card__btn"
          />
        ) : null}
      </footer>
    </article>
  );
}
