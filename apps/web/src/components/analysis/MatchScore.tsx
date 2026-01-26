/**
 * MatchScore Component - 원형 프로그레스 바로 매치 점수와 등급 시각화
 */

import { motion } from 'framer-motion';
import { Trophy, TrendingUp } from 'lucide-react';

type MatchGrade = 'S' | 'A' | 'B' | 'C' | 'D';

interface MatchScoreProps {
  score: number; // 0-100
  grade: MatchGrade;
  similarity?: number; // 0-1
}

// 등급별 색상 매핑
const gradeColors: Record<MatchGrade, { primary: string; gradient: string; bg: string }> = {
  S: {
    primary: 'text-purple-400',
    gradient: 'from-purple-500 to-fuchsia-500',
    bg: 'bg-purple-500/10',
  },
  A: {
    primary: 'text-blue-400',
    gradient: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-500/10',
  },
  B: {
    primary: 'text-green-400',
    gradient: 'from-green-500 to-emerald-500',
    bg: 'bg-green-500/10',
  },
  C: {
    primary: 'text-yellow-400',
    gradient: 'from-yellow-500 to-orange-500',
    bg: 'bg-yellow-500/10',
  },
  D: {
    primary: 'text-red-400',
    gradient: 'from-red-500 to-rose-500',
    bg: 'bg-red-500/10',
  },
};

// 등급별 메시지
const gradeMessages: Record<MatchGrade, string> = {
  S: '완벽한 매칭! 즉시 지원 가능합니다.',
  A: '뛰어난 적합도! 강력히 추천합니다.',
  B: '좋은 매칭! 충분히 지원 가능합니다.',
  C: '보통 매칭. 일부 준비가 필요합니다.',
  D: '준비가 더 필요합니다. 로드맵을 확인하세요.',
};

export const MatchScore: React.FC<MatchScoreProps> = ({ score, grade, similarity }) => {
  const colors = gradeColors[grade];
  const circumference = 2 * Math.PI * 80; // 반지름 80의 원
  const dashOffset = circumference - (score / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-8 backdrop-blur-sm"
    >
      {/* Background Gradient Glow */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${colors.gradient} opacity-5 blur-3xl`}
      />

      <div className="relative z-10">
        <div className="flex flex-col items-center space-y-6 md:flex-row md:space-x-8 md:space-y-0">
          {/* Circular Progress */}
          <div className="relative flex-shrink-0">
            {/* SVG Circle - viewBox를 사용하여 완벽한 중앙 정렬 */}
            <svg
              className="h-48 w-48 -rotate-90 transform md:h-56 md:w-56"
              viewBox="0 0 200 200"
            >
              {/* Background Circle */}
              <circle
                cx="100"
                cy="100"
                r="80"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                className="text-slate-800"
              />
              {/* Progress Circle */}
              <motion.circle
                cx="100"
                cy="100"
                r="80"
                stroke="url(#gradient)"
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={circumference}
                animate={{ strokeDashoffset: dashOffset }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
              />
              {/* Gradient Definition */}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop
                    offset="0%"
                    className={grade === 'S' ? 'text-purple-500' :
                              grade === 'A' ? 'text-blue-500' :
                              grade === 'B' ? 'text-green-500' :
                              grade === 'C' ? 'text-yellow-500' : 'text-red-500'}
                    stopColor="currentColor"
                  />
                  <stop
                    offset="100%"
                    className={grade === 'S' ? 'text-fuchsia-500' :
                              grade === 'A' ? 'text-cyan-500' :
                              grade === 'B' ? 'text-emerald-500' :
                              grade === 'C' ? 'text-orange-500' : 'text-rose-500'}
                    stopColor="currentColor"
                  />
                </linearGradient>
              </defs>
            </svg>

            {/* Center Content - 완벽한 중앙 정렬 */}
            <div className="absolute left-0 top-0 flex h-full w-full flex-col items-center justify-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
                className={`text-6xl font-black leading-none ${colors.primary}`}
              >
                {grade}
              </motion.div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="mt-1 text-sm font-medium leading-none text-slate-400"
              >
                {score}점
              </motion.div>
            </div>
          </div>

          {/* Text Content */}
          <div className="flex-1 space-y-4 text-center md:text-left">
            <div>
              <h3 className="mb-2 flex items-center justify-center gap-2 text-2xl font-bold text-slate-100 md:justify-start md:text-3xl">
                <Trophy className={`h-7 w-7 ${colors.primary}`} />
                매칭 점수
              </h3>
              <p className="text-base text-slate-400 md:text-lg">{gradeMessages[grade]}</p>
            </div>

            {/* Similarity Score */}
            {similarity !== undefined && (
              <div className={`inline-flex items-center gap-2 rounded-xl ${colors.bg} px-4 py-2`}>
                <TrendingUp className={`h-5 w-5 ${colors.primary}`} />
                <span className="text-sm font-medium text-slate-300">
                  유사도: {(similarity * 100).toFixed(1)}%
                </span>
              </div>
            )}

            {/* Grade Description */}
            <div className="rounded-xl border border-slate-800/50 bg-slate-900/50 p-4">
              <div className="space-y-2 text-sm text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">전체 점수</span>
                  <span className={`font-semibold ${colors.primary}`}>{score}/100</span>
                </div>
                {similarity !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">코사인 유사도</span>
                    <span className="font-semibold text-slate-300">
                      {similarity.toFixed(4)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MatchScore;
