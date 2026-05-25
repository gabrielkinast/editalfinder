import { buildGlobalStudyProgressSummary } from '../../utils/scientific/buildStudyProgressSummary';

export default function ScientificStudyProgressGlobal({ blocks = [], progressMap = {}, goalRoutes = [] }) {
  const summary = buildGlobalStudyProgressSummary(blocks, progressMap, goalRoutes);

  if (!summary.total) return null;

  return (
    <div className="scientific-progress-global" aria-labelledby="scientific-progress-global-title">
      <h3 id="scientific-progress-global-title" className="scientific-progress-global-title">
        Seu progresso
      </h3>
      <ul className="scientific-progress-global-list">
        <li>
          <span className="scientific-progress-global-count">{summary.a_estudar}</span>
          <span>tópicos a estudar</span>
        </li>
        <li>
          <span className="scientific-progress-global-count scientific-progress-global-count--studying">
            {summary.estudando}
          </span>
          <span>estudando</span>
        </li>
        <li>
          <span className="scientific-progress-global-count scientific-progress-global-count--done">
            {summary.dominado}
          </span>
          <span>dominados</span>
        </li>
        {summary.projectsInProgress > 0 && (
          <li>
            <span className="scientific-progress-global-count scientific-progress-global-count--studying">
              {summary.projectsInProgress}
            </span>
            <span>projetos em andamento</span>
          </li>
        )}
      </ul>
    </div>
  );
}
