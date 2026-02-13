import { ExternalLink, Clock } from 'lucide-react';
import { PlatformIcon } from '../common/TechIcon';
import type { LearningResource } from '../../types/roadmap.types';

const DIFFICULTY_COLORS = {
  beginner: 'bg-green-500/20 text-green-400 ring-1 ring-green-500/30',
  intermediate: 'bg-yellow-500/20 text-yellow-400 ring-1 ring-yellow-500/30',
  advanced: 'bg-red-500/20 text-red-400 ring-1 ring-red-500/30',
};

const DIFFICULTY_LABELS = {
  beginner: '초급',
  intermediate: '중급',
  advanced: '고급',
} as const;

interface RoadmapResourceItemProps {
  resource: LearningResource;
}

export const RoadmapResourceItem: React.FC<RoadmapResourceItemProps> = ({ resource }) => (
  <a
    href={resource.url}
    target="_blank"
    rel="noopener noreferrer"
    className="flex items-start gap-3 rounded-lg border border-slate-800/50 bg-slate-900/50 p-3 backdrop-blur-sm transition-all hover:border-blue-500/50 hover:bg-slate-800/50 hover:shadow-lg hover:shadow-blue-500/10"
  >
    <div className="flex-shrink-0 pt-1">
      <PlatformIcon keyword={resource.platform} className="text-slate-400" />
    </div>
    <div className="flex-1 min-w-0">
      <div className="mb-1 flex items-center gap-2">
        <h5 className="truncate font-medium text-slate-100">{resource.title}</h5>
        <ExternalLink size={14} className="flex-shrink-0 text-slate-500" />
      </div>
      {resource.description && (
        <p className="mb-2 text-xs text-slate-400">{resource.description}</p>
      )}
      <div className="flex items-center gap-2">
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${DIFFICULTY_COLORS[resource.difficulty]}`}
        >
          {DIFFICULTY_LABELS[resource.difficulty]}
        </span>
        <span className="text-xs text-slate-500">{resource.platform}</span>
        {resource.estimated_hours && (
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <Clock size={12} />
            {resource.estimated_hours}시간
          </span>
        )}
      </div>
    </div>
  </a>
);

export default RoadmapResourceItem;
