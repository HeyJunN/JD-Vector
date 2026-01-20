/**
 * RoadmapPage - 맞춤형 학습 로드맵 페이지
 *
 * 백엔드에서 생성된 로드맵을 시각화하고 학습 진척도를 관리
 */

import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Loader2,
  ArrowLeft,
  Target,
  TrendingUp,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { roadmapService } from '../services/roadmapService';
import { ProgressTracker } from '../components/roadmap/ProgressTracker';
import { RoadmapWeekCard } from '../components/roadmap/RoadmapWeekCard';
import type { RoadmapData, RoadmapWeek } from '../types/roadmap.types';

export const RoadmapPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // URL에서 파라미터 추출
  const resumeId = searchParams.get('resume_id');
  const jdId = searchParams.get('jd_id');
  const targetWeeks = searchParams.get('target_weeks');

  // 상태 관리
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [roadmapData, setRoadmapData] = useState<RoadmapData | null>(null);
  const [weeklyPlan, setWeeklyPlan] = useState<RoadmapWeek[]>([]);
  const [showConfetti, setShowConfetti] = useState(false);

  // 로드맵 데이터 불러오기
  useEffect(() => {
    const fetchRoadmap = async () => {
      if (!resumeId || !jdId) {
        setError('이력서 ID와 JD ID가 필요합니다.');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const response = await roadmapService.generateRoadmap({
          resume_id: resumeId,
          jd_id: jdId,
          target_weeks: targetWeeks ? parseInt(targetWeeks) : 8,
        });

        if (!response.success || !response.data) {
          throw new Error(response.message || '로드맵 생성에 실패했습니다.');
        }

        setRoadmapData(response.data);
        setWeeklyPlan(response.data.weekly_plan);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRoadmap();
  }, [resumeId, jdId, targetWeeks]);

  // 태스크 토글 핸들러
  const handleTaskToggle = (weekNumber: number, taskIndex: number) => {
    setWeeklyPlan((prev) =>
      prev.map((week) =>
        week.week_number === weekNumber
          ? {
              ...week,
              tasks: week.tasks.map((task, index) =>
                index === taskIndex
                  ? { ...task, completed: !task.completed }
                  : task
              ),
            }
          : week
      )
    );

    // 모든 태스크가 완료되었는지 확인
    const updatedPlan = weeklyPlan.map((week) =>
      week.week_number === weekNumber
        ? {
            ...week,
            tasks: week.tasks.map((task, index) =>
              index === taskIndex
                ? { ...task, completed: !task.completed }
                : task
            ),
          }
        : week
    );

    const allCompleted = updatedPlan.every((week) =>
      week.tasks.every((task) => task.completed)
    );

    if (allCompleted) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 5000);
    }
  };

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            맞춤형 학습 로드맵을 생성하고 있습니다...
          </p>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
            AI가 당신의 스킬 갭을 분석하여 최적의 커리큘럼을 만들고 있어요
          </p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error || !roadmapData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4 dark:bg-gray-900">
        <div className="max-w-md rounded-lg border border-red-200 bg-white p-6 text-center shadow-sm dark:border-red-800 dark:bg-gray-800">
          <AlertCircle className="mx-auto h-12 w-12 text-red-600 dark:text-red-400" />
          <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
            로드맵 생성 실패
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {error || '알 수 없는 오류가 발생했습니다.'}
          </p>
          <button
            onClick={() => navigate(-1)}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            <ArrowLeft size={16} />
            돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 축하 애니메이션 */}
      {showConfetti && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="rounded-2xl bg-white p-8 text-center shadow-2xl dark:bg-gray-800">
            <Sparkles className="mx-auto h-16 w-16 text-yellow-500" />
            <h2 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
              축하합니다! 🎉
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              모든 학습 태스크를 완료했습니다!
            </p>
            <button
              onClick={() => setShowConfetti(false)}
              className="mt-6 rounded-lg bg-blue-600 px-6 py-2 font-medium text-white transition-colors hover:bg-blue-700"
            >
              확인
            </button>
          </div>
        </div>
      )}

      {/* 헤더 */}
      <div className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 flex items-center gap-2 text-sm text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            <ArrowLeft size={16} />
            분석 결과로 돌아가기
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                맞춤형 학습 로드맵
              </h1>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {roadmapData.total_weeks}주 커리큘럼 | 현재 등급:{' '}
                <span className="font-semibold text-blue-600 dark:text-blue-400">
                  {roadmapData.match_grade}
                </span>{' '}
                → 목표 등급:{' '}
                <span className="font-semibold text-green-600 dark:text-green-400">
                  {roadmapData.target_grade}
                </span>
              </p>
            </div>
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
              <Target size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          {/* 좌측 사이드바 - 진행률 및 요약 */}
          <div className="lg:col-span-4">
            <div className="sticky top-8 space-y-6">
              {/* 로드맵 요약 */}
              <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <h2 className="font-semibold text-gray-900 dark:text-white">
                    학습 전략
                  </h2>
                </div>
                <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                  {roadmapData.summary}
                </p>

                {/* 핵심 개선 영역 */}
                {roadmapData.key_improvement_areas.length > 0 && (
                  <div className="mt-4">
                    <h3 className="mb-2 text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
                      핵심 개선 영역
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {roadmapData.key_improvement_areas.map((area, index) => (
                        <span
                          key={index}
                          className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-700 dark:bg-red-900 dark:text-red-300"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 진행률 트래커 */}
              <ProgressTracker weeks={weeklyPlan} />
            </div>
          </div>

          {/* 우측 메인 - 주차별 로드맵 */}
          <div className="lg:col-span-8">
            <div className="space-y-6">
              {weeklyPlan.map((week) => (
                <RoadmapWeekCard
                  key={week.week_number}
                  week={week}
                  onTaskToggle={handleTaskToggle}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoadmapPage;
