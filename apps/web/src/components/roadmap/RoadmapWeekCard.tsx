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
  beginner: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  intermediate: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  advanced: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
};

// 우선순위별 색상
const PRIORITY_COLORS = {
  high: 'text-red-600 dark:text-red-400',
  medium: 'text-yellow-600 dark:text-yellow-400',
  low: 'text-gray-600 dark:text-gray-400',
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
      className={`rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800 ${className}`}
    >
      {/* 헤더 */}
      <div className="border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50 p-6 dark:border-gray-700 dark:from-blue-900/20 dark:to-purple-900/20">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold text-white">
                Week {week.week_number}
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {week.duration}
              </span>
              {isCompleted && (
                <div className="flex items-center gap-1 rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                  <CheckCircle2 size={14} />
                  <span>완료</span>
                </div>
              )}
            </div>
            <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">
              {week.title}
            </h3>
            <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
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
          <div className="mb-1 flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>진행률</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isCompleted ? 'bg-green-500' : 'bg-blue-500'
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* 태스크 체크리스트 */}
      <div className="p-6">
        <h4 className="mb-4 flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <CheckCircle2 size={18} />
          학습 태스크
        </h4>
        <div className="space-y-3">
          {week.tasks.map((task, index) => (
            <label
              key={index}
              className="flex cursor-pointer items-start gap-3 rounded-lg p-3 transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50"
            >
              <div className="flex-shrink-0 pt-0.5">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => onTaskToggle(week.week_number, index)}
                  className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600"
                />
              </div>
              <div className="flex-1">
                <p
                  className={`text-sm ${
                    task.completed
                      ? 'text-gray-500 line-through dark:text-gray-400'
                      : 'text-gray-700 dark:text-gray-300'
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
        <div className="border-t border-gray-200 bg-gray-50 p-6 dark:border-gray-700 dark:bg-gray-900/50">
          <h4 className="mb-4 flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
            <Award size={18} />
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
      className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-3 transition-all hover:border-blue-300 hover:shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-600"
    >
      <div className="flex-shrink-0 pt-1">
        <PlatformIcon keyword={resource.platform} className="text-gray-600 dark:text-gray-400" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="mb-1 flex items-center gap-2">
          <h5 className="truncate font-medium text-gray-900 dark:text-white">
            {resource.title}
          </h5>
          <ExternalLink size={14} className="flex-shrink-0 text-gray-400" />
        </div>
        {resource.description && (
          <p className="mb-2 text-xs text-gray-600 dark:text-gray-400">
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
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {resource.platform}
          </span>
          {resource.estimated_hours && (
            <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
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
