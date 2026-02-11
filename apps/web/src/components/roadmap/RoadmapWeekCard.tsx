/**
 * RoadmapWeekCard Component - 주차별 학습 계획 카드
 *
 * 주차별 타이틀, 설명, 태스크 체크리스트, 리소스 표시
 */

import { Check, CheckCircle2, Circle, ExternalLink, Clock, Award } from 'lucide-react';
import { TechIconGroup, PlatformIcon } from '../common/TechIcon';
import type { RoadmapWeek, LearningResource } from '../../types/roadmap.types';

interface RoadmapWeekCardProps {
  week: RoadmapWeek;
  onTaskToggle: (weekNumber: number, taskIndex: number) => void;
  className?: string;
}

// 난이도별 배지 색상
const DIFFICULTY_COLORS = {
  beginner: 'bg-green-500/20 text-green-400 ring-1 ring-green-500/30',
  intermediate: 'bg-yellow-500/20 text-yellow-400 ring-1 ring-yellow-500/30',
  advanced: 'bg-red-500/20 text-red-400 ring-1 ring-red-500/30',
};

// 우선순위별 색상
const PRIORITY_COLORS = {
  high: 'text-red-400',
  medium: 'text-yellow-400',
  low: 'text-slate-500',
};

export const RoadmapWeekCard: React.FC<RoadmapWeekCardProps> = ({
  week,
  onTaskToggle,
  className = ''
}) => {
  const completedTasks = week.tasks.filter((t) => t.completed).length;
  const totalTasks = week.tasks.length;
  const progressPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  const isCompleted = completedTasks === totalTasks && totalTasks > 0;

  return (
    <div
      className={`rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 shadow-sm backdrop-blur-sm transition-all hover:border-slate-700/50 hover:shadow-lg hover:shadow-slate-900/20 ${className}`}
    >
      {/* 헤더 */}
      <div className="border-b border-slate-800/50 bg-gradient-to-r from-blue-900/20 to-purple-900/20 p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded-full bg-blue-500 px-3 py-1 text-xs font-semibold text-white shadow-lg shadow-blue-500/20">
                Week {week.week_number}
              </span>
              <span className="text-sm text-slate-400">
                {week.duration}
              </span>
              {isCompleted && (
                <div className="flex items-center gap-1 rounded-full bg-green-500/20 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-green-500/30">
                  <CheckCircle2 size={14} />
                  <span>완료</span>
                </div>
              )}
            </div>
            <h3 className="mb-2 text-xl font-bold text-slate-100">
              {week.title}
            </h3>
            <p className="text-sm leading-relaxed text-slate-300">
              {week.description}
            </p>
          </div>
        </div>

        {/* 키워드 아이콘 */}
        {week.keywords.length > 0 && (
          <div className="mt-4">
            <TechIconGroup keywords={week.keywords} />
          </div>
        )}

        {/* 진행률 바 */}
        <div className="mt-4">
          <div className="mb-1 flex items-center justify-between text-xs text-slate-400">
            <span>진행률</span>
            <span className="font-semibold">{Math.round(progressPercentage)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-800/50">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isCompleted
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg shadow-green-500/20'
                  : 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg shadow-blue-500/20'
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* 태스크 체크리스트 */}
      <div className="p-6">
        <h4 className="mb-4 flex items-center gap-2 font-semibold text-slate-100">
          <CheckCircle2 size={18} className="text-blue-400" />
          학습 태스크
        </h4>
        <div className="space-y-3">
          {week.tasks.map((task, index) => (
            <label
              key={index}
              className="flex cursor-pointer items-start gap-3 rounded-lg p-3 transition-colors hover:bg-slate-800/50"
            >
              <div className="flex-shrink-0 pt-0.5">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => onTaskToggle(week.week_number, index)}
                  className="h-5 w-5 rounded border-slate-600 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-slate-900"
                />
              </div>
              <div className="flex-1">
                <p
                  className={`text-sm ${
                    task.completed
                      ? 'text-slate-500 line-through'
                      : 'text-slate-300'
                  }`}
                >
                  {task.task}
                </p>
                {task.priority && (
                  <span
                    className={`mt-1 inline-block text-xs font-medium ${
                      PRIORITY_COLORS[task.priority]
                    }`}
                  >
                    {task.priority === 'high'
                      ? '높은 우선순위'
                      : task.priority === 'medium'
                      ? '보통'
                      : '낮은 우선순위'}
                  </span>
                )}
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* 학습 리소스 */}
      {week.resources.length > 0 && (
        <div className="border-t border-slate-800/50 bg-slate-900/30 p-6">
          <h4 className="mb-4 flex items-center gap-2 font-semibold text-slate-100">
            <Award size={18} className="text-purple-400" />
            추천 학습 리소스
          </h4>
          <div className="space-y-3">
            {week.resources.map((resource, index) => (
              <ResourceItem key={index} resource={resource} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// 리소스 아이템 컴포넌트
const ResourceItem: React.FC<{ resource: LearningResource }> = ({ resource }) => {
  return (
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
          <h5 className="truncate font-medium text-slate-100">
            {resource.title}
          </h5>
          <ExternalLink size={14} className="flex-shrink-0 text-slate-500" />
        </div>
        {resource.description && (
          <p className="mb-2 text-xs text-slate-400">
            {resource.description}
          </p>
        )}
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              DIFFICULTY_COLORS[resource.difficulty]
            }`}
          >
            {resource.difficulty === 'beginner'
              ? '초급'
              : resource.difficulty === 'intermediate'
              ? '중급'
              : '고급'}
          </span>
          <span className="text-xs text-slate-500">
            {resource.platform}
          </span>
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
};

export default RoadmapWeekCard;
