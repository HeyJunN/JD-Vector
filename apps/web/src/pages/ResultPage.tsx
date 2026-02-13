/**
 * ResultPage - 분석 결과 종합 대시보드
 */

import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { Loader2, ArrowRight, TrendingUp, BarChart3 } from 'lucide-react';

import { MatchScore } from '@/components/analysis/MatchScore';
import { CompetencyChart } from '@/components/analysis/CompetencyChart';
import { FeedbackSection } from '@/components/analysis/FeedbackSection';
import type { MatchResponse } from '@/services/analysisService';
import { StatCard } from '@/components/ui/StatCard';
import { normalizeScore } from '@/utils/scoreNormalization';

interface ResultPageState {
  analysisResult: MatchResponse['data'];
}

export const ResultPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as ResultPageState | null;

  const [isLoading, setIsLoading] = useState(false);

  // 분석 결과 데이터
  const analysisData = state?.analysisResult;

  // 데이터 유효성 검증
  useEffect(() => {
    if (!state || !analysisData) {
      toast.error('분석 결과를 불러올 수 없습니다.');
      navigate('/upload', { replace: true });
    }
  }, [state, analysisData, navigate]);

  if (!analysisData) {
    return null;
  }

  // section_scores를 CompetencyChart 형식으로 변환
  // JD 목표치는 고정된 합격 기준선 (등급과 무관하게 일정)
  const competencyData = analysisData.section_scores?.map((section) => ({
    category: section.section_type || 'Unknown',
    userScore: normalizeScore(section.score),
    jdRequirement: 80,
  })).filter(item => item.category !== 'Unknown') || [];

  // 로드맵 페이지로 이동
  const handleViewRoadmap = () => {
    setIsLoading(true);
    navigate(
      `/roadmap?resume_id=${analysisData.resume_document_id}&jd_id=${analysisData.jd_document_id}&target_weeks=8`,
      {
        state: {
          analysisResult: analysisData,
        },
      }
    );
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-500/10 p-2">
                <BarChart3 className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
                  분석 결과
                </h1>
                <p className="mt-1 text-sm text-slate-400">
                  AI가 분석한 당신의 커리어 적합도를 확인하세요
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Match Score Section */}
          <MatchScore
            score={analysisData.match_score}
            grade={analysisData.match_grade}
            similarity={analysisData.overall_similarity}
          />

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            <StatCard
              label="전체 유사도"
              value={`${(analysisData.overall_similarity * 100).toFixed(1)}%`}
              icon={<TrendingUp className="h-5 w-5" />}
              color="blue"
            />
            <StatCard
              label="매칭 청크 수"
              value={analysisData.chunk_match_count.toString()}
              subtitle="개의 섹션 매칭"
              icon={<BarChart3 className="h-5 w-5" />}
              color="green"
            />
            <StatCard
              label="유사 기술 보너스"
              value={`+${analysisData.similar_tech_bonus.toFixed(1)}점`}
              subtitle={`${analysisData.similar_tech_matches?.length || 0}개 매칭`}
              icon={<TrendingUp className="h-5 w-5" />}
              color="purple"
            />
            <StatCard
              label="분석된 섹션"
              value={analysisData.section_scores?.length.toString() || '0'}
              subtitle="개의 역량 영역"
              icon={<BarChart3 className="h-5 w-5" />}
              color="orange"
            />
          </motion.div>

          {/* Competency Radar Chart */}
          {competencyData.length > 0 && (
            <CompetencyChart data={competencyData} />
          )}

          {/* Feedback Section */}
          {analysisData.feedback && (
            <FeedbackSection
              summary={analysisData.feedback.summary}
              strengths={analysisData.feedback.strengths}
              weaknesses={analysisData.feedback.improvements}
              potential={analysisData.feedback.potential}
              actionItems={analysisData.feedback.action_items}
            />
          )}

          {/* Similar Tech Matches */}
          {analysisData.similar_tech_matches && analysisData.similar_tech_matches.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-6 backdrop-blur-sm"
            >
              <h3 className="mb-4 text-xl font-bold text-slate-100">
                유사 기술 스택 매칭
              </h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {analysisData.similar_tech_matches.map((match, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-slate-800/50 bg-slate-900/50 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-xs font-medium text-slate-400">
                        {match.relationship}
                      </span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">JD 요구:</span>
                        <span className="text-sm font-semibold text-blue-400">
                          {match.jd_required}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">보유:</span>
                        <span className="text-sm font-semibold text-green-400">
                          {match.resume_has}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* CTA Button - Navigate to Roadmap */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="flex justify-center pb-8"
          >
            <button
              onClick={handleViewRoadmap}
              disabled={isLoading}
              className="group relative inline-flex items-center space-x-3 rounded-xl border border-slate-200 bg-slate-50 px-8 py-4 text-base font-semibold text-slate-950 shadow-lg shadow-slate-50/10 transition-all duration-200 hover:scale-[1.02] hover:border-white hover:bg-white hover:shadow-xl hover:shadow-slate-50/20 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>로드맵 생성 중...</span>
                </>
              ) : (
                <>
                  <TrendingUp className="h-5 w-5" />
                  <span>맞춤형 학습 로드맵 확인하기</span>
                  <ArrowRight className="h-5 w-5 transition-transform duration-200 group-hover:translate-x-1" />
                </>
              )}

              {/* Glow Effect */}
              <div className="absolute inset-0 -z-10 rounded-xl bg-slate-50/20 opacity-0 blur-xl transition-opacity duration-200 group-hover:opacity-100" />
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Sub-components
// ============================================================================


export default ResultPage;
