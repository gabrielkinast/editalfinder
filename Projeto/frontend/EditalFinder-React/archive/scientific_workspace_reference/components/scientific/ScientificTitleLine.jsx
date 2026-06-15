import { displayScientificTitle } from '../../utils/scientific/cleanScientificTitle';

export default function ScientificTitleLine({
  item,
  className = 'scientific-feed-title scientific-title-clamp',
  as: Tag = 'h3',
}) {
  const { title, titleFull, badge } = displayScientificTitle(item);

  return (
    <div className="scientific-title-line">
      {badge && <span className="scientific-continuation-badge">{badge}</span>}
      <Tag className={className} title={titleFull}>
        {title}
      </Tag>
    </div>
  );
}
