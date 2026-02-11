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
  CheckCircle,
  Star,
  Briefcase,
  Zap,
  Code,
  Tag,
} from 'lucide-react';
import { roadmapService } from '../services/roadmapService';
import { ProgressTracker } from '../components/roadmap/ProgressTracker';
import { RoadmapWeekCard } from '../components/roadmap/RoadmapWeekCard';
import { getKoreanLabel } from '../utils/labelMapper';
import type { RoadmapData, RoadmapWeek } from '../types/roadmap.types';

// 카테고리별 배지 스타일 및 아이콘 매핑 (다크 모드 최적화)
const getCategoryStyle = (category: string) => {
  const normalizedCategory = category.toLowerCase().trim();

  // requirements, required → 필수 역량 (Blue)
  if (normalizedCategory.includes('requirement') || normalizedCategory.includes('required')) {
    return {
      icon: CheckCircle,
      bgClass: 'bg-blue-500/20 ring-1 ring-blue-500/30',
      textClass: 'text-blue-400',
      iconClass: 'text-blue-400',
    };
  }

  // preferred, preference → 우대 사항 (Purple)
  if (normalizedCategory.includes('prefer')) {
    return {
      icon: Star,
      bgClass: 'bg-purple-500/20 ring-1 ring-purple-500/30',
      textClass: 'text-purple-400',
      iconClass: 'text-purple-400',
    };
  }

  // experience → 경력/경험 (Emerald)
  if (normalizedCategory.includes('experience')) {
    return {
      icon: Briefcase,
      bgClass: 'bg-emerald-500/20 ring-1 ring-emerald-500/30',
      textClass: 'text-emerald-400',
      iconClass: 'text-emerald-400',
    };
  }

  // potential → 성장 잠재력 (Amber)
  if (normalizedCategory.includes('potential')) {
    return {
      icon: Zap,
      bgClass: 'bg-amber-500/20 ring-1 ring-amber-500/30',
      textClass: 'text-amber-400',
      iconClass: 'text-amber-400',
    };
  }

  // technical → 기술 스택 (Cyan)
  if (normalizedCategory.includes('technical') || normalizedCategory.includes('tech')) {
    return {
      icon: Code,
      bgClass: 'bg-cyan-500/20 ring-1 ring-cyan-500/30',
      textClass: 'text-cyan-400',
      iconClass: 'text-cyan-400',
    };
  }

  // 기본 (Slate)
  return {
    icon: Tag,
    bgClass: 'bg-slate-700/50 ring-1 ring-slate-600/30',
    textClass: 'text-slate-300',
    iconClass: 'text-slate-400',
  };
};

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
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-blue-400" />
          <p className="mt-4 text-lg text-slate-300">
            맞춤형 학습 로드맵을 생성하고 있습니다...
          </p>
          <p className="mt-2 text-sm text-slate-500">
            AI가 당신의 스킬 갭을 분석하여 최적의 커리큘럼을 만들고 있어요
          </p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error || !roadmapData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
        <div className="max-w-md rounded-2xl border border-red-500/30 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-6 text-center shadow-lg backdrop-blur-sm">
          <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
          <h2 className="mt-4 text-xl font-semibold text-slate-100">
            로드맵 생성 실패
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            {error || '알 수 없는 오류가 발생했습니다.'}
          </p>
          <button
            onClick={() => navigate(-1)}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/20"
          >
            <ArrowLeft size={16} />
            돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* 축하 애니메이션 */}
      {showConfetti && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
          <div className="rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/95 to-slate-950/95 p-8 text-center shadow-2xl backdrop-blur-sm">
            <Sparkles className="mx-auto h-16 w-16 text-yellow-400" />
            <h2 className="mt-4 text-2xl font-bold text-slate-100">
              축하합니다! 🎉
            </h2>
            <p className="mt-2 text-slate-400">
              모든 학습 태스크를 완료했습니다!
            </p>
            <button
              onClick={() => setShowConfetti(false)}
              className="mt-6 rounded-lg bg-blue-600 px-6 py-2 font-medium text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/20"
            >
              확인
            </button>
          </div>
        </div>
      )}

      {/* 헤더 */}
      <div className="border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 flex items-center gap-2 text-sm text-slate-400 transition-colors hover:text-slate-100"
          >
            <ArrowLeft size={16} />
            분석 결과로 돌아가기
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-100">
                맞춤형 학습 로드맵
              </h1>
              <p className="mt-2 text-sm text-slate-400">
                {roadmapData.total_weeks}주 커리큘럼 | 현재 등급:{' '}
                <span className="font-semibold text-blue-400">
                  {roadmapData.match_grade}
                </span>{' '}
                → 목표 등급:{' '}
                <span className="font-semibold text-green-400">
                  {roadmapData.target_grade}
                </span>
              </p>
            </div>
            <div className="flex items-center gap-2 text-blue-400">
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
              <div className="rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-6 shadow-sm backdrop-blur-sm">
                <div className="mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-400" />
                  <h2 className="font-semibold text-slate-100">
                    학습 전략
                  </h2>
                </div>
                <p className="text-sm leading-relaxed text-slate-300">
                  {roadmapData.summary}
                </p>

                {/* 핵심 개선 영역 */}
                {roadmapData.key_improvement_areas.length > 0 && (
                  <div className="mt-4">
                    <h3 className="mb-2 text-xs font-semibold uppercase text-slate-400">
                      핵심 개선 영역
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {roadmapData.key_improvement_areas.map((area, index) => {
                        const koreanLabel = getKoreanLabel(area);
                        const style = getCategoryStyle(area);
                        const Icon = style.icon;

                        return (
                          <span
                            key={index}
                            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium ${style.bgClass} ${style.textClass}`}
                          >
                            <Icon size={14} className={style.iconClass} />
                            {koreanLabel}
                          </span>
                        );
                      })}
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
