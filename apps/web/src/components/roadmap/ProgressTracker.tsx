/**
 * ProgressTracker Component - 학습 진행률 추적
 *
 * 전체 및 주차별 태스크 완료율을 시각화
 */

import { CheckCircle2, TrendingUp } from 'lucide-react';
import type { RoadmapWeek, ProgressStats, WeekProgressStats } from '../../types/roadmap.types';

interface ProgressTrackerProps {
  weeks: RoadmapWeek[];
  className?: string;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  weeks,
  className = ''
}) => {
  // 전체 진행률 계산
  const calculateOverallProgress = (): ProgressStats => {
    const totalTasks = weeks.reduce(
      (sum, week) => sum + week.tasks.length,
      0
    );
    const completedTasks = weeks.reduce(
      (sum, week) => sum + week.tasks.filter((t) => t.completed).length,
      0
    );

    return {
      totalTasks,
      completedTasks,
      percentage: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0,
    };
  };

  // 주차별 진행률 계산
  const calculateWeekProgress = (week: RoadmapWeek): WeekProgressStats => {
    const totalTasks = week.tasks.length;
    const completedTasks = week.tasks.filter((t) => t.completed).length;

    return {
      week_number: week.week_number,
      totalTasks,
      completedTasks,
      percentage: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0,
    };
  };

  const overallProgress = calculateOverallProgress();
  const weekProgress = weeks.map(calculateWeekProgress);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 전체 진행률 */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              전체 학습 진행률
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {overallProgress.completedTasks} / {overallProgress.totalTasks} 태스크 완료
            </p>
          </div>
          <div className="flex items-center gap-2 text-2xl font-bold text-blue-600 dark:text-blue-400">
            <TrendingUp className="h-6 w-6" />
            <span>{Math.round(overallProgress.percentage)}%</span>
          </div>
        </div>

        {/* 전체 진행률 바 */}
        <div className="relative h-4 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
            style={{ width: `${overallProgress.percentage}%` }}
          >
            <div className="absolute inset-0 animate-pulse bg-white opacity-20"></div>
          </div>
        </div>

        {/* 완료 메시지 */}
        {overallProgress.percentage === 100 && (
          <div className="mt-4 rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
            <div className="flex items-center gap-2 text-green-700 dark:text-green-400">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-semibold">축하합니다! 모든 태스크를 완료했습니다! 🎉</span>
            </div>
          </div>
        )}
      </div>

      {/* 주차별 진행률 */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <h4 className="mb-4 font-semibold text-gray-900 dark:text-white">
          주차별 진행률
        </h4>
        <div className="space-y-3">
          {weekProgress.map((progress) => (
            <div key={progress.week_number}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Week {progress.week_number}
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {progress.completedTasks}/{progress.totalTasks}
                </span>
              </div>
              <div className="relative h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    progress.percentage === 100
                      ? 'bg-green-500'
                      : 'bg-blue-500'
                  }`}
                  style={{ width: `${progress.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-center shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {weeks.length}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">주차</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-center shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {overallProgress.completedTasks}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">완료</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-center shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {overallProgress.totalTasks - overallProgress.completedTasks}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">남은 태스크</div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
